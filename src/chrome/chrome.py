import subprocess
import time
import socket
import os

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from loguru import logger

from src.utils.helpers import set_comments_for_users
from src.utils.constants import *
from .scripts import *


class Chrome:
    def __init__(self):
        self.debug_ports = {}
        self.chosen_debug_ports = []

        self.scripts = {
            'chrome_initial_setup': {
                'human_name': 'Первичная настройка Chrome',
                'method': chrome_initial_setup,
            },
            'omega_proxy_setup': {
                'human_name': 'Настройка Omega Proxy',
                'method': omega_proxy_setup
            },
            'agent_switcher': {
                'human_name': 'Настройка Agent Switcher',
                'method': agent_switcher
            },
            'rabby_import': {
                'human_name': 'Импорт Rabby Wallet',
                'method': rabby_import
            }
        }

    def create_new_user(self, user_name: str | int) -> None:
        try:
            user_path = self.__get_user_path(user_name)
            default_profile_extensions_path = os.path.join(user_path, USER_DEFAULT_PROFILE_NAME, "Extensions")

            os.makedirs(default_profile_extensions_path)  # can trigger FileExistsError
            set_comments_for_users([user_name], "")

            logger.info(f'✅  {user_name} - юзер создан')
        except FileExistsError:
            logger.warning(f'⚠️ {user_name} - юзер уже существует')
        except Exception as e:
            logger.error(f'⛔  {user_name} - не удалось создать юзера')
            logger.debug(f'{user_name} - не удалось создать юзера, причина: {e}')

    def launch_user(self,
                    user_name: str | int,
                    position: dict | None = None,
                    debug=False,
                    headless: bool = False,
                    maximized: bool = False) -> subprocess.Popen | None:
        try:
            launch_args = self.__create_launch_flags(user_name,
                                                     position,
                                                     debug,
                                                     headless,
                                                     maximized)

            with open(os.devnull, 'w') as devnull:  # to avoid Chrome log spam
                chrome_process = subprocess.Popen([CHROME_PATH, *launch_args], stdout=devnull, stderr=devnull)

            logger.info(f'✅  {user_name} - дефолтный профиль запущен')

            return chrome_process
        except Exception as e:
            logger.error(f'⛔  {user_name} - не удалось запустить дефолтный профиль')
            logger.debug(f'{user_name} - не удалось запустить дефолтный профиль, причина: {e}')

    def run_scripts(self,
                    user_name: str | int,
                    scripts_list: list[str],
                    headless: bool = False) -> None:
        try:
            chrome_process = self.launch_user(user_name,
                                              position=None,
                                              debug=True,
                                              headless=headless,
                                              maximized=True)
            if not chrome_process:
                raise Exception('не удалось запустить браузер')

            time.sleep(1)

            logger.debug(f'{user_name} - подключаюсь к порту {self.debug_ports[user_name]}')
            driver = self.__establish_debug_port_connection(user_name)
            logger.debug(f'{user_name} - соединение установлено')

            logger.debug(f'{user_name} - скрипты для прогона: {scripts_list}')
            for script in scripts_list:
                try:
                    human_name = self.scripts[script]['human_name']
                    logger.info(f'ℹ️ {user_name} - запускаю скрипт "{human_name}"')
                    script_data_path = os.path.join(DATA_PATH, 'scripts', "chrome", script)
                    self.scripts[script]['method'](
                        user_name,
                        script_data_path,
                        driver
                    )
                    logger.info(f'✅  {user_name} - скрипт "{human_name}" выполнен')
                except Exception as e:
                    human_name = self.scripts[script]['human_name']
                    logger.error(f'⛔  {user_name} - скрипт "{human_name}" завершен с ошибкой')
                    logger.debug(f'{user_name} - скрипт "{human_name}" завершен с ошибкой, причина: {e}')

        except Exception as e:
            logger.error(f'⛔  {user_name} - не удалось запустить дефолтный профиль, выполнение скриптов прервано')
            logger.debug(f'{user_name} - не удалось запустить дефолтный профиль, причина: {e}')
            return

        time.sleep(1)

        try:
            driver.quit()
            chrome_process.terminate()
            chrome_process.wait()
            logger.debug(f'{user_name} - дефолтный профиль закрыт')
        except Exception as e:
            logger.error(f'⛔  {user_name} - не удалось закрыть дефолтный профиль')
            logger.debug(f'{user_name} - не удалось закрыть дефолтный профиль, причина: {e}')

    def __establish_debug_port_connection(self, user_name) -> webdriver.Chrome:
        debug_port = self.debug_ports[user_name]

        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{debug_port}")
        service = Service(CHROME_DRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)

        return driver

    def __create_launch_flags(self,
                              user_name: str | int,
                              position: dict | None = None,
                              debug: bool = False,
                              headless: bool = False,
                              maximized: bool = False) -> list[str]:
        user_path = self.__get_user_path(user_name)
        user_extensions_path = os.path.join(user_path, USER_DEFAULT_PROFILE_NAME, "Extensions")
        user_welcome_page_path = self.__get_default_profile_welcome_page_path(user_name)

        all_extensions = []
        for ext_id in os.listdir(user_extensions_path):
            versions_dir = os.path.join(user_extensions_path, ext_id)
            if os.path.isdir(versions_dir):
                for version in os.listdir(versions_dir):
                    version_path = os.path.join(versions_dir, version)
                    if os.path.isfile(os.path.join(version_path, "manifest.json")):
                        all_extensions.append(version_path)

        load_arg = ",".join(all_extensions)

        flags = [
            f"--user-data-dir={os.path.join(USERS_PATH, user_name)}",
            f"--profile-directory={USER_DEFAULT_PROFILE_NAME}",
            "--no-first-run",
            f"--load-extension={load_arg}",
            f"file:///{user_welcome_page_path}",
            "--no-sync",
            "--disable-features=IdentityConsistency",
            "--disable-accounts-receiver",
            "--headless" if headless else None
        ]

        flags = [i for i in flags if i is not None]

        if position:
            flags.append(f'--window-size={position["width"]},{position["height"]}')
            flags.append(f'--window-position={position["x"]},{position["y"]}')
        elif maximized:
            flags.append("--start-maximized")

        if debug:
            free_port = self.__find_free_port()
            if free_port:
                self.debug_ports[user_name] = free_port
                flags.append(f'--remote-debugging-port={free_port}')
            else:
                logger.warning(f'⚠️ {user_name} - отсутствуют свободные порты для подключения')

        return flags

    @staticmethod
    def __get_user_path(user_name: str) -> str:
        return os.path.join(USERS_PATH, user_name)

    @staticmethod
    def __get_default_profile_welcome_page_path(user_name: str | int) -> str | Path:
        profile_welcome_page_path = USERS_PATH / str(user_name) / str(USER_DEFAULT_PROFILE_NAME) / f"welcome.html"

        with open(PROFILE_WELCOME_PAGE_TEMPLATE_PATH, 'r') as template_file:
            template_content = template_file.read()

        profile_page_content = template_content.replace("{{ user_name }}", user_name)

        with open(profile_welcome_page_path, 'w') as profile_page_file:
            profile_page_file.write(profile_page_content)

        return profile_welcome_page_path

    def __find_free_port(self, start_port=9222, max_port=9300) -> int | None:
        for port in range(start_port, max_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                if result != 0 and port not in self.chosen_debug_ports:
                    self.chosen_debug_ports.append(port)
                    return port

        return None
