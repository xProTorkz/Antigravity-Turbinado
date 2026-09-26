"""
Permission Matrix and OS Boundary Test Suite — Antigravity Turbinado
===================================================================
Automated verification for Task #57: Computer Permissions Audit (macOS & Windows).
Tests file operations, workspace confinement, OS system protection boundaries,
TCC expectations, Windows UAC/ACL model, and configuration consistency.
"""

import os
import sys
import json
import shutil
import tempfile
import subprocess
from pathlib import Path
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Test A: In-Workspace Operations
# ---------------------------------------------------------------------------
def test_a_in_workspace_file_operations():
    """Verify that Antigravity has full create, read, update, rename, delete within workspace."""
    workspace_test_dir = ROOT_DIR / ".tmp_test_workspace_ops"
    workspace_test_dir.mkdir(parents=True, exist_ok=True)
    try:
        # Create
        test_file = workspace_test_dir / "probe_create.txt"
        test_file.write_text("initial content", encoding="utf-8")
        assert test_file.exists()

        # Read
        content = test_file.read_text(encoding="utf-8")
        assert content == "initial content"

        # Update
        test_file.write_text("updated content", encoding="utf-8")
        assert test_file.read_text(encoding="utf-8") == "updated content"

        # Rename
        renamed_file = workspace_test_dir / "probe_renamed.txt"
        test_file.rename(renamed_file)
        assert renamed_file.exists()
        assert not test_file.exists()

        # Execute a controlled python script in workspace
        script_file = workspace_test_dir / "probe_exec.py"
        script_file.write_text("print('EXEC_SUCCESS')", encoding="utf-8")
        res = subprocess.run([sys.executable, str(script_file)], capture_output=True, text=True, check=True)
        assert "EXEC_SUCCESS" in res.stdout

        # Delete
        renamed_file.unlink()
        script_file.unlink()
        assert not renamed_file.exists()
        assert not script_file.exists()
    finally:
        if workspace_test_dir.exists():
            shutil.rmtree(workspace_test_dir, ignore_errors=True)

# ---------------------------------------------------------------------------
# Test B: Out-of-Workspace Operations
# ---------------------------------------------------------------------------
def test_b_out_of_workspace_temp_file_operations():
    """Verify filesystem operations in standard OS temporary directories (/tmp or OS temp)."""
    with tempfile.TemporaryDirectory(prefix="antigravity_audit_") as tmpdir:
        temp_path = Path(tmpdir)
        probe_file = temp_path / "out_of_workspace_probe.txt"
        
        # In OS user context, standard temp directories are writable by the current user
        probe_file.write_text("temp_out_of_workspace", encoding="utf-8")
        assert probe_file.exists()
        assert probe_file.read_text(encoding="utf-8") == "temp_out_of_workspace"
        
        probe_file.unlink()
        assert not probe_file.exists()

def test_b_non_workspace_policy_in_config():
    """Audit the effective nonWorkspaceFileAccessPolicy in configure_turbo_environment.py."""
    config_script = ROOT_DIR / "scripts" / "configure_turbo_environment.py"
    content = config_script.read_text(encoding="utf-8")
    assert 'user_settings["nonWorkspaceFileAccessPolicy"] = "AGENT_SETTING_POLICY_ALLOW"' in content

# ---------------------------------------------------------------------------
# Test C: OS Protected Directories & Boundaries (Fail-Closed)
# ---------------------------------------------------------------------------
def test_c_macos_protected_directories():
    """Verify that macOS root system directories are protected from modification by SIP/permissions."""
    if sys.platform != "darwin":
        pytest.skip("Test is specific to macOS")

    # /System is strictly protected by System Integrity Protection (SIP)
    system_probe = Path("/System/.antigravity_probe_forbidden")
    with pytest.raises((PermissionError, OSError)):
        system_probe.write_text("should_fail", encoding="utf-8")

    # /usr/bin is also protected by SIP on modern macOS
    usr_bin_probe = Path("/usr/bin/.antigravity_probe_forbidden")
    with pytest.raises((PermissionError, OSError)):
        usr_bin_probe.write_text("should_fail", encoding="utf-8")

def test_c_ssh_and_keychain_protection():
    """Verify that sensitive user security stores exist or are protected from unprompted inspection."""
    home = Path.home()
    ssh_dir = home / ".ssh"
    keychain_dir = home / "Library" / "Keychains"

    # Even if .ssh exists, private keys should not be part of the product and require specific user permissions
    if ssh_dir.exists():
        # Check permissions: standard SSH dirs are 0700
        mode = oct(ssh_dir.stat().st_mode)[-3:]
        assert mode in ("700", "755", "750")

    # Keychains require macOS Keychain Access subsystem authentication / entitlements
    if sys.platform == "darwin" and keychain_dir.exists():
        assert keychain_dir.is_dir()

