import toml
from typing import Any

from .settings_meta import SETTINGS_META
from src.utils.constants import ProjectPaths


class SettingsManager:
    @staticmethod
    def get_settings() -> dict:
        return toml.load(ProjectPaths.app_settings_path)
    
    @staticmethod
    def save_settings(new_settings: dict) -> None:
        ProjectPaths.app_settings_path.write_text(toml.dumps(new_settings))

    @staticmethod
    def get_meta(group: str):
        return SETTINGS_META.get(group, [])

    @staticmethod
    def get_value(group: str, param: str) -> Any:
        return SettingsManager.get_settings()[group].get(param)

    @staticmethod
    def get_groups():
        return list(SETTINGS_META.keys())

    @staticmethod
    def update_setting(group: str, param: str, value: Any) -> None:
        settings = SettingsManager.get_settings()
        if group in settings and param in settings[group]:
            settings[group][param] = value
            SettingsManager.save_settings(settings)
