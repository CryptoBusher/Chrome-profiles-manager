import toml
from pathlib import Path
from random import shuffle
import importlib.util
from typing import Literal

from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.utils.constants import ProjectPaths
from src.core.browser.browser_manager import BrowserManager
from .exceptions import DebugPortConnectionError


class AutomationManager:
    def __init__(self,
                 browser_manager: BrowserManager,
                 profile_names: list[str | int],
                 scripts: list[str],
                 headless: bool = False,
                 shuffle_profiles: bool = False,
                 shuffle_scripts: bool = False):
        
        self.browser_manager = browser_manager
        self.profile_names = profile_names
        self.scripts = scripts
        self.headless = headless
        self.shuffle_profiles = shuffle_profiles
        self.shuffle_scripts = shuffle_scripts

        self.scripts_config = toml.load(ProjectPaths.automation_path / 'config.toml')

    def __establish_debug_port_connection(self, profile_name) -> webdriver.Chrome:
        try:
            debug_port = self.browser_manager.active_browsers[profile_name]['debug_port']
            logger.debug(f'{profile_name} - connecting to port {debug_port}')

            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            service = Service(ProjectPaths.chromedriver_path.name)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.debug(f'{profile_name} - connection established')

            return driver
        except Exception as e:
            raise DebugPortConnectionError(e)
    
    def __get_script_config(self, script_name: str) -> dict | None:
        for script_type, script_configs_list in self.scripts_config.items():
            for script_config in script_configs_list:
                if script_config['name'] == script_name:
                    script_config['type'] = script_type
                    return script_config
            
        return None

    def __run_script(self, script_config: dict, profile_name: str, driver: webdriver.Chrome) -> None:
        # TODO: test this approach
        try:
            required_keys = ['name', 'human_name', 'folder_name', 'entry_file', 'entry_function']
            if not all(key in script_config for key in required_keys):
                raise ValueError(_("invalid_script_configuration"))

            script_path: Path = ProjectPaths.automation_path / script_config['type'] / script_config['folder_name']
            script_file = script_path / script_config['entry_file']
            if not script_file.is_file():
                raise FileNotFoundError(_("script_file_not_found").format(script_file=script_file))

            spec = importlib.util.spec_from_file_location(script_config['name'], script_file)
            script_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script_module)

            entry_function_name = script_config['entry_function']
            if hasattr(script_module, entry_function_name):
                function = getattr(script_module, entry_function_name)
                logger.debug(f'{profile_name} - calling function {entry_function_name} from sctipt "{script_config["human_name"]}"')
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
         
    def execute_scripts(self) -> None:
        if self.shuffle_profiles:
            shuffle(self.profile_names)
                     
        for profile_name in self.profile_names:
            try:
                self.browser_manager.launch_profile(profile_name,
                                                    window_params=None,
                                                    debug=True,
                                                    headless=self.headless,
                                                    maximized=True)
                
                if not self.browser_manager.active_browsers.get(profile_name, {}).get('process'):
                    logger.error(f'{profile_name} - {_("browser_session_is_not_active")}')
                    continue

                driver = self.__establish_debug_port_connection(profile_name)

                scripts = self.scripts.copy()
                if self.shuffle_scripts:
                    shuffle(scripts)

                for script_name in scripts:
                    script_config = self.__get_script_config(script_name)
                    if not script_config:
                        logger.error(f'{profile_name} - {_("missing_script_configuration").format(script_name=script_name)}')
                        continue

                    logger.info(f'{profile_name} - {_("launching_script")} {script_config["human_name"]}')
                    self.__run_script(script_config, profile_name, driver)

                # TODO: kill driver and chrome subprocess, remove debug port from selected ports list, remove profile from active profiles dict

            except DebugPortConnectionError as e:
                logger.error(f'{profile_name} - {_("debug_port_connection_error")}')
                logger.debug(f'{profile_name} - failed to connect to debug port, reason: {e}', exc_info=True)
            except Exception as e:
                logger.error(f'{profile_name} - {_("unexpected_error_during_scripts_execution_preparation")}')
                logger.debug(f'{profile_name} - unexpected error during scripts execution preparation, reason: {e}', exc_info=True)

    def get_scripts_list_by_type(self, script_type: Literal['selenium', 'playwright', 'other']) -> list[tuple]:
        configs = self.scripts_config[script_type]
        return [(config['name'], config['human_name']) for config in configs]
