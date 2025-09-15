from random import shuffle
from typing import Literal, cast

import toml
from loguru import logger
from questionary import select, checkbox

from .profiles_cli import ProfilesCli
from .base_cli import BaseCli
from src.core import AutomationManager, ScriptConfig, BrowserManager
from src.utils.constants import ProjectPaths
from src.exceptions import AutomationError, NoFreePortsError



class AutomationCli(BaseCli):
    @classmethod
    def start(cls):
        activity_options = {
            'selenium': '🤖 Selenium scripts',
            'playwright': '🤖 Playwright scripts',
            'other': '🤖 Other scripts',
            'back': '👈 Back'
        }

        activity_option_value = select(
            "Select scripts type",
            choices=list(activity_options.values()),
            style=cls.CUSTOM_STYLE
        ).ask()

        if activity_option_value is None:
            return

        activity_option_key = next((key for key, value in activity_options.items() if value == activity_option_value), None)

        if activity_option_key is None or activity_option_key == 'back':
            return

        script_type = cast(Literal['selenium', 'playwright', 'other'], activity_option_key)
        selected_script_configs = cls.__select_scripts_by_type(script_type)
        if not selected_script_configs:
            return

        selected_profiles = ProfilesCli.select_profiles()
        if not selected_profiles:
            return

        shuffle_profiles = cls._select_bool('Shuffle profiles?')
        shuffle_scripts = cls._select_bool('Shuffle scripts?')
        headless = cls._select_bool('Use headless mode?')

        if shuffle_profiles:
            shuffle(selected_profiles)

        for profile_name in selected_profiles:
            if shuffle_scripts:
                shuffle(selected_script_configs)

            try:
                AutomationManager.execute_scripts(profile_name,
                                                  script_type,
                                                  selected_script_configs,
                                                  headless)
                logger.success(f'{profile_name} - finished scripts execution')
            except NoFreePortsError as e:
                logger.error(f'{profile_name} - {e}')
            except AutomationError as e:
                logger.error(f'{profile_name} - {e}')
            except Exception as e:
                logger.error(f'{profile_name} - unexpected bulk scripts execution error')
                logger.bind(exception=True).debug(f'{profile_name} - unexpected bulk scripts execution error, reason: {e}')
            finally:
                BrowserManager().kill_browser(profile_name)

    @classmethod
    def __select_scripts_by_type(cls, script_type: Literal['selenium', 'playwright', 'other']) -> list[ScriptConfig] | None:
        automation_config = toml.load(ProjectPaths.automation_path / "config.toml")

        script_configs_raw = automation_config.get(script_type, None)
        if not script_configs_raw:
            logger.warning(f'Missing {script_type} scripts')
            return

        selected_script_human_names = checkbox(
            "Select scripts to execute",
            choices=list([config['human_name'] for config in script_configs_raw]),
            style=cls.CUSTOM_STYLE
        ).ask()

        if not selected_script_human_names:
            logger.warning(f'No scripts selected')
            return
 
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

        return selected_script_configs

