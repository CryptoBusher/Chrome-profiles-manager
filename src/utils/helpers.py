import os
import sys

from loguru import logger

from src.utils.constants import *


def kill_chrome_processes() -> None:
    try:
        if sys.platform == 'win32':
            os.system('taskkill /F /IM chrome.exe')
        else:
            os.system('pkill chrome')
        logger.success(f'Killed all chrome processes')
    except Exception as e:
        logger.error(f'Failed to kill all chrome processes')
        logger.bind(exception=True).debug(f'Failed to kill all chrome processes, reason: {e}')
