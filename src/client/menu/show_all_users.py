from loguru import logger
from rich.table import Table
from rich.console import Console

from src.utils.helpers import get_comments_for_users, get_users_list, sort_users


def show_all_users():
    users_list = get_users_list()
    users_list_sorted = sort_users(users_list)

    if not users_list_sorted:
        logger.error("⛔  Юзеры отсутствуют")
        return

    console = Console()
    table = Table(style="cyan")
    table.add_column("Название", style="magenta")
    table.add_column("Комментарии", style="green")

    result = get_comments_for_users()
    if result["success"]:
        comments = result["comments"]
    else:
        logger.warning(f"⚠️ Не удалось загрузить комментарии, причина: {result["description"]}")
        comments = {}

    for user in users_list_sorted:
        comment = comments.get(user, '')
        table.add_row(user, comment)

    console.print(table)
