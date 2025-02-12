from sys import stderr
import shutil
import json

from loguru import logger

from src.utils.constants import ProjectPaths


def setup_logger():    
    def emoji_filter(record):
        level_emojis = {
            "SUCCESS": "✅",
            "ERROR": "⛔",
            "WARNING": "⚠️",
            "INFO": "ℹ️",
            "DEBUG": "🐛",
        }
        emoji = level_emojis.get(record["level"].name, "")
        return f"{emoji} {record['message']}"

    logger.remove()
    
    log_format = (
        "<white>{time:YYYY-MM-DD HH:mm:ss}</white> | "
        "<level>{level: <8}</level> | "
        "<white>{message}</white>"
    )
    
    logger.add(
        stderr,
        level="INFO",
        format=log_format,
        filter=emoji_filter
    )
    
    logger.add(
        ProjectPaths.logs_path / "app_{time:YYYY-MM-DD}.log",
        level="DEBUG",
        format=log_format,
        rotation="00:00",
        retention="7 days",
        compression="zip"
    )


def setup_data_folder():
    data_path = ProjectPaths.data_path
    required_dirs = [
        data_path,
        data_path / "app_data",
        data_path / "chromedrivers",
        data_path / "default_extensions",
        data_path / "profiles",
        data_path / "profiles_data"
    ]

    for directory in required_dirs:
        try:
            directory.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.error(f"Failed to create directory {directory}")
            logger.debug(f"Failed to create directory {directory}: {str(e)}")
            raise

    app_settings_path = data_path / 'app_data' / 'settings.toml'
    if not app_settings_path.exists():
        shutil.copy(ProjectPaths.assets_path / 'settings_template.toml',
                    app_settings_path)
        
    profile_comments_path = ProjectPaths.profiles_data_path / 'comments.json'
    if not profile_comments_path.exists():
        profile_comments_path.write_text(json.dumps({}))


def setup_app():
    setup_logger()
    setup_data_folder()
