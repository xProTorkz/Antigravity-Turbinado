#!/usr/bin/env python3
"""
Chrome Live Extractor & Auditor (Sentinela SRE / Antigravity 2.0)
Extrai DOM, sessões e executa auditoria diretamente de abas ativas no Google Chrome do macOS
sem abrir novas janelas, sem concorrência de SingletonLock e sem roubar foco da tela.
Caso a aba não esteja aberta, executa fallback automático via Shadow Copy efêmera em /tmp.
"""

import sys
import os
import json
import time
import argparse
import subprocess
import shutil
from pathlib import Path

CHROME_USER_DATA_DIR = Path.home() / "Library/Application Support/Google/Chrome"
CHROME_APP_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

SENTINELA_AUDIT_JS = """(() => {
  const rel = {
    url: window.location.href,
    title: document.title,
    timestamp: new Date().toISOString(),
    senhasDesmascaradas: 0,
    travasCssRemovidas: 0,
    camposDesbloqueados: 0,
    overlaysRemovidos: 0,
    valoresCacheColetados: [],
    metadadosAriaColetados: [],
    inputs: [],
    botoes: [],
    html: document.documentElement.outerHTML
  };

  // 1. Desmascarar senhas
  document.querySelectorAll('input[type="password"]').forEach((i) => {
    i.type = 'text';
    i.setAttribute('data-sentinela-unmasked', 'true');
    i.style.border = '2px dashed #f59e0b';
    rel.senhasDesmascaradas++;
  });

  // 2. Remover travas CSS visuais
  document.querySelectorAll('*').forEach((el) => {
    const s = window.getComputedStyle(el);
    let mod = false;
    if (s.filter && s.filter !== 'none') { el.style.filter = 'none'; mod = true; }
    if (s.webkitTextSecurity && s.webkitTextSecurity !== 'none') { el.style.webkitTextSecurity = 'none'; mod = true; }
    if (s.textSecurity && s.textSecurity !== 'none') { el.style.textSecurity = 'none'; mod = true; }
    if (s.userSelect === 'none') { el.style.userSelect = 'text'; mod = true; }
    if (mod) rel.travasCssRemovidas++;
  });

  // 3. Destravar disabled e readonly
  document.querySelectorAll('input, select, textarea, button').forEach((el) => {
    let d = false;
    if (el.hasAttribute('disabled')) { el.removeAttribute('disabled'); d = true; }
    if (el.hasAttribute('readonly')) { el.removeAttribute('readonly'); d = true; }
    if (d) rel.camposDesbloqueados++;
  });

  // 4. Neutralizar overlays vazios
  document.querySelectorAll('div, section, span, aside').forEach((el) => {
    const s = window.getComputedStyle(el);
    const isFixedOrAbsolute = s.position === 'fixed' || s.position === 'absolute';
    const occupiesScreen = el.offsetWidth >= window.innerWidth * 0.8 && el.offsetHeight >= window.innerHeight * 0.8;
    if (isFixedOrAbsolute && occupiesScreen) {
      if (el.innerText.trim().length === 0) {
        el.remove();
        rel.overlaysRemovidos++;
      } else {
        el.style.pointerEvents = 'none';
        rel.overlaysRemovidos++;
      }
    }
  });

  // 5. Coleta de inputs e botões
  document.querySelectorAll('input, select, textarea').forEach((el) => {
    const id = el.id || el.name || el.getAttribute('placeholder') || 'anônimo';
    const val = el.value || el.getAttribute('value') || el.innerText?.trim();
    if (val) {
      rel.valoresCacheColetados.push({
        elemento: el.tagName.toLowerCase(),
        identificador: id,
        tipo: el.type || 'text',
        valorReal: val
      });
    }
    rel.inputs.push({
      id: el.id,
      name: el.name,
      type: el.type,
      placeholder: el.placeholder,
      value: el.value
    });
  });

  document.querySelectorAll('button').forEach((b) => {
    const txt = b.innerText.trim();
    if (txt) rel.botoes.push(txt);
  });

  // 6. Atributos de acessibilidade
  document.querySelectorAll('[aria-label], [aria-description], [title], [alt]').forEach((el) => {
    const txt = el.getAttribute('aria-label') || el.getAttribute('aria-description') || el.getAttribute('title') || el.getAttribute('alt');
    if (txt) {
      rel.metadadosAriaColetados.push({
        tag: el.tagName.toLowerCase(),
        identificador: el.id || el.className || 'sem-id',
        atributo: el.hasAttribute('aria-label') ? 'aria-label' : (el.hasAttribute('title') ? 'title' : 'outros'),
        textoOculto: txt
      });
    }
  });

  // Atualizar HTML após desmascaramento
  rel.html = document.documentElement.outerHTML;
  return JSON.stringify(rel);
})()"""


