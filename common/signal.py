import sys

from common.log import logger
import signal
import sys


def _exit_signal(signal, frame):
    logger.info(f"Close service by signal {signal}")
    sys.exit(0)


def signal_handler():
    signal.signal(signal.SIGTERM, _exit_signal)
    signal.signal(signal.SIGINT, _exit_signal)
