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
from src.exceptions import AutomationError


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
                raise AutomationError('browser instance is launched without debug port')

            chrome_options = Options()
            chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
            service = Service(ProjectPaths.chromedriver_path.name)
            driver = webdriver.Chrome(service=service, options=chrome_options)

            return driver
        except Exception:
            raise AutomationError('failed to establish debug port connection')

    @classmethod
    def __run_script(cls, profile_name: str | int, script_config: ScriptConfig, driver: webdriver.Chrome) -> None:
        profile_name = str(profile_name)

        if not script_config.script_path.is_dir() or script_config.entry_file_path.is_file():
            raise FileNotFoundError('script directory or file not found')

        spec = importlib.util.spec_from_file_location(script_config['name'], script_config.entry_file_path)
        script_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(script_module)

        if hasattr(script_module, script_config.entry_function_name):
            function = getattr(script_module, script_config.entry_function_name)
            logger.debug(f'{profile_name} - calling function {script_config.entry_function_name} from sctipt "{script_config["human_name"]}"')
            function(driver)
        else:
            raise AutomationError('script entry function call error')

    @classmethod
    def execute_scripts(cls,
                        profile_name: str | int,
                        scripts_type: Literal['selenium', 'playwright', 'other'],
                        script_configs: list[ScriptConfig],
                        headless: bool = False) -> None:
        
        if scripts_type != 'selenium':
            raise AutomationError(f'execution of {scripts_type} scripts is not yet implemented') 

        browser = BrowserManager().launch_browser(profile_name=profile_name,
                                                  window_geometry=None,
                                                  debug=True,
                                                  headless=headless,
                                                  maximized=True)

        driver = cls.__establish_debug_port_connection(browser)

        for script_config in script_configs:
            try:
                logger.info(f'{profile_name} - launching script "{script_config.human_name}"')
                cls.__run_script(profile_name, script_config, driver)
            except FileNotFoundError as e:
                logger.error(f'{profile_name} - {e}')
            except AutomationError as e:
                logger.error(f'{profile_name} - {e}')
            except Exception as e:
                logger.error(f'{profile_name} - unexpected script "{script_config.human_name}" execution error')
                logger.debug(f'{profile_name} - unexpected script "{script_config.human_name}" execution error: {e}', exc_info=True)

