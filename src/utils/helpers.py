import os
import json
import shutil
import sys
import math

from loguru import logger

from src.utils.constants import *


def kill_chrome_processes() -> None:
    try:
        if sys.platform == 'win32':
            os.system('taskkill /F /IM chrome.exe')
        else:
            os.system('pkill chrome')
        logger.info(f'✅  Все процессы Chrome завершены')
    except Exception as e:
        logger.error(f'⛔  Не удалоcь завершить процессы Chrome')
        logger.error(f'⛔  Не удалоcь завершить процессы Chrome, причина: {e}')



