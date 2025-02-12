from loguru import logger

from src.core.settings.settings_manager import SettingsManager
from src.config import set_logger, set_language


settings = SettingsManager.load_settings()
set_language(settings["language"])

set_logger()

