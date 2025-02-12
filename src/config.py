import gettext
import os
from sys import stderr

import toml
from loguru import logger
from src.utils.constants import ProjectPaths


def set_logger():
    def logs_emoji_filter(record):
        EMOJIS = {
            "SUCCESS": "✅",
            "ERROR": "⛔",
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "DEBUG": "🐛",
        }

        level = record["level"].name
        emoji = EMOJIS.get(level, "")
        return f"{emoji} {record['message']}"

    logger.remove()
    log_format = "<white>{time:YYYY-MM-DD HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>"
    logger.add(stderr, level="INFO", format=log_format, filter=logs_emoji_filter)
    logger.add(
        ProjectPaths.logs_path / "app_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format=log_format,
        rotation="00:00",
        retention="7 days",
        compression="zip"
    )


def set_language(language_code: str):
    global current_language
    current_language = language_code
    lang = gettext.translation('messages', localedir=ProjectPaths.locales_path, languages=[language_code], fallback=True)
    lang.install()
