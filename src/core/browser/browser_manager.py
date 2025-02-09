import os
import socket
import subprocess
from pathlib import Path

from loguru import logger

from src.utils.constants import ProjectPaths
from src.utils.helpers import set_comments_for_users


class BrowserManager:
    def __init__(self):
        self.active_browsers = {}
        self.busy_debug_ports = []

    def __create_launch_flags(self,
                              profile_name: str | int,
                              window_params: dict | None = None,
                              debug: bool = False,
                              headless: bool = False,
                              maximized: bool = False) -> list[str]:
            
            profile_path: Path = ProjectPaths.profiles_path / str(profile_name)
            profile_extensions_path: Path = profile_path / "Default" / "Extensions"
            profile_welcome_page_path: Path = self.__get_profile_welcome_page_path(profile_name)

            all_extensions = []
            for ext_id in os.listdir(profile_extensions_path):
                versions_dir = profile_extensions_path / ext_id
                if os.path.isdir(versions_dir):
                    for version in os.listdir(versions_dir):
                        version_path = versions_dir / version
                        if os.path.isfile(os.path.join(version_path, "manifest.json")):
                            all_extensions.append(version_path)

            load_extensions_arg = ",".join(all_extensions)

            flags = [
                f"--user-data-dir={ProjectPaths.profiles_path / str(profile_name)}",
                f"--profile-directory=Default",
                "--no-first-run",
                f"--load-extension={load_extensions_arg}",
                f"file:///{profile_welcome_page_path}",
                "--no-sync",
                "--disable-features=IdentityConsistency",
                "--disable-accounts-receiver",
                "--headless" if headless else None
            ]

            flags = [i for i in flags if i is not None]

            if window_params:
                flags.append(f'--window-size={window_params["width"]},{window_params["height"]}')
                flags.append(f'--window-position={window_params["x"]},{window_params["y"]}')
            elif maximized:
                flags.append("--start-maximized")

            if debug:
                free_port = self.__find_free_port()
                if not free_port:
                    raise Exception(_("missing_free_ports"))
                
                self.active_browsers.setdefault(profile_name, {})['debug_port'] = free_port
                flags.append(f'--remote-debugging-port={free_port}')

            return flags


    def __find_free_port(self, start_port=9222, max_port=9300) -> int | None:
        for port in range(start_port, max_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                if result != 0 and port not in self.busy_debug_ports:
                    self.busy_debug_ports.append(port)
                    return port
                
        return None
                
    @staticmethod
    def __get_profile_welcome_page_path(profile_name: str | int) -> Path:
        template_welcome_page_path = ProjectPaths.root_path / "src" / "assets" / "welcome_page_template.html"
        profile_welcome_page_path = ProjectPaths.profiles_path / str(profile_name) / "Default" / "welcome.html"

        with open(template_welcome_page_path, 'r') as template_file:
            template_content = template_file.read()

        profile_page_content = template_content.replace("{{ profile_name }}", profile_name)

        with open(profile_welcome_page_path, 'w') as profile_page_file:
            profile_page_file.write(profile_page_content)

        return profile_welcome_page_path


    def create_profile(self, profile_name: str | int) -> None:
        try:
            user_path: Path = ProjectPaths.profiles_path / str(profile_name)
            user_extensions_path: Path = user_path / "Default" / "Extensions"

            os.makedirs(user_extensions_path)  # can trigger FileExistsError
            set_comments_for_users([profile_name], "")
            logger.success(f'{profile_name} - {_("profile_created")}')

        except FileExistsError:
            logger.warning(f'{profile_name} - {_("profile_already_exists")}')
        except Exception as e:
            logger.error(f'{profile_name} - {_("failed_to_create_profile")}')
            logger.debug(f'{profile_name} - failed to create profile, reason: {e}', exc_info=True)

    def launch_profile(self,
                       profile_name: str | int,
                       window_params: dict | None = None,
                       debug: bool = False,
                       headless: bool = False,
                       maximized: bool = False) -> None:
        try:
            launch_args = self.__create_launch_flags(profile_name,
                                                     window_params,
                                                     debug,
                                                     headless,
                                                     maximized)

            with open(os.devnull, 'w') as devnull:  # to avoid Chrome log spam
                chrome_process = subprocess.Popen([ProjectPaths.chrome_path, *launch_args], stdout=devnull, stderr=devnull)
            
            self.active_browsers.setdefault(profile_name, {})['process'] = chrome_process
            logger.success(f'{profile_name} - {_("profile_launched")}')
        
        except Exception as e:
            logger.error(f'{profile_name} - {_("failed_to_launch_profile")}')
            logger.debug(f'{profile_name} - failed to launch profile, reason: {e}', exc_info=True)
