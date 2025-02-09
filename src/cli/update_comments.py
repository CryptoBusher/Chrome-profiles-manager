import questionary
from loguru import logger

from src.utils.helpers import set_comments_for_users
from src.cli.utils import select_users, custom_style


def update_comments():
    selected_users = select_users()
    if not selected_users:
        return

    new_comment = questionary.text(
        "Впиши комментарий\n",
        style=custom_style
    ).ask()

    result = set_comments_for_users(selected_users, new_comment)

    if result["success"]:
        logger.info("✅  Комментарии обновлены")
    else:
        logger.warning(f"⚠️ Не удалось обновить комментарии, причина: {result["description"]}")



