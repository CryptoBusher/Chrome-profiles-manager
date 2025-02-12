import toml
from pathlib import Path
import importlib.util
from typing import Literal
from dataclasses import dataclass

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils.constants import ProjectPaths
from src.core.browser.browser_manager import BrowserManager, Browser
from .exceptions import DebugPortConnectionError


@dataclass
class ScriptConfig:
    name: str
    human_name: str
    script_path: Path
    entry_file_path: Path
    entry_function_name: str


class AutomationManager:
    @staticmethod
    def __establish_debug_port_connection(browser: Browser) -> webdriver.Chrome:
        try:
            debug_port = browser.debug_port
            if not debug_port:
                raise DebugPortConnectionError('Browser instance is launched without debug port')

            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            service = Service(ProjectPaths.chromedriver_path.name)
            driver = webdriver.Chrome(service=service, options=chrome_options)

            return driver
        except Exception as e:
            raise DebugPortConnectionError(e)

    @staticmethod
    def __get_script_config(script_name: str) -> dict | None:
        scripts_config = toml.load(ProjectPaths.automation_path / 'config.toml')

        for script_type, script_configs_list in scripts_config.items():
            for script_config in script_configs_list:
                if script_config['name'] == script_name:
                    script_config['type'] = script_type
                    return script_config
            
        return None

    @classmethod
    def __run_script(cls, profile_name: str | int, script_config: ScriptConfig, driver: webdriver.Chrome) -> None:
        # TODO: test this approach
        try:
            profile_name = str(profile_name)

            logger.info(f'{profile_name} - {_("launching_script")} {script_config.human_name}')

            if not script_config.script_path.is_dir() or script_config.entry_file_path.is_file():
                raise FileNotFoundError(_("script_file_not_found"))

            spec = importlib.util.spec_from_file_location(script_config['name'], script_config.entry_file_path)
            script_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script_module)

            if hasattr(script_module, script_config.entry_function_name):
                function = getattr(script_module, script_config.entry_function_name)
                logger.debug(f'{profile_name} - calling function {script_config.entry_function_name} from sctipt "{script_config["human_name"]}"')
                function(driver)
            else:
                raise AttributeError(_("script_entry_function_call_error"))

            logger.success(_("script_run_success").format(script_name=script_config["human_name"]))

        except ValueError as e:
            logger.error(f'{profile_name} - {e}')
        except FileNotFoundError as e:
            logger.error(f'{profile_name} - {e}')
        except AttributeError as e:
            logger.error(f'{profile_name} - {e}')
        except Exception as e:
            logger.error(f'{profile_name} - {_("unexpected_script_execution_error")}')
            logger.debug(f'{profile_name} - unexpected script execution error: {e}', exc_info=True)

    @classmethod
    def execute_scripts(cls,
                        profile_name: str | int,
                        scripts_type: Literal['selenium', 'playwright', 'other'],
                        script_configs: list[ScriptConfig],
                        headless: bool = False) -> None:
        
        if scripts_type != 'selenium':
            logger.error(f'Feature under developement')
            return

        try:
            browser = BrowserManager().launch_browser(profile_name=profile_name,
                                            window_geometry=None,
                                            debug=True,
                                            headless=headless,
                                            maximized=True)

            if not browser:
                return

            driver = cls.__establish_debug_port_connection(browser)

            for script_config in script_configs:
                cls.__run_script(profile_name, script_config, driver)

            # TODO: kill driver and chrome subprocess, remove debug port from selected ports list, remove profile from active profiles dict

        except DebugPortConnectionError as e:
            logger.error(f'{profile_name} - {_("debug_port_connection_error")}')
            logger.debug(f'{profile_name} - failed to connect to debug port, reason: {e}', exc_info=True)
        except Exception as e:
            logger.error(f'{profile_name} - {_("unexpected_error_during_scripts_execution_preparation")}')
            logger.debug(f'{profile_name} - unexpected error during scripts execution preparation, reason: {e}', exc_info=True)

    @staticmethod
    def get_scripts_list_by_type(script_type: Literal['selenium', 'playwright', 'other']) -> list[tuple]:
        scripts_config = toml.load(ProjectPaths.automation_path / 'config.toml')

        configs_by_type = scripts_config[script_type]
        return [(config['name'], config['human_name']) for config in configs_by_type]
