import re

import questionary
from loguru import logger

from src.utils.helpers import get_users_list
from src.chrome.chrome import Chrome
from .utils import custom_style


def create_multiple_users() -> None:
    create_methods = [
        '📝 задать вручную',
        '🤖 задать автоматически',
        '🏠 назад в меню'
    ]

    create_method = questionary.select(
        "Выбери способ создания имен",
        choices=create_methods,
        style=custom_style
    ).ask()

    if not create_method:
        logger.warning("⚠️ Активность не выбрана")
        return

    if 'назад в меню' in create_method:
        return

    existing_user_names = get_users_list()

    users_to_create = []

    if 'задать вручную' in create_method:
        names_raw = questionary.text(
            "Впиши названия юзеров через запятую или каждое с новой строки\n",
            style=custom_style
        ).ask()
        selected_names = list(set(i.strip() for i in re.split(r'[\n,]+', names_raw) if i.strip()))
        names_to_skip = list(set(existing_user_names) & set(selected_names))

        if names_to_skip:
            logger.warning(f'⚠️ Пропускаем юзеров {names_to_skip}, имена уже заняты')

        users_to_create = [item for item in selected_names if item not in names_to_skip]

    elif 'задать автоматически' in create_method:
        amount = questionary.text(
            "Впиши количество юзеров для создания\n",
            style=custom_style
        ).ask()

        try:
            amount = int(amount)
        except ValueError:
            logger.warning('⚠️ Неверное количество')
            return

        highest_existing_numeric_name = 0

        for name in existing_user_names:
            try:
                num = int(name)
                if num > highest_existing_numeric_name:
                    highest_existing_numeric_name = num
            except ValueError:
                continue

        start = highest_existing_numeric_name + 1
        users_to_create = list(range(start, start + amount))

    chrome = Chrome()
    for name in users_to_create:
        chrome.create_new_user(str(name))
