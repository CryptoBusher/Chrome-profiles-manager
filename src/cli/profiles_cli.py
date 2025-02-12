import re
import json

import questionary
from loguru import logger

from .base_cli import BaseCli
from src.utils.constants import ProjectPaths
from src.core.browser.browser_manager import BrowserManager


class ProfilesCli(BaseCli):
    @staticmethod
    def _sort_profiles(profiles_list: list[str]):
        profiles_list_str = [str(p) for p in profiles_list]

        numeric_profiles = [p for p in profiles_list_str if p.isdigit()]
        non_numeric_users = [p for p in profiles_list_str if not any(char.isdigit() for char in p)]
        numeric_profiles.sort(key=int)
        non_numeric_users.sort()

        profiles_list_sorted = numeric_profiles + non_numeric_users
        return profiles_list_sorted

    @classmethod
    def _get_profiles_list(cls) -> list[str] | None:
        profiles = [p.name for p in ProjectPaths.profiles_path.iterdir()]
        return cls._sort_profiles(profiles)
    
    @classmethod
    def _get_profile_comment(cls, profile_name: str | int) -> str:
        profile_name = str(profile_name)
        comments_file_path = ProjectPaths.profiles_data_path / "comments_for_users.json"

        if not comments_file_path.exists():
            comments_file_path.write_text("{}", encoding="utf-8")

        with open(comments_file_path, 'r', encoding="utf-8") as f:
            comments: dict[str, str] = json.load(f)

        return comments.get(profile_name, '')

    @classmethod
    def select_profiles(cls, reverse: bool = False) -> list[str] | None:
        profiles_list = cls._get_profiles_list()

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
            choices=select_options.values(),
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
                    comment = cls._get_profile_comment(profile_name)
                    if comment_substring.lower() in comment.lower:
                        selected_profiles.append(profile_name)

            case 'select_all':
                selected_profiles = profiles_list
                
            case 'back_to_start':
                return

        if not selected_profiles:
            logger.warning("Юзеры не выбраны")
            return

        selected_profiles = cls._sort_profiles(selected_profiles)

        return selected_profiles[::-1] if reverse else selected_profiles

    @classmethod
    def create_profiles(cls):
        pass

    @classmethod
    def launch_profiles(cls):
        selected_profiles = cls.select_profiles() # TODO: reverse param from config here
        if not selected_profiles:
            return

        for i, name in enumerate(selected_profiles):
            # TODO: pass working area w/h here from user settings
            window_geometry = BrowserManager.calculate_window_geometry(len(selected_profiles),
                                                                       i)
            chrome.launch_user(str(name),
                            window_geometry,
                            debug=False,
                            headless=False,
                            maximized=False)

            # TODO: sleep as per launch delay from user settings
            # sleep(config['launch_delay_sec'])

    @classmethod
    def show_profiles(cls):
        pass

    @classmethod
    def set_profiles_comments(cls):
        pass






# def set_comments_for_users(user_names: list[str | int], comment: str | int | float) -> dict:
#     result = get_comments_for_users()
#     if result["success"]:
#         comments = result["comments"]
#     else:
#         logger.warning(f"⚠️ Не удалось загрузить комментарии, причина: {result["description"]}")
#         return result

#     for name in user_names:
#         comments[name] = comment

#     comments_file_path = DATA_PATH / "comments_for_users.json"
#     with open(comments_file_path, 'w', encoding="utf-8") as f:
#         json.dump(comments, f, indent=4, ensure_ascii=False)

#     return {
#         "success": True
#     }