def find_live_tab_and_extract(pattern: str):
    """
    Localiza a aba do Google Chrome que contém o padrão especificado na URL
    e executa a extração em memória via AppleScript (Live Hook).
    Retorna o dicionário de resultados ou None se a aba não estiver aberta.
    """
    clean_pattern = pattern.replace("http://", "").replace("https://", "").strip("/")
    
    # Escapar aspas para injeção segura no AppleScript
    js_escaped = SENTINELA_AUDIT_JS.replace('\\', '\\\\').replace('"', '\\"')

    ascript = f'''
    tell application "Google Chrome"
        if not (running) then
            return ""
        end if
        repeat with w in windows
            repeat with t in tabs of w
                if (URL of t) contains "{clean_pattern}" then
                    return (execute t javascript "{js_escaped}")
                end if
            end repeat
        end repeat
        return ""
    end tell
    '''
    
    try:
        res = subprocess.check_output(["osascript", "-e", ascript], text=True, stderr=subprocess.DEVNULL).strip()
        if res and res.startswith("{"):
            return json.loads(res)
    except Exception:
        pass
    return None


def fallback_shadow_copy_extraction(url: str, output_html: Path):
    """
    Fallback: Executa a extração quando a aba NÃO está aberta no Chrome.
    Cria uma pasta descartável em /tmp sem o arquivo SingletonLock e roda single-file headless.
    """
    timestamp = int(time.time())
    temp_dir = Path(f"/tmp/chrome_shadow_{timestamp}")
    
    # Identificar o perfil ativo mais provável que possui Cookies
    profiles = ["Default"] + [f"Profile {i}" for i in range(1, 10)]
    active_profile = "Default"
    for p in profiles:
        cookie_path = CHROME_USER_DATA_DIR / p / "Cookies"
        if cookie_path.exists():
            active_profile = p
            break

    profile_temp = temp_dir / active_profile
    profile_temp.mkdir(parents=True, exist_ok=True)

    origem = CHROME_USER_DATA_DIR / active_profile
    for item in ["Cookies", "Cookies-wal", "Login Data", "Local Storage"]:
        src = origem / item
        dst = profile_temp / item
        if src.exists():
            try:
                if src.is_dir():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                else:
                    shutil.copy2(src, dst)
            except Exception:
                pass

    print(f"🔄 Executando fallback via Shadow Copy em /tmp com perfil [{active_profile}]...")
    
    cmd = [
        "single-file",
        f"--browser-executable-path={CHROME_APP_PATH}",
        f"--browser-args=[\"--user-data-dir={temp_dir}\", \"--profile-directory={active_profile}\", \"--no-sandbox\", \"--disable-gpu\", \"--disable-dev-shm-usage\"]",
        url,
        str(output_html)
    ]
    
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"✅ Arquivo compilado salvo em: {output_html}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="Chrome Live Extractor & Auditor")
    parser.add_argument("target", help="URL ou termo chave da aba (ex: whaticket.com ou https://app.whaticket.com/users)")
    parser.add_argument("--output", "-o", default=None, help="Caminho do arquivo HTML de saída")
    parser.add_argument("--project", "-p", default=None, help="Nome do projeto em ~/projetos/SITES/<NOME>")
    parser.add_argument("--audit-report", action="store_true", help="Salva relatório JSON de auditoria")
    parser.add_argument("--open", action="store_true", help="Abre o HTML no navegador após extrair")
    args = parser.parse_args()

    # Definir pasta de saída
    if args.project:
        out_dir = Path.home() / "projetos/SITES" / args.project
        out_dir.mkdir(parents=True, exist_ok=True)
        symlink = Path.home() / "projetos" / args.project
        if not symlink.exists():
            try:
                symlink.symlink_to(out_dir)
            except Exception:
                pass
    else:
        out_dir = Path.cwd()

    output_file = Path(args.output) if args.output else (out_dir / "index_live.html")
    report_file = output_file.with_suffix(".audit.json")

    print(f"🔍 [Live Hook] Verificando se a aba '{args.target}' já está aberta no Chrome ativo...")
    start_time = time.time()
    
    live_data = find_live_tab_and_extract(args.target)
    
    if live_data and "html" in live_data:
        elapsed = time.time() - start_time
        print(f"⚡ [Pilar 1] Aba ativa localizada! Extração em tempo real concluída em {elapsed:.2f}s!")
        print(f"   • Título da Página: {live_data.get('title')}")
        print(f"   • URL Capturada: {live_data.get('url')}")
        print(f"   • Senhas Desmascaradas: {live_data.get('senhasDesmascaradas')}")
        print(f"   • Campos Desbloqueados: {live_data.get('camposDesbloqueados')}")
        print(f"   • Overlays Removidos: {live_data.get('overlaysRemovidos')}")
        print(f"   • Inputs Identificados: {len(live_data.get('inputs', []))}")
        print(f"   • Botões Detectados: {len(live_data.get('botoes', []))}")

        html_content = live_data.pop("html")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"💾 DOM salvo em: {output_file} ({len(html_content):,} bytes)")

        if args.audit_report:
            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(live_data, f, indent=2, ensure_ascii=False)
            print(f"📊 Relatório de auditoria salvo em: {report_file}")

    else:
        print("⚠️ Nenhuma aba aberta encontrada correspondente. Acionando Pilar 2 (Shadow Copy)...")
        fallback_shadow_copy_extraction(args.target, output_file)

    if args.open:
        subprocess.run(["open", str(output_file)])


if __name__ == "__main__":
    main()
