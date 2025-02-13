from random import shuffle

import toml
from questionary import select, checkbox
from loguru import logger

from .base_cli import BaseCli
from src.utils.constants import ProjectPaths
from src.cli.profiles_cli import ProfilesCli
from src.core.automation.automation_manager import AutomationManager, ScriptConfig


class AutomationCli(BaseCli):
    @classmethod
    def show(cls):
        automation_config = toml.load(ProjectPaths.automation_path / "config.toml")

        activity_options = {
            'selenium': '🤖 Selenium scripts',
            'playwright': '🤖 Playwright scripts',
            'other': '🤖 Other scripts',
            'back_to_start': '🏠 Back to the main menu'
        }

        activity_option_value = select(
            "Select scripts type",
            choices=list(activity_options.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if activity_option_value is None:
            return

        script_type = next((key for key, value in activity_options.items() if value == activity_option_value), None)

        if script_type == None or script_type == 'back_to_start':
            return

        script_configs_raw = automation_config[script_type]

        selected_script_human_names = checkbox(
            "Select scripts to execute",
            choices=list([config['human_name'] for config in script_configs_raw]),
            style=cls.CUSTOM_STYLE
        ).ask()
 
        selected_script_configs = [
            ScriptConfig(
                name=config['name'],
                human_name=config['human_name'],
                script_path=ProjectPaths.automation_path / script_type / config['folder_name'],
                entry_file_path=ProjectPaths.automation_path / script_type / config['folder_name'] / config["entry_file"],
                entry_function_name=config["entry_function"]
            )
            for config in script_configs_raw if config['human_name'] in selected_script_human_names
        ]

        selected_profiles = ProfilesCli.select_profiles()

        shuffle_profiles_choice = select(
            "Shuffle profiles?",
            choices=[so[1] for so in cls.BOOL_OPTIONS],
            style=cls.CUSTOM_STYLE
        ).ask()
        
        shuffle_profiles = next(so[0] for so in cls.BOOL_OPTIONS if so[1] == shuffle_profiles_choice)

        shuffle_scripts_choice = select(
            "Shuffle scripts?",
            choices=[so[1] for so in cls.BOOL_OPTIONS],
            style=cls.CUSTOM_STYLE
        ).ask()

        shuffle_scripts = next(so[0] for so in cls.BOOL_OPTIONS if so[1] == shuffle_scripts_choice)

        headless_choice = select(
            "Use headless mode?",
            choices=[so[1] for so in cls.BOOL_OPTIONS],
            style=cls.CUSTOM_STYLE
        ).ask()

        headless = next(so[0] for so in cls.BOOL_OPTIONS if so[1] == headless_choice)

        if shuffle_profiles:
            shuffle(selected_profiles)

        for profile_name in selected_profiles:
            if shuffle_scripts:
                shuffle(selected_script_configs)

            AutomationManager.execute_scripts(profile_name,
                                              script_type,
                                              selected_script_configs,
                                              headless)
