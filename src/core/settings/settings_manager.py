import gettext
from pathlib import Path

import toml

from src.utils.constants import ProjectPaths


class SettingsManager:
    SETTINGS_PATH = ProjectPaths.app_settings_path

    @classmethod
    def load_settings(cls) -> dict:
        if not cls.SETTINGS_PATH.exists():
            raise FileNotFoundError(f'App settings file not found at "{cls.SETTINGS_PATH.name}"')

        return toml.load(cls.SETTINGS_PATH)

    @classmethod
    def save_settings(cls, settings: dict) -> None:
        with open(cls.SETTINGS_PATH, "w") as f:
            toml.dump(settings, f)

    @classmethod
    def set_language(cls, language_code: str) -> None:
        global current_language  # TODO: change global variable here
        current_language = language_code
        lang = gettext.translation('messages',
                                   localedir=ProjectPaths.locales_path,
                                   languages=[language_code],
                                   fallback=True)
        lang.install()
