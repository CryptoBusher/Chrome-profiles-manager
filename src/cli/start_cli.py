from sys import stderr, exit

import questionary
from loguru import logger

from src.utils.helpers import kill_chrome_processes
from .base_cli import BaseCli
from .profiles_cli import ProfilesCli
from .extensions_cli import ExtensionsCli
from .automation_cli import AutomationCli
from .settings_cli import SettingsCli


class StartCli(BaseCli):
    CLI_OPTIONS = {
        'launch_profiles': {
            'human_name': '🚀 Launch profiles',
            'action': lambda: ProfilesCli.launch_profiles()
        },
        'show_profiles': {
            'human_name': '📖 Show profiles',
            'action': lambda: ProfilesCli.show_profiles()
        },
        'set_comments': {
            'human_name': '📝 Set comments',
            'action': lambda: ProfilesCli.set_comments()
        },
        'run_scripts': {
            'human_name': '🤖 Execute scripts',
            'action': lambda: AutomationCli.show()
        },
        'manage_extensions': {
            'human_name': '🧩 Extensions management',
            'action': lambda: ExtensionsCli.show()
        },
        'create_profiles': {
            'human_name': '➕ Create profiles',
            'action': lambda: ProfilesCli.create_profiles()
        },
        'kill_chrome_processes': {
            'human_name': '💀 Kill Chrome processes',
            'action': lambda: kill_chrome_processes()
        },
        'settings': {
            'human_name': '🔧 Settings',
            'action': lambda: SettingsCli.show()
        },
        'exit': {
            'human_name': '🚪 Exit',
            'action': lambda: StartCli.exit_program()
        }
    }

    @staticmethod
    def exit_program():
        logger.info("Exiting the program")
        exit(0)


    @classmethod
    def show(cls):
        while True:
            selected_option_human_name = questionary.select(
                "Choose an action",
                choices=[option["human_name"] for option in cls.CLI_OPTIONS.values()],
                style=cls.CUSTOM_STYLE
            ).ask()

            if selected_option_human_name is None:
                cls.exit_program()

            selected_option_key = next(
                (key for key, value in cls.CLI_OPTIONS.items() if value["human_name"] == selected_option_human_name),
                None
            )

            if not selected_option_key:
                cls.exit_program()

            selected_option = cls.CLI_OPTIONS[selected_option_key]
            if selected_option["action"]:
                selected_option["action"]()
            else:
                logger.warning("This feature is not yet implemented")
