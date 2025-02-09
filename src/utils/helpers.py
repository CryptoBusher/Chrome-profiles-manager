import os
import json
import shutil
import sys
import math

from loguru import logger

from src.utils.constants import *


def get_users_list() -> list[str]:
    users = []
    for user in os.listdir(USERS_PATH):
        users.append(user)

    return sort_users(users)


def sort_users(users_list: list[str | int]) -> list[str]:
    numeric_users = [u for u in users_list if u.isdigit()]
    non_numeric_users = [u for u in users_list if not any(char.isdigit() for char in u)]
    numeric_users.sort(key=int)
    non_numeric_users.sort()

    users_list_sorted = numeric_users + non_numeric_users
    return users_list_sorted


def get_comments_for_users() -> dict:
    try:
        comments_file_path = DATA_PATH / "comments_for_users.json"
        with open(comments_file_path, 'r', encoding="utf-8") as f:
            comments = json.load(f)
    except FileNotFoundError:
        return {
            "success": False,
            "description": "файл с комментариями не найден"
        }

    except json.JSONDecodeError:
        return {
            "success": False,
            "description": "не удалось прочитать файл с комментариями"
        }

    return {
        "success": True,
        "comments": comments
    }


def set_comments_for_users(user_names: list[str | int], comment: str | int | float) -> dict:
    result = get_comments_for_users()
    if result["success"]:
        comments = result["comments"]
    else:
        logger.warning(f"⚠️ Не удалось загрузить комментарии, причина: {result["description"]}")
        return result

    for name in user_names:
        comments[name] = comment

    comments_file_path = DATA_PATH / "comments_for_users.json"
    with open(comments_file_path, 'w', encoding="utf-8") as f:
        json.dump(comments, f, indent=4, ensure_ascii=False)

    return {
        "success": True
    }


def kill_chrome_processes() -> None:
    try:
        if sys.platform == 'win32':
            os.system('taskkill /F /IM chrome.exe')
        else:
            os.system('pkill chrome')
        logger.info(f'✅  Все процессы Chrome завершены')
    except Exception as e:
        logger.error(f'⛔  Не удалоcь завершить процессы Chrome')
        logger.error(f'⛔  Не удалоcь завершить процессы Chrome, причина: {e}')


def calculate_window_positions(users_amount: int,
                               screen_width_px: int = 1920,
                               screen_height_px: int = 1080,
                               min_width=300,
                               min_height=200) -> list[dict[str, int]]:

    cols = math.ceil(math.sqrt(users_amount))
    rows = math.ceil(users_amount / cols)

    while cols * min_width > screen_width_px or rows * min_height > screen_height_px:
        cols -= 1
        rows = math.ceil(users_amount / cols)

    window_width = screen_width_px // cols
    window_height = screen_height_px // rows

    if window_width < min_width:
        window_width = min_width
    if window_height < min_height:
        window_height = min_height

    user_positions = []
    for i in range(users_amount):
        row = i // cols
        col = i % cols

        x = col * window_width
        y = row * window_height

        user_positions.append({
            'x': x,
            'y': y,
            'width': window_width,
            'height': window_height
        })

    return user_positions
