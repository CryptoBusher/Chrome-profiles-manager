import questionary
from loguru import logger

from .base_cli import BaseCli
from src.utils.constants import ProjectPaths
from src.cli.profiles_cli import ProfilesCli
from src.core.extension.extension_manager import ExtensionManager


class ExtensionsCli(BaseCli):
    @classmethod
    def show(cls):
        activity_options = {
            'add_without_replace': '🟢 добавить дефолтные без замены',
            'add_with_replace': '🔴 добавить дефолтные с заменой',
            'remove': '❌ удалить расширения',
            'back_to_start': '🏠 назад в меню'
        }

        activity_option_value = questionary.select(
            "Выбери действие с расширениями",
            choices=list(activity_options.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if activity_option_value is None:
            return

        activity_option_key = next((key for key, value in activity_options.items() if value == activity_option_value), None)

        selected_profiles = ProfilesCli.select_profiles()

        if not selected_profiles:
            logger.warning("Юзеры не выбраны")
            return

        match activity_option_key:
            case 'add_without_replace':
                cls.add_default_extensions(selected_profiles, False)

            case 'add_with_replace':
                cls.add_default_extensions(selected_profiles, True)

            case 'remove':
                cls.remove_extensions_menu(selected_profiles)

            case 'back_to_start':
                return

    @classmethod
    def add_default_extensions(cls, profiles_list: list[str | int], replace: bool = False) -> None:
        default_extensions_info = ExtensionManager.get_all_default_extension_names()

        if not default_extensions_info:
            logger.warning('Дефолтные расширения не найдены')
            return

        choices = [
            f"{ext_id} ({name})" if name else ext_id
            for ext_id, name in default_extensions_info.items()
        ]

        selected_extensions = questionary.checkbox(
            "Выбери расширения",
            choices=choices,
            style=cls.CUSTOM_STYLE
        ).ask()

        selected_ids = [str(choice.split(" ")[0]) for choice in selected_extensions]

        if not selected_ids:
            logger.warning('Расширения не выбраны')
            return

        for name in profiles_list:
            name = str(name)
            for ext_id in selected_ids:
                ExtensionManager.add_extension_to_profile(name, ext_id, replace)

    @classmethod
    def remove_extensions_menu(cls, profiles_list: list[str | int]) -> None:
        default_profiles_extension_info = ExtensionManager.get_profiles_extension_names(profiles_list)

        if not default_profiles_extension_info:
            logger.warning('⚠️ Расширения в дефолтных профилях не найдены')
            return

        choices = [
            f"{ext_id} ({name})" if name else ext_id
            for ext_id, name in default_profiles_extension_info.items()
        ]

        selected_extensions = questionary.checkbox(
            "Выбери расширения",
            choices=choices,
            style=cls.CUSTOM_STYLE
        ).ask()

        selected_ids = [choice.split(" ")[0] for choice in selected_extensions]

        if not selected_ids:
            logger.warning('⚠️ Расширения не выбраны')
            return

        for name in profiles_list:
            for ext_id in selected_ids:
                ExtensionManager.remove_extension_from_profile(name, ext_id)
