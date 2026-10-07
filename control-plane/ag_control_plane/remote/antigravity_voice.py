#!/usr/bin/env python3
"""
Antigravity Native Voice Recording Controller.
Controls the official Antigravity voice shortcut:
- Start/Stop Voice Recording: ⌃ Control + M (key code for 'm' with control down)
- New Conversation: ⌘ Command + Shift + N (new window) or ⌘ Command + N
- Send / Submit: Return (key code 36)
"""

import logging
import subprocess
import time
from typing import Dict, Any

logger = logging.getLogger("ag-voice-native")

ANTIGRAVITY_APP_NAME = "Antigravity"
ANTIGRAVITY_BUNDLE_ID = "com.google.antigravity"

# Estado em memória da sessão de gravação nativa
_recording_state = {
    "is_recording": False,
    "started_at": 0.0,
    "last_action": None,
}


def is_currently_recording() -> bool:
    """Verifica se há uma gravação nativa ativa no Antigravity."""
    return _recording_state["is_recording"]


def run_applescript(script: str, timeout: float = 4.0) -> bool:
    """Executa um trecho de AppleScript no macOS de forma segura."""
    try:
        res = subprocess.run(
            ["osascript", "-e", script],
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
        )
        if res.returncode != 0:
            logger.warning("Falha ao executar AppleScript: %s (stderr: %s)", script, res.stderr.strip())
            return False
        return True
    except Exception as exc:
        logger.error("Exceção ao rodar AppleScript: %s", exc)
        return False


def focus_antigravity() -> bool:
    """Acorda e traz o aplicativo Antigravity para primeiro plano."""
    try:
        subprocess.run(["open", "-b", ANTIGRAVITY_BUNDLE_ID], capture_output=True, timeout=3)
    except Exception:
        pass
    script = f'''
    tell application "{ANTIGRAVITY_APP_NAME}"
        activate
    end tell
    '''
    return run_applescript(script)


def open_new_conversation() -> bool:
    """Abre uma nova conversa / nova janela no Antigravity."""
    focus_antigravity()
    time.sleep(0.3)
    script = f'''
    tell application "System Events"
        tell process "{ANTIGRAVITY_APP_NAME}"
            set frontmost to true
            keystroke "n" using {{command down, shift down}}
        end tell
    end tell
    '''
    success = run_applescript(script)
    # Aguarda o foco do novo chat carregar
    time.sleep(0.5)
    return success


def start_voice_recording(new_conversation: bool = True) -> Dict[str, Any]:
    """
    Inicia a gravação de voz nativa no Antigravity:
    1. Foca o aplicativo Antigravity;
    2. Se new_conversation=True, abre uma nova conversa limpa (Cmd+Shift+N);
    3. Pressiona o atalho oficial ⌃ Control + M para ativar o Record Audio.
    """
    focus_antigravity()

    if new_conversation:
        open_new_conversation()

    time.sleep(0.4)

    # Atalho oficial: ⌃ Control + M
    script = f'''
    tell application "System Events"
        tell process "{ANTIGRAVITY_APP_NAME}"
            set frontmost to true
            keystroke "m" using {{control down}}
        end tell
    end tell
    '''
    success = run_applescript(script)

    _recording_state["is_recording"] = True
    _recording_state["started_at"] = time.time()
    _recording_state["last_action"] = "START"

    logger.info("Gravação de voz nativa (Control+M) iniciada no Antigravity.")
    return {
        "status": "SUCCESS" if success else "WARNING",
        "action": "RECORDING_STARTED",
        "is_recording": True,
        "message": "Gravação de voz nativa iniciada com ⌃ Control + M no Antigravity.",
        "speech": "Antigravity pronto. Gravação de voz iniciada em uma nova conversa.",
    }


def stop_voice_recording_and_send() -> Dict[str, Any]:
    """
    Encerra a gravação de voz nativa e envia a mensagem:
    1. Pressiona novamente o atalho oficial ⌃ Control + M para parar a gravação;
    2. Aguarda a transcrição de voz ser inserida no campo de texto;
    3. Pressiona Return (key code 36) para enviar a mensagem no chat.
    """
    focus_antigravity()

    # 1. Pressiona ⌃ Control + M para parar a gravação
    script_stop = f'''
    tell application "System Events"
        tell process "{ANTIGRAVITY_APP_NAME}"
            set frontmost to true
            keystroke "m" using {{control down}}
        end tell
    end tell
    '''
    run_applescript(script_stop)

    # 2. Aguarda a transcrição do áudio estabilizar no chat
    time.sleep(0.6)

    # 3. Pressiona Return (Enter) para enviar
    script_send = f'''
    tell application "System Events"
        tell process "{ANTIGRAVITY_APP_NAME}"
            set frontmost to true
            key code 36
        end tell
    end tell
    '''
    success = run_applescript(script_send)

    _recording_state["is_recording"] = False
    _recording_state["last_action"] = "STOP_AND_SEND"

    logger.info("Gravação de voz encerrada (Control+M) e mensagem enviada (Return).")
    return {
        "status": "SUCCESS" if success else "WARNING",
        "action": "RECORDING_STOPPED_AND_SENT",
        "is_recording": False,
        "message": "Gravação encerrada com ⌃ Control + M e enviada com sucesso no Antigravity.",
        "speech": "Gravação encerrada e mensagem enviada no Antigravity.",
    }


def toggle_voice_recording(new_conversation_on_start: bool = True) -> Dict[str, Any]:
    """Alterna o estado de gravação nativa (Inicia ou Para e Envia)."""
    if _recording_state["is_recording"]:
        return stop_voice_recording_and_send()
    else:
        return start_voice_recording(new_conversation=new_conversation_on_start)
