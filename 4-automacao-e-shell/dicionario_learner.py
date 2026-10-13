#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Dicionário Learner - Motor de Auto-Aprendizado e Evolução do Dicionário Léxico.
Permite auto-adicionar comandos úteis detectados em tempo de execução que não estavam
prescritos previamente nos gatilhos, organizando-os em sequências por camada e área.
Garante preservação de 100% das funções e integridade estrita de JSON.
"""

import os
import sys
import json
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timezone

DEFAULT_DICT_PATH = Path("4-automacao-e-shell/dicionario_lexico.json")

def calculate_sha256(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

class DicionarioLearner:
    def __init__(self, dict_path: Path = DEFAULT_DICT_PATH):
        self.dict_path = dict_path.resolve()
        if not self.dict_path.exists():
            # Tentar encontrar no diretório pai ou relativo
            candidates = [
                Path("4-automacao-e-shell/dicionario_lexico.json"),
                Path("dicionario_lexico.json"),
                Path(os.path.expanduser("~/.gemini/config/dicionario_lexico.json"))
            ]
            for c in candidates:
                if c.exists():
                    self.dict_path = c.resolve()
                    break
        self.modulos_dir = self.dict_path.parent / "dicionario_modulos"
        self.learned_module_file = self.modulos_dir / "03_governanca_e_aprendizado" / "comandos_aprendidos.json"
        self.builder_script = self.dict_path.parent / "build_dicionario.py"

    def trigger_rebuild(self):
        """Dispara a reconstrução do dicionário canônico a partir dos módulos."""
        if self.builder_script.exists():
            try:
                sys.path.insert(0, str(self.builder_script.parent))
                import build_dicionario
                build_dicionario.build()
                return True
            except Exception as e:
                # Fallback via subprocess
                try:
                    import subprocess
                    subprocess.run([sys.executable, str(self.builder_script)], check=True)
                    return True
                except Exception as ex2:
                    print(f"[!] Erro ao recompilar dicionário: {ex2}")
        return False

    def load(self) -> dict:
        if not self.dict_path.exists():
            raise FileNotFoundError(f"Dicionário não encontrado em: {self.dict_path}")
        with open(self.dict_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self, data: dict):
        # Validação de integridade antes de salvar
        content = json.dumps(data, indent=2, ensure_ascii=False)
        # Teste de re-parse para garantir 100% validade
        json.loads(content)
        
        with open(self.dict_path, "w", encoding="utf-8") as f:
            f.write(content)

    def infer_category(self, cmd: str) -> str:
        """Infere a categoria arquitetural com base nos binários e argumentos do comando."""
        cmd_lower = cmd.lower()
        if any(k in cmd_lower for k in ["git", "branch", "commit", "merge", "fetch", "push", "status"]):
            return "versionamento_e_git"
        elif any(k in cmd_lower for k in ["curl", "wget", "socket", "nc", "ping", "dns", "http", "api"]):
            return "conectividade_e_integracoes"
        elif any(k in cmd_lower for k in ["sql", "db", "sqlite", "mysql", "postgres", "dump", "backup"]):
            return "armazenamento_e_logs"
        elif any(k in cmd_lower for k in ["pci", "luhn", "secret", "token", "jwt", "key", "audit", "sha256", "hash"]):
            return "seguranca_e_conformidade"
        elif any(k in cmd_lower for k in ["dom", "html", "css", "js", "browser", "chrome", "devtools", "single-file"]):
            return "espelhamento_e_download_estatico"
        elif any(k in cmd_lower for k in ["ps", "kill", "top", "lsof", "pkill", "pgrep"]):
            return "processos_e_recursos"
        elif any(k in cmd_lower for k in ["kernel", "sysctl", "modprobe", "hwid", "spoof"]):
            return "runtimes_e_kernel"
        return "conectividade_e_integracoes"

    def command_exists(self, data: dict, cmd: str) -> bool:
        """Verifica se o comando já existe no dicionário."""
        raw_cmd = cmd.strip()
        
        # Verificar em aliases_linguagem
        for alias_data in data.get("aliases_linguagem", {}).values():
            if isinstance(alias_data, dict):
                # Verificar em comandos_por_contexto
                for c in alias_data.get("comandos_por_contexto", {}).values():
                    if isinstance(c, str) and raw_cmd in c:
                        return True
                    elif isinstance(c, dict) and any(raw_cmd in str(v) for v in c.values()):
                        return True
                # Verificar em fluxo_execucao_sequencial
                for etapa in alias_data.get("fluxo_execucao_sequencial", []):
                    if raw_cmd in etapa.get("comandos", []):
                        return True

        # Verificar em pipelines
        for pipe in data.get("pipelines", {}).values():
            for etapa in pipe.get("etapas", []):
                if raw_cmd in etapa.get("comandos", []):
                    return True

        # Verificar em comandos_aprendidos
        for item in data.get("comandos_aprendidos_dinamicamente", []):
            if item.get("comando") == raw_cmd:
                return True

        return False

    def learn_command(self, cmd: str, contexto: str = None, descricao: str = None,
                      camada: str = None, area: str = None, criterio_verificacao: str = None) -> dict:
        """
        Aprende e registra um novo comando no dicionário léxico.
        Adiciona de forma limpa, estruturada e sequencial.
        """
        data = self.load()
        raw_cmd = cmd.strip()

        if not raw_cmd:
            return {"status": "ERRO", "mensagem": "Comando vazio fornecido."}

        if self.command_exists(data, raw_cmd):
            return {
                "status": "IGNORADO_EXISTENTE",
                "mensagem": f"O comando já está registrado no dicionário: {raw_cmd}"
            }

        # Inferir metadados ausentes
        categoria = contexto or self.infer_category(raw_cmd)
        desc = descricao or f"Comando aprendido dinamicamente para contexto {categoria}."
        cam = camada or f"Camada de {categoria.replace('_', ' ').title()}"
        ar = area or "Operações Dinâmicas de Sistema"
        crit = criterio_verificacao or "Comando executado com exit code 0 e saída confirmada."

        # Inicializar nó de aprendizado no dicionário se não existir
        if "comandos_aprendidos_dinamicamente" not in data:
            data["comandos_aprendidos_dinamicamente"] = []

        novo_registro = {
            "id": f"cmd_aprendido_{len(data['comandos_aprendidos_dinamicamente']) + 1}",
            "comando": raw_cmd,
            "categoria": categoria,
            "descricao": desc,
            "camada": cam,
            "area": ar,
            "criterio_verificacao": crit,
            "data_aprendizado_utc": datetime.now(timezone.utc).isoformat()
        }

        data["comandos_aprendidos_dinamicamente"].append(novo_registro)

        # Se houver um alias correspondente à categoria ou contexto, inserir também em seu fluxo_execucao_sequencial
        alias_alvo = None
        if categoria in data.get("aliases_linguagem", {}):
            alias_alvo = categoria
        elif any(k in categoria for k in ["git", "pull", "sync"]):
            alias_alvo = "pull" if "pull" in categoria else "sync"
        elif any(k in categoria for k in ["fetch", "http", "api"]):
            alias_alvo = "fetch"
        elif any(k in categoria for k in ["dump", "backup"]):
            alias_alvo = "dump"

        if alias_alvo and alias_alvo in data["aliases_linguagem"]:
            alias_obj = data["aliases_linguagem"][alias_alvo]
            if "comandos_aprendidos" not in alias_obj:
                alias_obj["comandos_aprendidos"] = []
            alias_obj["comandos_aprendidos"].append(raw_cmd)

            # Adicionar como etapa sequencial complementar se houver fluxo
            if "fluxo_execucao_sequencial" in alias_obj:
                etapas = alias_obj["fluxo_execucao_sequencial"]
                nova_etapa = {
                    "etapa": len(etapas) + 1,
                    "fase": f"PASSO_DINAMICO_{len(etapas) + 1}",
                    "camada": cam,
                    "area": ar,
                    "acao": desc,
                    "comandos": [raw_cmd],
                    "criterio_verificacao": crit,
                    "bloqueio_em_caso_falha": True
                }
                etapas.append(nova_etapa)

        # Atualizar metadados globais
        data["total_comandos_aprendidos"] = len(data["comandos_aprendidos_dinamicamente"])
        data["data_atualizacao"] = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        # Se o módulo vivo de comandos aprendidos existir, registrar nele e disparar compilação
        if self.learned_module_file.exists():
            try:
                with open(self.learned_module_file, "r", encoding="utf-8") as lf:
                    mod_data = json.load(lf)
                if "comandos_aprendidos_dinamicamente" not in mod_data:
                    mod_data["comandos_aprendidos_dinamicamente"] = []
                
                if not any(x.get("comando") == raw_cmd for x in mod_data["comandos_aprendidos_dinamicamente"]):
                    mod_data["comandos_aprendidos_dinamicamente"].append(novo_registro)
                    mod_data["total_comandos_aprendidos"] = len(mod_data["comandos_aprendidos_dinamicamente"])
                    with open(self.learned_module_file, "w", encoding="utf-8") as lf:
                        json.dump(mod_data, lf, indent=2, ensure_ascii=False)
                
                # Reconstruir o dicionário canônico e o symlink global
                self.trigger_rebuild()
                data = self.load()
            except Exception as ex_mod:
                print(f"[!] Aviso ao salvar no módulo de aprendizado: {ex_mod}")
                self.save(data)
        else:
            self.save(data)

        novo_hash = calculate_sha256(json.dumps(data, ensure_ascii=False))

        return {
            "status": "APRENDIDO_COM_SUCESSO",
            "comando": raw_cmd,
            "categoria": categoria,
            "camada": cam,
            "area": ar,
            "novo_hash_dicionario": novo_hash[:16],
            "total_aprendidos": data.get("total_comandos_aprendidos", len(data.get("comandos_aprendidos_dinamicamente", []))),
            "mensagem": f"Comando aprendido com sucesso e incorporado à esteira progressiva de {categoria}."
        }

    def list_learned(self) -> list:
        data = self.load()
        return data.get("comandos_aprendidos_dinamicamente", [])

def main():
    parser = argparse.ArgumentParser(description="Dicionário Learner - Auto-Aprendizado do Dicionário Léxico")
    parser.add_argument("--cmd", type=str, help="Comando a ser aprendido")
    parser.add_argument("--contexto", type=str, help="Contexto ou categoria arquitetural")
    parser.add_argument("--desc", type=str, help="Descrição da utilidade do comando")
    parser.add_argument("--camada", type=str, help="Nome da camada arquitetural")
    parser.add_argument("--area", type=str, help="Área específica do sistema")
    parser.add_argument("--criterio", type=str, help="Critério de verificação para avanço de etapa")
    parser.add_argument("--listar", action="store_true", help="Lista todos os comandos aprendidos")
    parser.add_argument("--status", action="store_true", help="Exibe o status de aprendizado do dicionário")

    args = parser.parse_args()
    learner = DicionarioLearner()

    if args.listar:
        learned = learner.list_learned()
        print(f"\n📋 Total de comandos aprendidos dinamicamente: {len(learned)}")
        for it in learned:
            print(f"  • [{it.get('categoria')}] $ {it.get('comando')}")
            print(f"    ℹ {it.get('descricao')} (Camada: {it.get('camada')})")
        return

    if args.status:
        data = learner.load()
        learned_count = len(data.get("comandos_aprendidos_dinamicamente", []))
        print(f"\n🧠 STATUS DE APRENDIZADO DO DICIONÁRIO:")
        print(f"  • Versão do Dicionário: {data.get('versao')}")
        print(f"  • Mapeamentos Fixos: {len(data.get('mapeamento', {}))}")
        print(f"  • Comandos Aprendidos Dinamicamente: {learned_count}")
        print(f"  • Última Atualização: {data.get('data_atualizacao')}\n")
        return

    if args.cmd:
        res = learner.learn_command(
            cmd=args.cmd,
            contexto=args.contexto,
            descricao=args.desc,
            camada=args.camada,
            area=args.area,
            criterio_verificacao=args.criterio
        )
        print(f"\n🛡️ [RESULTADO]: {res.get('status')}")
        print(f"  {res.get('mensagem')}")
        if "novo_hash_dicionario" in res:
            print(f"  Hash SHA-256: {res.get('novo_hash_dicionario')}... | Total Aprendidos: {res.get('total_aprendidos')}\n")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