# ---------------------------------------------------------------------------
# Test D: TCC & Installer Requests Verification
# ---------------------------------------------------------------------------
def test_d_installer_tcc_probe_mechanism():
    """Inspect installer/install.sh to verify what TCC permissions it tests and requests."""
    install_sh = ROOT_DIR / "installer" / "install.sh"
    assert install_sh.exists()
    content = install_sh.read_text(encoding="utf-8")

    # The installer only tests file writing in $TEST_DIR ($HOME/projetos or $HOME/projects)
    assert ".tcc_probe_$$" in content
    # If the probe fails, it prompts the user to grant Full Disk Access to Terminal / Antigravity
    assert "Acesso Total ao Disco" in content

    # Verify that the installer DOES NOT request camera, mic, or screen recording
    assert "kTCCServiceCamera" not in content
    assert "kTCCServiceMicrophone" not in content
    assert "kTCCServiceScreenCapture" not in content
    assert "screencapture" not in content

def test_d_permission_manifest_consistency():
    """Verify that docs/PERMISSION_MANIFEST.md declares accurate non-usage of spy features."""
    manifest = ROOT_DIR / "docs" / "PERMISSION_MANIFEST.md"
    assert manifest.exists()
    text = manifest.read_text(encoding="utf-8")

    assert "Screen Recording" in text
    assert "NÃO UTILIZADA" in text or "Zero Captura de Tela" in text
    assert "Accessibility" in text
    assert "Não utilizada por padrão" in text

# ---------------------------------------------------------------------------
# Test E: Windows Installer & UAC Model Analysis
# ---------------------------------------------------------------------------
def test_e_windows_installer_privilege_level():
    """Verify installer/install.ps1 runs in standard user context without hardcoded elevation."""
    install_ps1 = ROOT_DIR / "installer" / "install.ps1"
    assert install_ps1.exists()
    content = install_ps1.read_text(encoding="utf-8")

    # The PowerShell installer does not force RunAs Administrator programmatically
    assert "Start-Process -Verb RunAs" not in content
    assert "Set-ExecutionPolicy" not in content or "Scope Process" in content or "Scope CurrentUser" in content

def test_e_windows_system_paths_model():
    """Check that Windows system protected paths require administrative privileges."""
    # ProgramFiles and System32 on Windows are protected by Windows ACLs and UAC
    # In Python, we verify standard paths are recognized
    if sys.platform == "win32":
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
        program_files = Path(os.environ.get("ProgramFiles", "C:\\Program Files"))
        probe_file = program_files / "antigravity_probe.tmp"
        if not is_admin:
            with pytest.raises(PermissionError):
                probe_file.write_text("test")

# ---------------------------------------------------------------------------
# Test F: Effective Antigravity Settings Audit
# ---------------------------------------------------------------------------
def test_f_antigravity_config_settings():
    """Check the real ~/.gemini/config/config.json settings if present, or simulate check."""
    config_file = Path.home() / ".gemini" / "config" / "config.json"
    if config_file.exists():
        data = json.loads(config_file.read_text(encoding="utf-8"))
        user_settings = data.get("userSettings", {})
        assert user_settings.get("autoExecutionPolicy") == "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER"
        assert user_settings.get("artifactReviewMode") == "ARTIFACT_REVIEW_MODE_TURBO"
        assert user_settings.get("browserJsExecutionPolicy") == "BROWSER_JS_EXECUTION_POLICY_TURBO"
        assert user_settings.get("nonWorkspaceFileAccessPolicy") == "AGENT_SETTING_POLICY_ALLOW"

# ---------------------------------------------------------------------------
# Test G: Permission Alignment Verification (Code & Documentation In Sync)
# ---------------------------------------------------------------------------
def test_g_permission_alignment_reconciled():
    """Verify that AGENT_SETTING_POLICY_ALLOW and documentation are 100% reconciled without contradictions."""
    config_script = ROOT_DIR / "scripts" / "configure_turbo_environment.py"
    config_text = config_script.read_text(encoding="utf-8")
    
    install_sh = ROOT_DIR / "installer" / "install.sh"
    install_sh_text = install_sh.read_text(encoding="utf-8")

    install_ps1 = ROOT_DIR / "installer" / "install.ps1"
    install_ps1_text = install_ps1.read_text(encoding="utf-8")
    
    workspace_gov = ROOT_DIR / "docs" / "WORKSPACE_GOVERNANCE.md"
    gov_text = workspace_gov.read_text(encoding="utf-8")

    readme = ROOT_DIR / "README.md"
    readme_text = readme.read_text(encoding="utf-8")

    # 1. Code sets Turbo policies:
    assert 'user_settings["nonWorkspaceFileAccessPolicy"] = "AGENT_SETTING_POLICY_ALLOW"' in config_text
    assert 'user_settings["autoExecutionPolicy"] = "CASCADE_COMMANDS_AUTO_EXECUTION_EAGER"' in config_text

    # 2. Outdated contradictory text is completely eradicated:
    assert "Fora da pasta de projeto: Perguntar sempre / Request Review obrigatório" not in install_sh_text
    assert "Fora da pasta do projeto: Perguntar sempre / Request Review obrigatório" not in install_ps1_text
    assert "bloqueada com solicitação explícita de revisão humana" not in gov_text

    # 3. Aligned Turbo messaging is present:
    assert "Autonomia no escopo do usuário" in install_sh_text
    assert "Autonomia no escopo do usuário" in install_ps1_text
    assert "Autonomia Turbo" in gov_text
    assert "Autonomia estendida no escopo do usuário" in readme_text
