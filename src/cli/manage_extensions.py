import os
from concurrent.futures import ThreadPoolExecutor

import questionary
from loguru import logger

from config import general_config
from src.utils.helpers import (get_all_default_extensions_info,
                               get_default_profiles_extensions_info,
                               copy_extension,
                               remove_extensions_in_default_profiles)
from src.utils.constants import *
from src.cli.utils import select_users, custom_style


def manage_extensions():
    selected_users = select_users()
    if not selected_users:
        return

    extension_activity = questionary.select(
        "Выбери действие с расширениями",
        choices=[
            '🟢 добавить дефолтные без замены',
            '🔴 добавить дефолтные с заменой',
            '❌  удалить расширения',
            '🏠 назад в меню'
        ],
        style=custom_style
    ).ask()

    if 'назад в меню' in extension_activity:
        return

    if 'добавить дефолтные без замены' in extension_activity:
        add_default_extensions(selected_users, False)
    elif 'добавить дефолтные с заменой' in extension_activity:
        add_default_extensions(selected_users, True)
    elif 'удалить расширения' in extension_activity:
        remove_extensions_menu(selected_users)
    else:
        logger.warning('⚠️ Действие с расширениями не выбрано')
        return


def add_default_extensions(selected_users: list[str | int], replace=False) -> None:
    default_extensions_info = get_all_default_extensions_info()
    if not default_extensions_info:
        logger.warning('⚠️ Дефолтные расширения не найдены')
        return

    choices = [
        f"{ext_id} ({name})" if name else ext_id
        for ext_id, name in default_extensions_info.items()
    ]

    selected_extensions = questionary.checkbox(
        "Выбери расширения",
        choices=choices,
        style=custom_style
    ).ask()

    selected_ids = [str(choice.split(" ")[0]) for choice in selected_extensions]

    if not selected_ids:
        logger.warning('⚠️ Расширения не выбраны')
        return

    with ThreadPoolExecutor(max_workers=general_config['max_workers']) as executor:
        futures = []
        for user in selected_users:
            user_default_profile_extensions_path = USERS_PATH / str(user) / str(USER_DEFAULT_PROFILE_NAME) / "Extensions"
            os.makedirs(user_default_profile_extensions_path, exist_ok=True)

            for ext_id in selected_ids:
                src_path = os.path.join(DEFAULT_EXTENSIONS_PATH, ext_id)
                dest_path = os.path.join(user_default_profile_extensions_path, ext_id)
                futures.append(executor.submit(copy_extension, src_path, dest_path, user, ext_id, replace))


def remove_extensions_menu(selected_users: list[str | int]) -> None:
    default_profiles_extension_info = get_default_profiles_extensions_info(selected_users)

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
        style=custom_style
    ).ask()

    selected_ids = [choice.split(" ")[0] for choice in selected_extensions]

    if not selected_ids:
        logger.warning('⚠️ Расширения не выбраны')
        return

    for user in selected_users:
        remove_extensions_in_default_profiles(user, selected_ids)



