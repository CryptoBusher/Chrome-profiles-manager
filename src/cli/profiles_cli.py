import re
import json

import questionary
from loguru import logger

from .base_cli import BaseCli
from src.utils.constants import ProjectPaths
from src.core.browser.browser_manager import BrowserManager
from src.core.profile.profile_manager import ProfileManager


class ProfilesCli(BaseCli):
    @classmethod
    def select_profiles(cls) -> list[str] | None:
        profiles_list = ProfileManager.get_sorted_profiles_list()

        if not profiles_list:
            logger.error("Юзеры отсутствуют")
            return

        select_options = {
            'select_from_list': '📋 выбрать из списка',
            'enter_names': '📝 вписать названия',
            'select_by_comment': '📒 выбрать по комментарию',
            'select_all': '📦 выбрать все',
            'back_to_start': '🏠 назад в меню'
        }

        select_method_value = questionary.select(
            "Способ выбора юзеров",
            choices=list(select_options.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if select_method_value is None:
            return

        select_method_key = next((key for key, value in select_options.items() if value == select_method_value), None)

        selected_profiles = []

        match select_method_key:
            case 'select_from_list':
                selected_profiles = cls._paginate_selection(profiles_list, 'профили')

            case 'enter_names':
                names_raw = questionary.text(
                    "Впиши названия юзеров через запятую или каждое с новой строки\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                names = list(set(i.strip() for i in re.split(r'[\n,]+', names_raw) if i.strip()))
                names_to_skip = [name for name in names if name not in profiles_list]

                if names_to_skip:
                    logger.warning(f'⚠️ Пропускаем юзеров {names_to_skip}, юзеры не найдены')

                selected_profiles = [name for name in names if name not in names_to_skip]

            case 'select_by_comment':
                comment_substring: str = questionary.text(
                    "Впиши текст, который должен содержать комментарий\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                for profile_name in profiles_list:
                    comment = ProfileManager.get_profile_comment(profile_name)
                    if comment_substring.lower() in comment.lower:
                        selected_profiles.append(profile_name)

            case 'select_all':
                selected_profiles = profiles_list

            case 'back_to_start':
                return

        if not selected_profiles:
            return

        selected_profiles = ProfileManager.sort_profiles(selected_profiles)

        return selected_profiles

    @classmethod
    def create_profiles(cls):
        create_methods = {
            'manual': '📝 задать вручную',
            'auto': '🤖 задать автоматически',
            'back_to_start': '🏠 назад в меню'
        }

        create_method_value = questionary.select(
            "Выбери способ создания имен",
            choices=list(create_methods.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if create_method_value is None:
            return

        create_method_key = next((key for key, value in create_methods.items() if value == create_method_value), None)

        profiles_to_create = []
        match create_method_key:
            case 'manual':
                names_raw = questionary.text(
                    "Впиши названия юзеров через запятую или каждое с новой строки\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                selected_names = list(set(i.strip() for i in re.split(r'[\n,]+', names_raw) if i.strip()))

                existing_profile_names = ProfileManager.get_sorted_profiles_list()
                names_to_skip = list(set(existing_profile_names) & set(selected_names))

                if names_to_skip:
                    logger.warning(f'⚠️ Пропускаем юзеров {names_to_skip}, имена уже заняты')

                profiles_to_create = [item for item in selected_names if item not in names_to_skip]

            case 'auto':
                amount = questionary.text(
                    "Впиши количество юзеров для создания\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                try:
                    amount = int(amount)
                except ValueError:
                    logger.warning('⚠️ Неверное количество')
                    return

                highest_existing_numeric_name = ProfileManager.get_highest_numeric_profile_name()
                start = highest_existing_numeric_name + 1
                profiles_to_create = list(range(start, start + amount))

            case 'back_to_start':
                return

        for name in profiles_to_create:
            ProfileManager.create_profile(name)

    @classmethod
    def launch_profiles(cls):
        selected_profiles = cls.select_profiles()

        if not selected_profiles:
            logger.warning("Юзеры не выбраны")
            return

        # TODO: [CONFIG] reverse selected profiles as per config

        for i, name in enumerate(selected_profiles):
            # TODO: [CONFIG] pass working area w/h here from user settings
            window_geometry = BrowserManager.calculate_window_geometry(len(selected_profiles),
                                                                       i)
            BrowserManager().launch_browser(profile_name=name,
                                            window_geometry=window_geometry,
                                            debug=False,
                                            headless=False,
                                            maximized=False)

            # TODO: [CONFIG] sleep as per launch delay from user settings
            # sleep(config['launch_delay_sec'])

    @classmethod
    def show_profiles(cls):
        profiles_table = ProfileManager.get_profiles_table()
        print(profiles_table)

    @classmethod
    def set_comments(cls):
        selected_profiles = cls.select_profiles()

        if not selected_profiles:
            logger.warning("Юзеры не выбраны")
            return

        new_comment = questionary.text(
            "Впиши комментарий\n",
            style=cls.CUSTOM_STYLE
        ).ask()

        if new_comment is None:
            return

        for name in selected_profiles:
            ProfileManager.set_profile_comment(name, new_comment)
