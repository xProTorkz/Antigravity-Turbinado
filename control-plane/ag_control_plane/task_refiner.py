from __future__ import annotations

import json
import logging
import os
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from .execution_brief import ExecutionBrief, FilePlanItem, ReadOnlyContextItem
from .github_client import GitHubClient
from .task_parser import TaskParser
from .notification_bridge import NotificationBridge, StatusEvent, get_notification_bridge

logger = logging.getLogger("ag-task-refiner")


class GitHubTaskRefiner:
    """
    Camada de Refinamento no GitHub (Fases 1 a 12).
    Audita pedidos preliminares com 'refinement:pending', resolve arquivos candidatos cirúrgicos,
    valida e especializa skills, verifica conflitos via ConflictGuard e emite o execution_brief fechado.
    """

    GENERIC_SKILLS = {
        "@developer", "@desenvolvedor", "@programador", "@generic",
        "@coder", "@software-engineer", "@assistant", "@assistente",
        "@ai", "@chatgpt"
    }

    def __init__(
        self,
        root_dir: Optional[Path] = None,
        github_client: Optional[GitHubClient] = None,
        registry: Optional[Dict[str, Any]] = None,
        notification_bridge: Optional[Any] = None,
    ):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.registry_file = self.root_dir / "PROJECT_REGISTRY.json"
        self.github = github_client or GitHubClient()
        self.registry = registry if registry is not None else self._load_registry()
        self.notification_bridge = notification_bridge or get_notification_bridge()

    def _emit_status(
        self,
        status: str,
        project: str,
        issue_number: int,
        repo: str,
        comment: str,
        reason: Optional[str] = None,
        labels: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Any:
        event = StatusEvent(
            status=status,
            project=project,
            issue_number=issue_number,
            repo=repo,
            comment=comment,
            reason=reason,
            labels=labels or [],
            metadata=metadata or {},
        )
        return self.notification_bridge.emit(event)

    def _load_registry(self) -> Dict[str, Any]:
        if self.registry_file.exists():
            try:
                return json.loads(self.registry_file.read_text(encoding="utf-8"))
            except Exception as e:
                logger.warning(f"Erro ao carregar registry: {e}")
        return {}

    def resolve_project(self, title: str, body: str, labels: List[str]) -> Optional[str]:
        """Identifica o projeto alvo a partir do corpo da tarefa, título, labels ou registry."""
        # 1. YAML target_project explícito
        yaml_block = TaskParser.extract_yaml_block(body)
        if yaml_block:
            parsed = TaskParser.parse_yaml_str(yaml_block)
            candidate = parsed.get("target_project") or parsed.get("project")
            if candidate and str(candidate).lower() in self.registry:
                return str(candidate).lower()

        # 2. Labels project:<slug>
        for l in labels:
            if l.startswith("project:"):
                slug = l.split(":", 1)[1].strip().lower()
                if slug in self.registry:
                    return slug

        # 3. Padrão no título: [slug] ou "slug - ..." ou "slug | ..."
        m = re.search(r"\[([a-zA-Z0-9_\-]+)\]", title)
        if m:
            candidate = m.group(1).lower()
            if candidate in self.registry:
                return candidate

        # 4. Context Firewall Scope Classification
        from .context_firewall import ScopeType, classify_scope
        combined_text = f"{title}\n{body}"
        sc = classify_scope(prompt=combined_text, registry=self.registry, root_dir=self.root_dir)
        if sc.scope == ScopeType.PROJECT and sc.target_project:
            return sc.target_project
        if sc.scope == ScopeType.GLOBAL_CONTROL_PLANE and any(
            kw in combined_text.lower() for kw in ["control-plane", "control plane", "antigravity", "dispatcher", "sentinela"]
        ):
            return "antigravity-control-plane"

        title_lower = title.lower()
        body_lower = body.lower()

        # 4. Procura aliases no registry
        for slug, info in self.registry.items():
            if slug.lower() in title_lower:
                return slug.lower()
            aliases = info.get("aliases", [])
            for alias in aliases:
                if alias.lower() in title_lower:
                    return slug.lower()

        for slug, info in self.registry.items():
            if re.search(r"\b" + re.escape(slug.lower()) + r"\b", body_lower):
                return slug.lower()
            for alias in info.get("aliases", []) or []:
                if re.search(r"\b" + re.escape(alias.lower()) + r"\b", body_lower):
                    return slug.lower()

        return None

    def resolve_workstream(self, project_slug: str, title: str, body: str) -> str:
        """Determina workstream ('system', 'sharkbot', ou 'general')."""
        combined = f"{title} {body}".lower()
        if "sharkbot" in combined or "bacbo" in combined or "telegram" in combined or "sinais" in combined:
            return "sharkbot"
        return "system"

    def get_baseline_sha(self, project_slug: str, body: str) -> str:
        """Obtém baseline_sha do corpo ou do repositório local do projeto."""
        m = re.search(r"(?:baseline_sha|commit|sha):\s*([a-f0-9]{7,40})", body, re.IGNORECASE)
        if m:
            return m.group(1)

        proj_info = self.registry.get(project_slug, {})
        ws = proj_info.get("workspace")
        if ws and Path(ws).exists() and (Path(ws) / ".git").exists():
            try:
                res = subprocess.run(
                    ["git", "-C", ws, "rev-parse", "HEAD"],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if res.returncode == 0 and res.stdout.strip():
                    return res.stdout.strip()
            except Exception:
                pass

        return "0000000000000000000000000000000000000000"

    def resolve_files(
        self,
        project_slug: str,
        title: str,
        body: str,
        repo: str
    ) -> Tuple[List[FilePlanItem], List[ReadOnlyContextItem]]:
        """
        Localiza os arquivos estritamente necessários para a alteração e contexto read-only.
        Sem dump de repositório completo.
        """
        files: List[FilePlanItem] = []
        read_only: List[ReadOnlyContextItem] = []
        combined_text = f"{title}\n{body}"

        # 1. Procura caminhos explícitos no texto
        path_pattern = r"(?:(?:[\w\.\-]+/)+[\w\.\-]+\.[a-zA-Z0-9]+)"
        explicit_paths = set(re.findall(path_pattern, combined_text))

        # Filtra caminhos irrelevantes ou de documentação protegida
        cleaned_paths = set()
        for p in explicit_paths:
            p_clean = p.strip("`'\"(),;:")
            if any(p_clean.endswith(ext) for ext in [".py", ".ts", ".js", ".json", ".yaml", ".yml", ".md", ".sh", ".html", ".css"]):
                if not any(ign in p_clean for ign in [".git/", "node_modules/", ".venv/", "__pycache__/"]):
                    cleaned_paths.add(p_clean)

        proj_info = self.registry.get(project_slug, {})
        ws = Path(proj_info.get("workspace", ""))

        for path_str in sorted(cleaned_paths):
            op = "MODIFY"
            if "criar" in combined_text.lower() and path_str in combined_text:
                op = "CREATE"
            elif "excluir" in combined_text.lower() or "remover" in combined_text.lower():
                op = "DELETE"
            files.append(
                FilePlanItem(
                    path=path_str,
                    operation=op,
                    symbols=[],
                    instruction=f"Executar alteração em {path_str} conforme especificação da tarefa."
                )
            )

        # 2. Se nenhum caminho explícito foi encontrado, tenta pesquisar arquivos locais por palavra-chave
        if not files and ws.exists():
            # Busca palavras-chave relevantes
            keywords = re.findall(r"\b[a-zA-Z0-9_]{3,30}\b", combined_text)
            for kw in keywords:
                if kw.lower() in {"para", "como", "com", "uma", "esse", "este", "alterar", "validar", "task", "issue"}:
                    continue
                try:
                    candidates = list(ws.glob(f"**/*{kw}*.py"))
                    for c in candidates[:3]:
                        rel_path = str(c.relative_to(ws))
                        if not any(f.path == rel_path for f in files) and ".venv" not in rel_path:
                            files.append(
                                FilePlanItem(
                                    path=rel_path,
                                    operation="MODIFY",
                                    instruction=f"Aplicar modificação no módulo {rel_path}."
                                )
                            )
                except Exception:
                    pass

        return files, read_only

    def review_skill(
        self,
        project_slug: str,
        body: str,
        files: List[FilePlanItem]
    ) -> Tuple[str, Optional[str], Dict[str, Any]]:
        """
        Analisa a skill sugerida, reclassifica para skill mais específica se genérica.
        """
        suggested_skill: Optional[str] = None
        m = re.search(r"@([a-zA-Z0-9_\-]+)", body)
        if m:
            suggested_skill = f"@{m.group(1)}"

        initial = suggested_skill or "@pesquisa-projeto"
        final_skill = initial
        swapped = False
        reason = "Skill específica mantida."

        combined_paths = " ".join(f.path for f in files)
        body_lower = body.lower()

        if initial.lower() in self.GENERIC_SKILLS or not suggested_skill:
            swapped = True
            if "test" in combined_paths or "test" in body_lower or "valida" in body_lower:
                final_skill = "@testes-validacao"
                reason = "Skill genérica substituída por @testes-validacao baseada no foco em testes."
            elif "context" in body_lower or "budget" in body_lower or "prompt" in body_lower or "token" in body_lower:
                final_skill = "@context-window-management"
                reason = "Skill genérica substituída por @context-window-management para otimização de contexto."
            elif "git" in body_lower or "branch" in body_lower or "conflito" in body_lower:
                final_skill = "@git-governanca"
                reason = "Skill genérica substituída por @git-governanca para gestão de versionamento."
            elif "seguranca" in body_lower or "secret" in body_lower or "token" in body_lower:
                final_skill = "@seguranca-infra"
                reason = "Skill genérica substituída por @seguranca-infra para proteção de credenciais."
            else:
                final_skill = "@pesquisa-projeto"
                reason = "Skill genérica substituída pela skill canônica de pesquisa antes de modificação."

        if not final_skill.startswith("@"):
            final_skill = f"@{final_skill}"

        review_info = {
            "initial_skill": initial,
            "final_skill": final_skill,
            "swapped": swapped,
            "reason": reason,
            "status": "PASS",
        }
        return final_skill, None, review_info

    def check_conflicts(
        self,
        repo: str,
        current_issue_number: int,
        files: List[FilePlanItem],
        read_only_context: Optional[List[ReadOnlyContextItem]] = None,
        current_brief: Optional[ExecutionBrief] = None,
    ) -> Tuple[bool, List[int], List[str]]:
        """
        ConflictGuard / ImpactGuard (Patch 2A.1 e 2A.2): verifica se outras tarefas abertas
        no mesmo repositório possuem sobreposição na ordem canônica:
        1. PATH (arquivos ou diretórios pai/filho)
        2. SYMBOL (símbolos e identificadores de código)
        3. SEMANTIC_RESOURCE (recursos lógicos hierárquicos)
        com matriz de acesso (WRITE/WRITE, WRITE/READ, READ/WRITE = CONFLICT; READ/READ = SAFE).
        """
        from .execution_brief import (
            ExecutionBrief,
            ConflictDetail,
            PathConflictDetail,
            detect_impact_conflicts,
            detect_path_conflicts,
        )

        if current_brief is None:
            current_brief = ExecutionBrief(
                files=files,
                read_only_context=read_only_context or [],
            )

        conflicting_issues: List[int] = []
        conflicting_files: List[str] = []
        conflict_details: List[ConflictDetail] = []

        try:
            open_issues = self.github.list_open_issues(repo)
        except Exception as e:
            logger.warning(f"Não foi possível listar issues abertas em {repo}: {e}")
            return False, [], []

        for issue in open_issues:
            num = issue.get("number")
            if num == current_issue_number:
                continue

            issue_body = issue.get("body", "")
            other_brief = TaskParser.parse_execution_brief(issue_body)

            if other_brief and (other_brief.files or other_brief.read_only_context or other_brief.impact_set):
                detected = detect_impact_conflicts(
                    current_brief=current_brief,
                    current_issue_id=current_issue_number,
                    other_brief=other_brief,
                    other_issue_id=num,
                )
                if detected:
                    conflicting_issues.append(num)
                    for d in detected:
                        conflicting_files.append(d.resource)
                        conflict_details.append(d)
            else:
                yaml_block = TaskParser.extract_yaml_block(issue_body)
                if yaml_block:
                    parsed = TaskParser.parse_yaml_str(yaml_block)
                    scope = parsed.get("allowed_scope", [])
                    if isinstance(scope, list):
                        other_paths = [str(s).strip() for s in scope if s]
                        legacy_other_brief = ExecutionBrief(
                            files=[FilePlanItem(path=p, operation="MODIFY") for p in other_paths]
                        )
                        detected = detect_impact_conflicts(
                            current_brief=current_brief,
                            current_issue_id=current_issue_number,
                            other_brief=legacy_other_brief,
                            other_issue_id=num,
                        )
                        if detected:
                            conflicting_issues.append(num)
                            for d in detected:
                                conflicting_files.append(d.resource)
                                conflict_details.append(d)

        self.last_conflict_details = conflict_details
        has_conflict = len(conflicting_issues) > 0
        return has_conflict, sorted(list(set(conflicting_issues))), sorted(list(set(conflicting_files)))

    def refine_issue(self, repo: str, issue_number: int) -> Dict[str, Any]:
        """Executa o pipeline completo de refinamento em uma Issue."""
        logger.info(f"Iniciando refinamento da Issue #{issue_number} em {repo}")
        issue = self.github.get_issue(repo, issue_number)
        title = issue.get("title", "")
        body = issue.get("body", "")
        labels = [l["name"] for l in issue.get("labels", [])]

        # 0. ExecutionBrief Fast Path (Item 4)
        existing_brief = TaskParser.parse_execution_brief(body)
        if existing_brief:
            ok_fp, fp_errs = existing_brief.validate_fast_path(self.registry)
            if ok_fp:
                logger.info(f"[REFINER_FAST_PATH] Issue #{issue_number} possui ExecutionBrief válido. FAST_PATH=PASS.")
                self.github.update_issue_labels(
                    repo,
                    issue_number,
                    add_labels=["ag:queued"],
                    remove_labels=["refinement:pending", "refinement:blocked"]
                )
                comment_body = (
                    f"REFINEMENT_RESULT\nSTATUS=PASS\nFAST_PATH=PASS\nPROJECT={existing_brief.project}\n"
                    f"SKILL={existing_brief.skill_primary}\n"
                    "ExecutionBrief pré-existente validado com sucesso (Fast Path). Enfileirado para execução imediata."
                )
                formatted_comment = self.notification_bridge.format_comment(
                    status="REFINEMENT_PASS",
                    project=existing_brief.project,
                    issue_number=issue_number,
                    repo=repo,
                    comment=comment_body,
                    reason="FAST_PATH_VALIDATED",
                    labels=["ag:queued"],
                )
                self._emit_status(
                    status="REFINEMENT_PASS",
                    project=existing_brief.project,
                    issue_number=issue_number,
                    repo=repo,
                    comment=formatted_comment,
                    reason="FAST_PATH_VALIDATED",
                    labels=["ag:queued"],
                )
                self.github.add_comment(repo, issue_number, formatted_comment)
                return {"status": "PASS", "fast_path": True, "execution_brief": existing_brief.to_dict()}
            else:
                logger.info(f"[REFINER_FAST_PATH] ExecutionBrief existente inválido para Fast Path: {fp_errs}. Prosseguindo para refinamento padrão.")

        # 1. Resolução do Projeto
        project_slug = self.resolve_project(title, body, labels)
        if not project_slug:
            error_msg = "Não foi possível resolver o projeto canônico no PROJECT_REGISTRY."
            comment_body = f"REFINEMENT_RESULT\nSTATUS=BLOCKED\nPROJECT=unknown\nGATE=PROJECT_RESOLVED\nERROR={error_msg}"
            formatted_comment = self.notification_bridge.format_comment(
                status="REFINEMENT_BLOCKED",
                project="unknown",
                issue_number=issue_number,
                repo=repo,
                comment=comment_body,
                reason="GATE_PROJECT_RESOLVED",
                labels=["refinement:blocked"],
            )
            self._emit_status(
                status="REFINEMENT_BLOCKED",
                project="unknown",
                issue_number=issue_number,
                repo=repo,
                comment=formatted_comment,
                reason="GATE_PROJECT_RESOLVED",
                labels=["refinement:blocked"],
            )
            self.github.add_comment(repo, issue_number, formatted_comment)
            self.github.update_issue_labels(
                repo,
                issue_number,
                add_labels=["refinement:blocked"],
                remove_labels=["refinement:pending", "ag:queued"]
            )
            return {"status": "BLOCKED", "gate": "PROJECT_RESOLVED", "error": error_msg}

        proj_info = self.registry.get(project_slug, {})
        canonical_name = proj_info.get("canonical_name", project_slug)

        # 2. Resolução da Workstream
        workstream = self.resolve_workstream(project_slug, title, body)

        # 3. Arquivos Candidatos
        files, read_only = self.resolve_files(project_slug, title, body, repo)
        if not files:
            error_msg = "Não foi possível identificar arquivos candidatos específicos para a execução."
            comment_body = f"REFINEMENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\nGATE=FILES_RESOLVED\nERROR={error_msg}"
            formatted_comment = self.notification_bridge.format_comment(
                status="REFINEMENT_BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=repo,
                comment=comment_body,
                reason="GATE_FILES_RESOLVED",
                labels=["refinement:blocked"],
            )
            self._emit_status(
                status="REFINEMENT_BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=repo,
                comment=formatted_comment,
                reason="GATE_FILES_RESOLVED",
                labels=["refinement:blocked"],
            )
            self.github.add_comment(repo, issue_number, formatted_comment)
            self.github.update_issue_labels(
                repo,
                issue_number,
                add_labels=["refinement:blocked"],
                remove_labels=["refinement:pending", "ag:queued"]
            )
            return {"status": "BLOCKED", "gate": "FILES_RESOLVED", "error": error_msg}

        # 4. Baseline SHA
        baseline_sha = self.get_baseline_sha(project_slug, body)

        # 5. Skill Review
        skill_primary, skill_support, skill_review = self.review_skill(project_slug, body, files)

        # 6. ConflictGuard
        from .execution_brief import ExecutionBrief
        temp_brief = ExecutionBrief(
            project=project_slug,
            objective=title,
            baseline_sha=baseline_sha,
            skill_primary=skill_primary,
            files=files,
            read_only_context=read_only,
        )
        has_conflict, conf_issues, conf_resources = self.check_conflicts(
            repo, issue_number, files, read_only_context=read_only, current_brief=temp_brief
        )
        if has_conflict:
            details = getattr(self, "last_conflict_details", [])
            detail_strings = [d.to_reason_string() for d in details] if details else []
            error_msg = f"Conflito detectado com Issues abertas {conf_issues} nos recursos {conf_resources}."
            reason_block = "\n---\n".join(detail_strings) if detail_strings else error_msg
            comment_body = (
                f"REFINEMENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\nGATE=CONFLICT_GUARD\n"
                f"CONFLICTING_ISSUES={conf_issues}\nCONFLICTING_RESOURCES={conf_resources}\n"
                f"{reason_block}"
            )
            formatted_comment = self.notification_bridge.format_comment(
                status="REFINEMENT_BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=repo,
                comment=comment_body,
                reason="GATE_CONFLICT_GUARD",
                labels=["refinement:blocked"],
            )
            self._emit_status(
                status="REFINEMENT_BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=repo,
                comment=formatted_comment,
                reason="GATE_CONFLICT_GUARD",
                labels=["refinement:blocked"],
            )
            self.github.add_comment(repo, issue_number, formatted_comment)
            self.github.update_issue_labels(
                repo,
                issue_number,
                add_labels=["refinement:blocked"],
                remove_labels=["refinement:pending", "ag:queued"]
            )
            return {
                "status": "BLOCKED",
                "gate": "CONFLICT_GUARD",
                "conflicting_issues": conf_issues,
                "conflicting_files": conf_resources,
                "conflicting_resources": conf_resources,
                "conflict_details": [d.to_dict() for d in details],
                "error": error_msg
            }

        # 7. Montagem do ExecutionBrief
        objective = title
        if " - " in title:
            objective = title.split(" - ", 1)[1].strip()
        elif " | " in title:
            objective = title.split(" | ", 1)[1].strip()

        brief = ExecutionBrief(
            refinement_status="PASS",
            project=project_slug,
            workstream=workstream,
            objective=objective,
            baseline_sha=baseline_sha,
            skill_primary=skill_primary,
            skill_support=skill_support,
            files=files,
            read_only_context=read_only,
            do_not_touch=[
                "TASK_PROTOCOL.md",
                "JARVIS_ARCHITECTURE_LOCK.md",
                "CANONICAL_RULES.md"
            ],
            tests=[f"tests/test_{Path(f.path).stem}.py" for f in files if not f.path.startswith("tests/")],
            acceptance=[
                "Modificação cirúrgica restrita aos arquivos do file_plan.",
                "Execução dos testes específicos da alteração sem regressão.",
                "Validação de integridade e diff limpo."
            ],
            conflicts_checked=True,
        )

        valid, errs = brief.validate()
        if not valid:
            error_msg = f"Falha na validação do ExecutionBrief: {errs}"
            comment_body = f"REFINEMENT_RESULT\nSTATUS=BLOCKED\nPROJECT={project_slug}\nGATE=EXECUTION_BRIEF_VALIDATION\nERROR={error_msg}"
            formatted_comment = self.notification_bridge.format_comment(
                status="REFINEMENT_BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=repo,
                comment=comment_body,
                reason="GATE_EXECUTION_BRIEF_VALIDATION",
                labels=["refinement:blocked"],
            )
            self._emit_status(
                status="REFINEMENT_BLOCKED",
                project=project_slug,
                issue_number=issue_number,
                repo=repo,
                comment=formatted_comment,
                reason="GATE_EXECUTION_BRIEF_VALIDATION",
                labels=["refinement:blocked"],
            )
            self.github.add_comment(repo, issue_number, formatted_comment)
            self.github.update_issue_labels(
                repo,
                issue_number,
                add_labels=["refinement:blocked"],
                remove_labels=["refinement:pending", "ag:queued"]
            )
            return {"status": "BLOCKED", "gate": "EXECUTION_BRIEF_VALIDATION", "error": error_msg}

        # 8. Anexa o ExecutionBrief no corpo da Issue
        brief_yaml = brief.to_yaml()
        brief_block = f"\n\n```yaml\n{brief_yaml}```\n"

        # Remove execution_brief anterior se existir
        clean_body = re.sub(
            r"```(?:yaml|execution_brief)?\s*execution_brief:[\s\S]*?```",
            "",
            body,
            flags=re.IGNORECASE
        ).strip()
        updated_body = f"{clean_body}{brief_block}"

        # Padroniza título se necessário
        standard_workstream = "Sharkbot" if workstream == "sharkbot" else "Sistema"
        standard_title = f"{canonical_name} - {standard_workstream} | {objective}"

        try:
            self.github.update_issue(
                repo,
                issue_number,
                title=standard_title,
                body=updated_body
            )
        except Exception as e:
            logger.warning(f"Falha ao atualizar título/corpo da issue #{issue_number}: {e}")

        # 9. Promove para ag:queued
        self.github.update_issue_labels(
            repo,
            issue_number,
            add_labels=["ag:queued"],
            remove_labels=["refinement:pending", "refinement:blocked"]
        )

        # Adiciona comentário de sucesso do refinement
        refine_report = (
            f"REFINEMENT_RESULT\n"
            f"STATUS=PASS\n"
            f"PROJECT={project_slug}\n"
            f"WORKSTREAM={workstream}\n"
            f"SKILL={skill_primary}\n"
            f"FILES_COUNT={len(files)}\n"
            f"CONFLICTS_CHECKED=PASS\n"
            f"BASELINE_SHA={baseline_sha[:7]}\n"
            f"ACTION=ENQUEUED_FOR_DISPATCH"
        )
        formatted_comment = self.notification_bridge.format_comment(
            status="REFINEMENT_PASS",
            project=project_slug,
            issue_number=issue_number,
            repo=repo,
            comment=refine_report,
            reason="REFINEMENT_PASS",
            labels=["ag:queued"],
        )
        self._emit_status(
            status="REFINEMENT_PASS",
            project=project_slug,
            issue_number=issue_number,
            repo=repo,
            comment=formatted_comment,
            reason="REFINEMENT_PASS",
            labels=["ag:queued"],
        )
        self.github.add_comment(repo, issue_number, formatted_comment)

        return {
            "status": "PASS",
            "project": project_slug,
            "workstream": workstream,
            "skill": skill_primary,
            "execution_brief": brief,
            "files": [f.path for f in files],
        }

    def process_all_pending(self, repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """Processa todas as issues com rótulo refinement:pending."""
        repos_to_scan: Set[str] = set()
        if repo:
            repos_to_scan.add(repo)
        else:
            for info in self.registry.values():
                q = info.get("queue_repo") or info.get("repo")
                if q:
                    repos_to_scan.add(q)

        results: List[Dict[str, Any]] = []
        for target_repo in sorted(repos_to_scan):
            try:
                pending_issues = self.github.list_issues_by_label(target_repo, label="refinement:pending")
            except Exception as e:
                logger.warning(f"Falha ao listar issues pendentes em {target_repo}: {e}")
                continue

            for issue in pending_issues:
                num = issue.get("number")
                if num:
                    res = self.refine_issue(target_repo, num)
                    results.append(res)

        return results
