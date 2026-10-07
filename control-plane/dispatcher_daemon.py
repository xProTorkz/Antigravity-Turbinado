#!/usr/bin/env python3
import logging
import os
import signal
import sys
import time
from pathlib import Path
from ag_control_plane.dispatcher import Dispatcher

log_dir = Path(__file__).resolve().parent / ".control-plane" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "dispatcher.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(log_file), encoding="utf-8")
    ]
)
logger = logging.getLogger("ag-dispatcher-daemon")

running = True

def handle_signal(signum, frame):
    global running
    logger.info(f"Sinal {signum} recebido. Encerrando graciosamente...")
    running = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

def main():
    logger.info("Iniciando Antigravity Dispatcher Daemon (Fast Dispatch Mode)...")
    dispatcher = Dispatcher()

    event_driven = os.environ.get("AG_EVENT_DRIVEN_DISPATCH", "ON").upper() in ("ON", "TRUE", "1")
    try:
        poll_fallback = max(1, int(os.environ.get("AG_POLL_FALLBACK_SECONDS", "5")))
    except ValueError:
        poll_fallback = 5

    logger.info(f"Configuração: EVENT_DRIVEN_DISPATCH={'ON' if event_driven else 'OFF'}, POLL_FALLBACK_SECONDS={poll_fallback}s")

    while running:
        try:
            processed = dispatcher.run_cycle()
            if processed > 0:
                logger.info(f"Ciclo concluído. Tarefas processadas: {processed}")
        except Exception as e:
            logger.error(f"Erro inesperado no loop do dispatcher: {e}", exc_info=True)

        if not running:
            break

        if event_driven:
            # Acorda imediatamente se uma issue/evento ocorrer, ou cai no fallback de 5s
            dispatcher.wait_for_event(timeout=float(poll_fallback))
        else:
            time.sleep(poll_fallback)

    logger.info("Dispatcher encerrado com sucesso.")

if __name__ == "__main__":
    main()
