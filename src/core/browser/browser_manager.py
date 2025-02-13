import os
import socket
import math
import subprocess
from pathlib import Path
from dataclasses import dataclass

from selenium import webdriver

from src.core.profile.profile_manager import ProfileManager
from src.utils.constants import ProjectPaths
from src.exceptions import NoFreePortsError


@dataclass
class Browser:
    profile_name: str
    process: subprocess.Popen[bytes]
    debug_port: int | None = None

@dataclass
class Chromium:
    profile_name: str
    driver: webdriver.Chrome


class BrowserManager:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.active_browsers: list[Browser] = []
            self.active_chromedrivers: list[Chromium] = []
            self.busy_debug_ports: list[int] = []
            self.__class__._initialized = True

    def __create_launch_flags(self,
                              profile_name: str | int,
                              window_geometry: dict | None = None,
                              debug: bool = False,
                              headless: bool = False,
                              maximized: bool = False) -> tuple[list[str], int]:

        profile_path = ProjectPaths.profiles_path / str(profile_name)
        profile_extensions_path: Path = profile_path / "Default" / "Extensions"
        profile_welcome_page_path: Path = ProfileManager.get_profile_welcome_page_path(profile_name)

        all_extensions = []
        for ext_id in os.listdir(profile_extensions_path):
            versions_dir = profile_extensions_path / ext_id
            if os.path.isdir(versions_dir):
                for version in os.listdir(versions_dir):
                    version_path = versions_dir / version
                    if os.path.isfile(os.path.join(version_path, "manifest.json")):
                        all_extensions.append(version_path.name)

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

        if window_geometry:
            flags.append(f'--window-size={window_geometry["w"]},{window_geometry["h"]}')
            flags.append(f'--window-position={window_geometry["x"]},{window_geometry["y"]}')
        elif maximized:
            flags.append("--start-maximized")

        debug_port = None
        if debug:
            debug_port = self.__select_free_port()
            if not debug_port:
                raise NoFreePortsError()

            flags.append(f'--remote-debugging-port={debug_port}')

        return flags, debug_port

    def __select_free_port(self, start_port=9222, max_port=9300) -> int | None:
        for port in range(start_port, max_port):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                result = s.connect_ex(('127.0.0.1', port))
                if result != 0 and port not in self.busy_debug_ports:
                    self.busy_debug_ports.append(port)
                    return port

        return None

    @staticmethod
    def calculate_window_geometry(windows_amount: int,
                                  window_index: int,
                                  working_area_width_px: int = 1920,
                                  working_area_height_px: int = 1080,
                                  min_width_px=300,
                                  min_height_px=200) -> dict[str, int]:

        cols = math.ceil(math.sqrt(windows_amount))
        rows = math.ceil(windows_amount / cols)

        while cols * min_width_px > working_area_width_px or rows * min_height_px > working_area_height_px:
            cols -= 1
            rows = math.ceil(windows_amount / cols)

        window_width = working_area_width_px // cols
        window_height = working_area_height_px // rows

        if window_width < min_width_px:
            window_width = min_width_px
        if window_height < min_height_px:
            window_height = min_height_px

        all_window_positions = []
        for i in range(windows_amount):
            row = i // cols
            col = i % cols

            x = col * window_width
            y = row * window_height

            all_window_positions.append({
                'x': x,
                'y': y,
                'w': window_width,
                'h': window_height
            })

        return all_window_positions[window_index]

    def __get_browser(self, profile_name: str | int) -> Browser | None:
        return next((b for b in self.active_browsers if b.profile_name == profile_name), None)
    
    def __get_chromium(self, profile_name: str | int) -> Chromium | None:
        return next((c for c in self.active_chromedrivers if c.profile_name == profile_name), None)

    def launch_browser(self,
                       profile_name: str | int,
                       window_geometry: dict | None = None,
                       debug: bool = False,
                       headless: bool = False,
                       maximized: bool = False) -> Browser:
        
        profile_name = str(profile_name)
        launch_args, debug_port = self.__create_launch_flags(profile_name,
                                                             window_geometry,
                                                             debug,
                                                             headless,
                                                             maximized)

        with open(os.devnull, 'w') as devnull:  # to avoid Chrome log spam
            chrome_process = subprocess.Popen([ProjectPaths.chrome_path, *launch_args],
                                              stdout=devnull,
                                              stderr=devnull)

        browser = Browser(
            profile_name,
            chrome_process,
            debug_port
        )
        self.active_browsers.append(browser)

        return browser
    
    def kill_browser(self, profile_name: str | int):
        profile_name = str(profile_name)
        browser = self.__get_browser(profile_name)
        chromium = self.__get_chromium(profile_name)

        if chromium:
            if chromium.driver:
                chromium.driver.close()
                chromium.driver.quit()
                
            self.active_chromedrivers = [c for c in self.active_chromedrivers if c.profile_name != profile_name]

        if browser:
            port_used = browser.debug_port
            if browser.process:
                browser.process.terminate()
                browser.process.wait()

            self.active_browsers = [b for b in self.active_browsers if b.profile_name != profile_name]

            if port_used in  self.busy_debug_ports:
                self.busy_debug_ports.remove(port_used)
