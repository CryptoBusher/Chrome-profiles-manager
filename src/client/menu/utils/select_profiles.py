import re
import questionary
from loguru import logger

from src.utils.helpers import get_users_list, get_comments_for_users, sort_users
from src.client.menu.utils.helpers import custom_style


def select_users(reverse: bool = False) -> list[str] | None:
    profiles_list = get_users_list()

    if not profiles_list:
        logger.error("⛔  Юзеры отсутствуют")
        return

    select_options = [
        '📋 выбрать из списка',
        '📝 вписать названия',
        '📒 выбрать по комментарию',
        '📦 выбрать все',
        '🏠 назад в меню'
    ]

    select_method = questionary.select(
        "Способ выбора юзеров",
        choices=select_options,
        style=custom_style
    ).ask()

    if 'назад в меню' in select_method:
        return

    selected_profiles = []
    if 'выбрать из списка' in select_method:
        selected_profiles = paginate_profiles(profiles_list)

    elif 'вписать названия' in select_method:
        names_raw = questionary.text(
            "Впиши названия юзеров через запятую или каждое с новой строки\n",
            style=custom_style
        ).ask()

        names = list(set(i.strip() for i in re.split(r'[\n,]+', names_raw) if i.strip()))

        names_to_skip = [name for name in names if name not in profiles_list]

        if names_to_skip:
            logger.warning(f'⚠️ Пропускаем юзеров {names_to_skip}, юзеры не найдены')

        selected_profiles = [name for name in names if name not in names_to_skip]

    elif 'выбрать по комментарию' in select_method:
        comment_substring = questionary.text(
            "Впиши текст, который должен содержать комментарий\n",
            style=custom_style
        ).ask()

        for profile in profiles_list:
            result = get_comments_for_users()
            if result["success"]:
                comments = result["comments"]
            else:
                logger.warning(f"⚠️ Не удалось загрузить комментарии, причина: {result["description"]}")
                comments = {}

            comment = comments.get(profile, '')
            if comment_substring.lower() in comment.lower():
                selected_profiles.append(profile)

    elif 'выбрать все' in select_method:
        selected_profiles = profiles_list

    if not selected_profiles:
        logger.warning("⚠️ Юзеры не выбраны")
        return

    selected_profiles = sort_users(selected_profiles)
    if reverse:
        selected_profiles = selected_profiles[::-1]

    return selected_profiles


def paginate_profiles(profiles, items_per_page=10):
    total_pages = (len(profiles) + items_per_page - 1) // items_per_page
    current_page = 0
    selected_profiles = []

    while current_page < total_pages:
        start = current_page * items_per_page
        end = min(start + items_per_page, len(profiles))
        page_profiles = profiles[start:end]

        selected_profiles_on_page = questionary.checkbox(
            f"Выбери юзеров для запуска (страница {current_page + 1} из {total_pages})",
            choices=page_profiles,
            style=custom_style,
        ).ask()

        selected_profiles.extend(selected_profiles_on_page)

        current_page += 1

    return selected_profiles
