from time import sleep

from config import general_config as config
from src.utils.helpers import calculate_window_positions
from src.chrome.chrome import Chrome
from .utils import select_users


def launch_multiple_users():
    selected_users = select_users(config['reverse_users_on_launch'])
    if not selected_users:
        return

    positions = calculate_window_positions(len(selected_users)) if config['distribute_users'] else []

    chrome = Chrome()

    for i, name in enumerate(selected_users):
        position = positions[i] if i < len(positions) else None

        chrome.launch_user(str(name),
                           position,
                           debug=False,
                           headless=False,
                           maximized=False)

        sleep(config['launch_delay_sec'])

