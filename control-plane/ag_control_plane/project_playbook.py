"""Cache operacional por projeto (Project Playbook) (Item 14).

Armazena em cache dados operacionais estáticos para evitar redescobri-los a cada Issue:
- PACKAGE_MANAGER
- INSTALL_COMMAND
- TEST_COMMANDS
- BUILD_COMMAND
- LINT_COMMAND
- DEV_COMMAND
- KNOWN_SERVICES
- KNOWN_PORTS
- KNOWN_APIS
- KNOWN_MCPS
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("ag-project-playbook")


@dataclass
class ProjectPlaybookData:
    project: str
    package_manager: str
    install_command: str
    test_commands: List[str]
    build_command: str
    lint_command: str
    dev_command: str
    known_services: List[str]
    known_ports: List[int]
    known_apis: List[str]
    known_mcps: List[str]
    manifest_hash: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProjectPlaybookCache:
    """Gerencia o cache do playbook por projeto, invalidando apenas sob alteração de manifesto."""

    def __init__(self, root_dir: Optional[Path] = None):
        self.root_dir = root_dir or Path(__file__).resolve().parent.parent
        self.playbooks_dir = self.root_dir / ".control-plane" / "playbooks"
        self.playbooks_dir.mkdir(parents=True, exist_ok=True)

    def _compute_manifest_hash(self, workspace_path: Path) -> str:
        h = hashlib.sha256()
        manifests = [
            workspace_path / "requirements.txt",
            workspace_path / "package.json",
            workspace_path / "pyproject.toml",
            workspace_path / "Cargo.toml",
        ]
        for m in manifests:
            if m.exists():
                try:
                    h.update(m.read_bytes())
                except Exception:
                    pass
        return h.hexdigest()[:16]

    def get_playbook(self, project_slug: str, workspace_path: Path) -> ProjectPlaybookData:
        cache_file = self.playbooks_dir / f"{project_slug}.json"
        manifest_hash = self._compute_manifest_hash(workspace_path)

        if cache_file.exists():
            try:
                data = json.loads(cache_file.read_text(encoding="utf-8"))
                if data.get("manifest_hash") == manifest_hash:
                    return ProjectPlaybookData(**data)
            except Exception:
                pass

        # Gera e persiste o playbook para o projeto
        playbook = self._discover_playbook(project_slug, workspace_path, manifest_hash)
        try:
            cache_file.write_text(json.dumps(playbook.to_dict(), indent=2), encoding="utf-8")
        except Exception as e:
            logger.warning(f"Erro ao salvar playbook de {project_slug}: {e}")

        return playbook

    def _discover_playbook(
        self, project_slug: str, workspace_path: Path, manifest_hash: str
    ) -> ProjectPlaybookData:
        logger.info(f"[PLAYBOOK] Descobrindo comandos do projeto '{project_slug}'...")

        pkg_mgr = "pip"
        install_cmd = "pip install -r requirements.txt"
        test_cmds = [".venv/bin/pytest tests/"]
        build_cmd = "none"
        lint_cmd = "flake8 ."
        dev_cmd = "python main.py"
        ports = []
        services = []

        if (workspace_path / "package.json").exists():
            pkg_mgr = "npm"
            install_cmd = "npm install"
            test_cmds = ["npm test"]
            build_cmd = "npm run build"
            lint_cmd = "npm run lint"
            dev_cmd = "npm run dev"

        if project_slug in ("antigravity-control-plane", "jarvis"):
            ports = [8765, 8088]
            services = ["voice_gateway", "remote_gateway", "chatgpt_voice"]
            test_cmds = [".venv/bin/pytest tests/"]

        return ProjectPlaybookData(
            project=project_slug,
            package_manager=pkg_mgr,
            install_command=install_cmd,
            test_commands=test_cmds,
            build_command=build_cmd,
            lint_command=lint_cmd,
            dev_command=dev_cmd,
            known_services=services,
            known_ports=ports,
            known_apis=["github", "gemini", "openai"],
            known_mcps=["aas-mcp", "chrome-devtools"],
            manifest_hash=manifest_hash,
        )
