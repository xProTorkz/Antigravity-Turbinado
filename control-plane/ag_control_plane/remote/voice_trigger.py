#!/usr/bin/env python3
"""
Voice Trigger Processor for Antigravity, Siri, Alexa, and Mac.
Handles activation phrases, trailing completion triggers ("pronto", "execute", "é isso"),
and prewarms Antigravity even when idle.
"""

import logging
import re
import subprocess
from typing import NamedTuple, Optional, Tuple

logger = logging.getLogger("ag-voice-trigger")

ANTIGRAVITY_BUNDLE_ID = "com.google.antigravity"

# Padrões de ativação inicial (Siri, Alexa, Mac, Antigravity)
LEADING_PREFIX_REGEX = re.compile(
    r"^\s*(?:"
    r"(?:(?:(?:e\s+a[ií]\s+)?siri|alexa|macbook|mac)\s*[,:\-]?\s*(?:pe[çc]a\s+para\s+(?:o\s+)?|diga\s+(?:ao|para\s+o)\s+)?)?"
    r"(?:"
    r"(?:despertar|acordar)\s+(?:e\s+abrir\s+)?antigravity|"
    r"(?:abrir?|abra|ative|iniciar?)\s+(?:o\s+)?antigravity|"
    r"antigravity"
    r")\s*(?:[,:\-]|e\s+|por\s+favor\s*|que\s+|para\s+)?\s*"
    r"(?:execute|executa|executar)?"
    r"|"
    r"(?:execute|executa|executar)"
    r")\s+",
    re.IGNORECASE,
)

# Padrões de finalização / encerramento falado
TRAILING_TRIGGER_REGEX = re.compile(
    r"\s*[,.\-—]?\s*\b("
    r"pronto|"
    r"[eé]\s+isso|"
    r"isso\s+[eé]\s+tudo|"
    r"execute|"
    r"executa|"
    r"executar|"
    r"pode\s+executar|"
    r"pode\s+rodar|"
    r"encerrei|"
    r"terminou|"
    r"terminado|"
    r"finalizado|"
    r"conclu[ií]do|"
    r"acabei|"
    r"s[oó]\s+isso|"
    r"tudo\s+certo|"
    r"manda\s+ver|"
    r"manda\s+bala|"
    r"fim"
    r")\b[.!?]*\s*$",
    re.IGNORECASE,
)


class VoiceTriggerResult(NamedTuple):
    original_text: str
    cleaned_prompt: str
    is_wake_only: bool
    had_completion_trigger: bool
    trigger_word: Optional[str]


def wake_antigravity() -> bool:
    """Acorda e foca o Antigravity no macOS mesmo se estiver em modo ocioso."""
    success = False
    try:
        res = subprocess.run(
            ["open", "-b", ANTIGRAVITY_BUNDLE_ID],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        success = res.returncode == 0
    except Exception as exc:
        logger.warning("Falha ao abrir Antigravity via launch: %s", exc)

    try:
        # Foca a aplicação trazendo para primeiro plano
        subprocess.run(
            ["osascript", "-e", f'tell application id "{ANTIGRAVITY_BUNDLE_ID}" to activate'],
            capture_output=True,
            text=True,
            check=False,
            timeout=3,
        )
    except Exception as exc:
        logger.debug("Falha ao focar Antigravity via osascript: %s", exc)

    return success


def clean_voice_triggers(raw_text: str) -> VoiceTriggerResult:
    """
    Processa uma transcrição de voz da Siri, Alexa, Atalhos ou Mac:
    1. Identifica se foi apenas comando de despertar ("abra antigravity", "macbook despertar");
    2. Remove gatilhos de encerramento ("pronto", "execute", "é isso") do final;
    3. Remove prefixos de invocação do início, preservando a tarefa real;
    4. Acorda o Antigravity no Mac se ainda não estiver em primeiro plano.
    """
    text = (raw_text or "").strip()
    if not text:
        return VoiceTriggerResult(
            original_text="",
            cleaned_prompt="",
            is_wake_only=False,
            had_completion_trigger=False,
            trigger_word=None,
        )

    # 1. Verifica trailing completion trigger ("..., pronto", "..., execute", "..., é isso")
    had_completion = False
    trigger_word = None
    m_trailing = TRAILING_TRIGGER_REGEX.search(text)
    if m_trailing:
        had_completion = True
        trigger_word = m_trailing.group(1).lower()
        text_without_trailing = text[: m_trailing.start()].strip()
    else:
        text_without_trailing = text

    # 2. Verifica se o texto remanescente era apenas um comando de despertar
    wake_only_patterns = [
        re.compile(r"^\s*(?:e\s+a[ií]\s+siri|siri|alexa|macbook|mac)?\s*[,:\-]?\s*(?:despertar|acordar)?\s*(?:e\s+)?(?:abrir?|abra|ative|iniciar?)?\s*(?:o\s+)?antigravity[.!?]*\s*$", re.IGNORECASE),
        re.compile(r"^\s*antigravity[.!?]*\s*$", re.IGNORECASE),
        re.compile(r"^\s*(?:macbook|mac)\s*[,:\-]?\s*(?:despertar|acordar)[.!?]*\s*$", re.IGNORECASE),
        re.compile(r"^\s*(?:despertar|acordar)\s+(?:o\s+)?(?:macbook|mac)[.!?]*\s*$", re.IGNORECASE),
        re.compile(r"^\s*(?:macbook|mac)\s*[,:\-]?\s*(?:despertar|acordar)\s+e\s+(?:abrir?|abra)\s+(?:o\s+)?antigravity[.!?]*\s*$", re.IGNORECASE),
    ]
    if any(p.match(text_without_trailing) for p in wake_only_patterns):
        wake_antigravity()
        return VoiceTriggerResult(
            original_text=raw_text,
            cleaned_prompt="",
            is_wake_only=True,
            had_completion_trigger=had_completion,
            trigger_word=trigger_word,
        )

    # 3. Remove prefixo de invocação se houver comando subsequente
    m_lead = LEADING_PREFIX_REGEX.match(text_without_trailing)
    if m_lead and m_lead.end() < len(text_without_trailing):
        cleaned = text_without_trailing[m_lead.end():].strip()
    else:
        cleaned = text_without_trailing

    # Remove conjunções soltas no início do comando ('e verifique...', 'para rodar...')
    cleaned = re.sub(r"^(?:e|que|para)\s+", "", cleaned, flags=re.IGNORECASE).strip()

    # Garante que o Antigravity seja acordado
    wake_antigravity()

    return VoiceTriggerResult(
        original_text=raw_text,
        cleaned_prompt=cleaned or text_without_trailing,
        is_wake_only=False,
        had_completion_trigger=had_completion,
        trigger_word=trigger_word,
    )
