from random import shuffle

from loguru import logger
from questionary import select, text, confirm

from .base_cli import BaseCli
from src.core.settings.settings_meta import ParamType
from src.core.settings.settings_manager import SettingsManager


class SettingsCLI(BaseCli):
    @classmethod
    def start(cls):
        while True:
            group = cls._select_group()
            if not group:
                return
            
            cls._handle_group(group)

    @classmethod
    def _select_group(cls):
        groups = {
            'general': 'general Settings',
            'browser': 'browser Settings',
            'back': '🏠 back to main menu'
        }
        
        choice = select(
            "Select settings group:",
            choices=list(groups.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        return next((k for k, v in groups.items() if v == choice), None)

    @classmethod
    def _handle_group(cls, group: str):
        while True:
            param = cls._select_param(group)
            if not param:
                break
            
            cls._edit_param(group, param)

    @classmethod
    def _select_param(cls, group: str):
        params = SettingsManager.get_meta(group)
        choices = [
            {
                'name': f"{p.name} ({SettingsManager.get_value(group, p.key)})", 
                'value': p
            } for p in params
        ]
        choices.append({'name': 'back', 'value': None})
        
        return select(
            f"Select parameter to edit in {group}:",
            choices=choices,
            style=cls.CUSTOM_STYLE
        ).ask()

    @classmethod
    def _edit_param(cls, group: str, param):
        current_value = SettingsManager.get_value(group, param.key)
        new_value = cls._ask_param_value(param, current_value)
        
        if new_value is not None:
            try:
                SettingsManager.update_setting(group, param.key, new_value)
                logger.success(f"Successfully updated {param.name}!")
            except Exception as e:
                logger.error(f"Error updating {param.name}")
                logger.debug(f"Error updating {param.name}: {str(e)}")

    @classmethod
    def _ask_param_value(cls, param, current_value):
        try:
            if param.param_type == ParamType.BOOL:
                return confirm(
                    param.description,
                    default=bool(current_value)
                ).ask()

            if param.param_type == ParamType.SELECT:
                return select(
                    param.description,
                    choices=param.options,
                    default=str(current_value)
                ).ask()

            if param.param_type in (ParamType.INT, ParamType.FLOAT):
                return cls._ask_numeric_param(param, current_value)

            return text(
                param.description,
                default=str(current_value),
                validate=lambda val: cls._validate_param_value(param, val)
            ).ask()
        
        except:
            return None

    @classmethod
    def _ask_numeric_param(cls, param, current_value):
        while True:
            value = text(
                f"{param.description} ({param.min}-{param.max})",
                default=str(current_value),
                validate=lambda val: cls._validate_param_value(param, val)
            ).ask()
            
            if value is None:
                return None
                
            try:
                return int(value) if param.param_type == ParamType.INT else float(value)
            except:
                logger.error("Invalid number format")

    @staticmethod
    def _validate_param_value(param, value):
        try:
            if param.param_type == ParamType.INT:
                num = int(value)
                if not (param.min <= num <= param.max):
                    return f"Must be between {param.min}-{param.max}"
                
            elif param.param_type == ParamType.FLOAT:
                num = float(value)
                if not (param.min <= num <= param.max):
                    return f"Must be between {param.min}-{param.max}"
                
            return True
        except ValueError:
            return "Invalid value format"
