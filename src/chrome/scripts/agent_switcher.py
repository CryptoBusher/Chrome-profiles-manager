import os
import time
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

from .utils import js_click, close_all_other_tabs


def agent_switcher(user_name: str | int, script_data_path: str | Path, driver: webdriver.Chrome):
    with open(os.path.join(script_data_path, 'config.json'), 'r', encoding="utf-8") as f:
        config = json.load(f)

    working_tab = driver.current_window_handle
    wait = WebDriverWait(driver, 3)

    if config["run_delay_sec"]:
        logger.debug(f"{user_name} - waiting {config['run_delay_sec']} sec")
        time.sleep(config["run_delay_sec"])

    close_all_other_tabs(driver, working_tab)

    # General settings
    driver.get(f'chrome-extension://{config["extension_id"]}/options/index.html#/general')
    time.sleep(0.5)

    base_row_xpath = '(//aside//div[contains(@class, "row")])'

    for i in range(2):
        for index, setting in enumerate(config['general_settings']):
            checkbox_xpath = f'{base_row_xpath}[{index + 1}]//input[@type="checkbox"]'  # Xpath matches starts with index 1
            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))

            toggle_checkbox(driver, checkbox, setting["must_be_enabled"], working_tab)
            logger.debug(f'{user_name} - general setting "{setting["human_name"]}" adjusted to {setting["must_be_enabled"]}')

        time.sleep(0.5)

    # Generator settings
    driver.get(f'chrome-extension://{config["extension_id"]}/options/index.html#/generator')
    time.sleep(0.5)

    for i in range(2):
        for setting in config['generator_settings']:
            checkbox_xpath = f'//input[@id="{setting["id"]}"]'
            checkbox = wait.until(EC.element_to_be_clickable((By.XPATH, checkbox_xpath)))

            toggle_checkbox(driver, checkbox, setting["must_be_enabled"], working_tab)
            logger.debug(f'{user_name} - generator setting "{setting["human_name"]}" adjusted to {setting["must_be_enabled"]}')

        time.sleep(0.5)

    # Generate UA
    driver.get(f'chrome-extension://{config["extension_id"]}/popup/index.html')
    time.sleep(0.5)

    for i in range(2):
        generate_ua_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH, '//span[contains(text(), "Get new agent")]/..')))
        close_all_other_tabs(driver, working_tab)
        js_click(driver, generate_ua_btn)
        time.sleep(0.5)


def toggle_checkbox(
        driver: webdriver,
        checkbox: WebElement,
        must_be_enabled: bool = True,
        working_tab: str | None = None) -> None:
    if checkbox.is_selected() != must_be_enabled:
        if working_tab:
            close_all_other_tabs(driver, working_tab)

        js_click(driver, checkbox)
        time.sleep(0.1)
