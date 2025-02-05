import os
import time
import json
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from loguru import logger

from .utils import js_click, close_all_other_tabs, get_txt_line_by_user_name, is_twelve_words_string


def rabby_import(user_name: str | int, script_data_path: str | Path, driver: webdriver.Chrome):
    with open(os.path.join(script_data_path, 'config.json'), 'r', encoding="utf-8") as f:
        config = json.load(f)

    secrets_file_path = os.path.join(script_data_path, 'secrets.txt')
    user_data = get_txt_line_by_user_name(user_name, secrets_file_path)
    if not user_data:
        raise Exception('приватный ключ или сид фраза не найдены')
    _, secret, password = user_data.split('|')

    is_seed_phrase = is_twelve_words_string(secret)
    working_tab = driver.current_window_handle
    wait = WebDriverWait(driver, 5)

    if config["run_delay_sec"]:
        logger.debug(f"{user_name} - waiting {config['run_delay_sec']} sec")
        time.sleep(config["run_delay_sec"])

    close_all_other_tabs(driver, working_tab)

    driver.get(f'chrome-extension://{config["extension_id"]}/index.html#/new-user/guide')
    import_btn_xpath = "//button/span[contains(text(),'I already have an address')]/.."
    import_btn = wait.until(EC.element_to_be_clickable((By.XPATH, import_btn_xpath)))
    js_click(driver, import_btn)

    if is_seed_phrase:
        import_seed_btn_xpath = "//div[contains(text(),'Seed Phrase')]"
        import_seed_btn = wait.until(EC.element_to_be_clickable((By.XPATH, import_seed_btn_xpath)))
        js_click(driver, import_seed_btn)

        word_input_base_xpath = "(//div[contains(@class, 'is-mnemonics-input')]//input)"
        for i, word in enumerate(secret.split()):
            word_input = wait.until(EC.presence_of_element_located((By.XPATH, word_input_base_xpath + f'[{i+1}]')))
            word_input.send_keys(word)
    else:
        import_private_key_btn_xpath = "//div[contains(text(),'Private Key')]"
        import_private_key_btn = wait.until(EC.element_to_be_clickable((By.XPATH, import_private_key_btn_xpath)))
        js_click(driver, import_private_key_btn)

        private_key_input_xpath = "//input[@id='privateKey']"
        wait.until(EC.presence_of_element_located((By.XPATH, private_key_input_xpath))).send_keys(secret)

    confirm_btn_xpath = "//button/span[contains(text(),'Confirm')]/.."
    confirm_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_btn_xpath)))
    js_click(driver, confirm_btn)

    password_input_xpath = "//input[@id='password']"
    wait.until(EC.presence_of_element_located((By.XPATH, password_input_xpath))).send_keys(password)
    confirm_password_input_xpath = "//input[@id='confirmPassword']"
    wait.until(EC.presence_of_element_located((By.XPATH, confirm_password_input_xpath))).send_keys(password)

    confirm_import_btn_xpath = "//span[contains(text(),'Confirm')]/.."
    confirm_import_btn = wait.until(EC.element_to_be_clickable((By.XPATH, confirm_import_btn_xpath)))
    js_click(driver, confirm_import_btn)

    if is_seed_phrase:
        import_selected_secrets_btn_xpath = "//button/span[contains(text(),'Import')]/.."
        import_selected_secrets_btn = wait.until(EC.element_to_be_clickable((By.XPATH, import_selected_secrets_btn_xpath)))
        js_click(driver, import_selected_secrets_btn)

    time.sleep(0.2)