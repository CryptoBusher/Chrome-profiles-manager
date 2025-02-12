import re
import json

import questionary
from loguru import logger

from .base_cli import BaseCli
from src.utils.constants import ProjectPaths
from src.cli.profiles_cli import ProfilesCli
from src.core.extension.extension_manager import ExtensionManager


class AutomationCli(BaseCli):
    @classmethod
    def show(cls):
        activity_options = {
            'run_selenium_scripts': '',
            'run_playwright_scripts': '',
            'run_other_scripts': '',
            'back_to_start': ''
        }