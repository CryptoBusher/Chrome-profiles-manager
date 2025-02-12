from sys import stderr, exit

import questionary
from loguru import logger

from src.utils.helpers import kill_chrome_processes
from .base_cli import BaseCli
from .profiles_cli import ProfilesCli
from .extensions_cli import ExtensionsCli
from .automation_cli import AutomationCli
from .settings_cli import SettingsCli


class StartPage(BaseCli):
    CLI_OPTIONS = {
        'launch_profiles': {
            'human_name': '🚀 запуск профилей',
            'action': lambda: ProfilesCli.launch_profiles()
        },
        'show_profiles': {
            'human_name': '📖 просмотр профилей',
            'action': lambda: ProfilesCli.show_profiles()
        },
        'set_comments': {
            'human_name': '📝 задать комментарии',
            'action': lambda: ProfilesCli.set_comments()
        },
        'run_scripts': {
            'human_name': '🤖 прогон скриптов',
            'action': lambda: AutomationCli.show()
        },
        'manage_extensions': {
            'human_name': '🧩 работа с расширениями',
            'action': lambda: ExtensionsCli.show()
        },
        'create_profiles': {
            'human_name': '➕ создание профилей',
            'action': lambda: ProfilesCli.create_profiles()
        },
        'kill_chrome_processes': {
            'human_name': '💀 убить процессы Chrome',
            'action': lambda: kill_chrome_processes()
        },
        'settings': {
            'human_name': '🔧 настройки',
            'action': lambda: SettingsCli.show()
        },
        'exit': {
            'human_name': '🚪 выход',
            'action': lambda: StartPage.exit_programm()
        }
    }

    @staticmethod
    def exit_programm():
        logger.info("Выход из программы")
        exit(0)


    @classmethod
    def show(cls):
        while True:
            selected_option_human_name = questionary.select(
                "Выбери действие",
                choices=[option["human_name"] for option in cls.CLI_OPTIONS.values()],
                style=cls.CUSTOM_STYLE
            ).ask()

            if selected_option_human_name is None:
                cls.exit_programm()

            selected_option_key = next(
                (key for key, value in cls.CLI_OPTIONS.items() if value["human_name"] == selected_option_human_name),
                None
            )

            if not selected_option_key:
                cls.exit_programm()

            selected_option = cls.CLI_OPTIONS[selected_option_key]
            if selected_option["action"]:
                selected_option["action"]()
            else:
                logger.warning("Эта функция пока не реализована.")
