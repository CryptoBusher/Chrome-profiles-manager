import toml
from pathlib import Path
from typing import Any

from src.utils.constants import ProjectPaths
from .settings_meta import SETTINGS_META, ParamType



class SettingsManager:
    @staticmethod
    def get_settings() -> dict:
        return toml.load(ProjectPaths.app_settings_path)
    
    @staticmethod
    def save_settings(new_settings: dict) -> None:
        with open(ProjectPaths.app_settings_path, 'w') as f:
            toml.dump(new_settings, f)

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
    def update_setting(cls, group: str, param: str, value: Any) -> None:
        settings = SettingsManager.get_settings()
        if group in settings and param in settings[group]:
            settings[group][param] = value
            SettingsManager.save_settings(settings)
