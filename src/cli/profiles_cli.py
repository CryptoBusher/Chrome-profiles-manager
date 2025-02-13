import re
from time import sleep

from questionary import select, text
from loguru import logger

from .base_cli import BaseCli
from src.utils.constants import ProjectPaths
from src.core.settings.settings_manager import SettingsManager
from src.core.browser.browser_manager import BrowserManager
from src.core.profile.profile_manager import ProfileManager


class ProfilesCli(BaseCli):
    @classmethod
    def select_profiles(cls) -> list[str] | None:
        profiles_list = ProfileManager.get_sorted_profiles_list()

        if not profiles_list:
            logger.error("No profiles found")
            return

        select_options = {
            'select_from_list': '📋 Select from the list',
            'enter_names': '📝 Enter names',
            'select_by_comment': '📒 Select by a comment',
            'select_all': '📦 Select all',
            'back_to_start': '🏠 Back to the main menu'
        }

        select_method_value = select(
            "Choose a method for selecting profiles",
            choices=list(select_options.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if select_method_value is None:
            return

        select_method_key = next((key for key, value in select_options.items() if value == select_method_value), None)

        if select_method_key == None or select_method_key == 'back_to_start':
            return

        selected_profiles = []

        match select_method_key:
            case 'select_from_list':
                selected_profiles = cls._paginate_selection(profiles_list, 'profiles')

            case 'enter_names':
                names_raw = text(
                    "Enter user names separated by commas or each on a new line\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                names = list(set(i.strip() for i in re.split(r'[\n,]+', names_raw) if i.strip()))
                names_to_skip = [name for name in names if name not in profiles_list]

                if names_to_skip:
                    logger.warning(f'Skipping profiles {names_to_skip}, profiles not found')

                selected_profiles = [name for name in names if name not in names_to_skip]

            case 'select_by_comment':
                comment_substring: str = text(
                    "Enter a substring of the comment (case insensitive)\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                for profile_name in profiles_list:
                    comment = ProfileManager.get_profile_comment(profile_name)
                    if comment_substring.lower() in comment.lower:
                        selected_profiles.append(profile_name)

            case 'select_all':
                selected_profiles = profiles_list


        if not selected_profiles:
            logger.warning('No profiles selected')
            return

        selected_profiles = ProfileManager.sort_profiles(selected_profiles)

        return selected_profiles

    @classmethod
    def create_profiles(cls):
        create_methods = {
            'manual': '📝 Manual entry',
            'auto': '🤖 Automatic entry',
            'back_to_start': '🏠 Back to the main menu'
        }

        create_method_value = select(
            "Choose a method for creating names",
            choices=list(create_methods.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if create_method_value is None:
            return

        create_method_key = next((key for key, value in create_methods.items() if value == create_method_value), None)

        profiles_to_create = []
        match create_method_key:
            case 'manual':
                names_raw = text(
                    "Enter user names separated by commas or each on a new line\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                selected_names = list(set(i.strip() for i in re.split(r'[\n,]+', names_raw) if i.strip()))

                existing_profile_names = ProfileManager.get_sorted_profiles_list()
                names_to_skip = list(set(existing_profile_names) & set(selected_names))

                if names_to_skip:
                    logger.warning(f'Skipping profiles {names_to_skip}, the names are already taken')

                profiles_to_create = [item for item in selected_names if item not in names_to_skip]

            case 'auto':
                amount = text(
                    "Enter the number of profiles to create\n",
                    style=cls.CUSTOM_STYLE
                ).ask()

                try:
                    amount = int(amount)
                except ValueError:
                    logger.warning('Wrong amount')
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
            logger.warning('No profiles selected')
            return
        
        if SettingsManager.get_settings()['browser']['reverse_launch_order']:
            selected_profiles = selected_profiles[::-1]

        for i, name in enumerate(selected_profiles):
            window_geometry = BrowserManager.calculate_window_geometry(len(selected_profiles),
                                                                       i,
                                                                       SettingsManager.get_settings['browser']['working_area_width_px'],
                                                                       SettingsManager.get_settings['browser']['working_area_height_px'])
            BrowserManager().launch_browser(profile_name=name,
                                            window_geometry=window_geometry,
                                            debug=False,
                                            headless=False,
                                            maximized=False)

            sleep(SettingsManager.get_settings()['browser']['launch_delay_sec'])

    @classmethod
    def show_profiles(cls):
        profiles_table = ProfileManager.get_profiles_table()
        print(profiles_table)

    @classmethod
    def set_comments(cls):
        selected_profiles = cls.select_profiles()

        if not selected_profiles:
            logger.warning('No profiles selected')
            return

        new_comment = text(
            "Enter comments\n",
            style=cls.CUSTOM_STYLE
        ).ask()

        if new_comment is None:
            return

        for name in selected_profiles:
            ProfileManager.set_profile_comment(name, new_comment)
