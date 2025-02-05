import time
import os
import json

from selenium import webdriver
from selenium.webdriver.common.by import By
from loguru import logger

from .utils import js_click, close_all_other_tabs


def chrome_initial_setup(user_name: str | int, script_data_path: str, driver: webdriver.Chrome) -> None:
    with open(os.path.join(script_data_path, 'config.json'), 'r', encoding="utf-8") as f:
        config = json.load(f)

    working_tab = driver.current_window_handle

    if config["run_delay_sec"]:
        logger.debug(f"{user_name} - waiting {config['run_delay_sec']} sec")
        time.sleep(config["run_delay_sec"])

    close_all_other_tabs(driver, working_tab)

    turn_off_sync(user_name, driver, working_tab)
    turn_off_autofill(user_name, driver, working_tab)
    adjust_privacy_choices(user_name, driver, working_tab)
    adjust_tabs_memorizing(user_name, driver, working_tab, config["startup_settings"]["remember_tabs"])

    # TODO: fix this shit
    # if profile_name:
    #     set_profile_name(profile_name, driver, working_tab)


def dive_into_shadowroots(driver: webdriver.Chrome, host_tags):
    final_sr = driver
    for host in host_tags:
        element = final_sr.find_element(By.CSS_SELECTOR, host)
        shadow_root = element.shadow_root
        final_sr = shadow_root

    return final_sr


def turn_off_sync(name: str | int, driver: webdriver.Chrome, working_tab: str) -> None:
    try:
        host_tags = [
            "settings-ui",
            "settings-main",
            "settings-basic-page",
            "settings-people-page",
            "settings-sync-page",
            "settings-personalization-options"
        ]

        child_host_tags = [
            "settings-toggle-button#signinAllowedToggle",
            "settings-toggle-button#metricsReportingControl",
            "settings-toggle-button#urlCollectionToggle",
            "settings-toggle-button#spellCheckControl",
            "settings-toggle-button#searchSuggestToggle"
        ]

        driver.get("chrome://settings/syncSetup")
        time.sleep(0.5)

        mother_sr = dive_into_shadowroots(driver, host_tags)
        for child_host in child_host_tags:
            element = mother_sr.find_element(By.CSS_SELECTOR, child_host)
            final_sr = element.shadow_root

            toggle = final_sr.find_element(By.CSS_SELECTOR, 'cr-toggle')
            if toggle.get_attribute('aria-pressed') == 'true':
                close_all_other_tabs(driver, working_tab)
                js_click(driver, toggle)

        logger.info(f"✅  {name} - синхронизация выключена")
    except Exception as e:
        logger.error(f"⛔  {name} - не удалось выключить синхронизацию")
        logger.debug(f"{name} - не удалось выключить синхронизацию, причина: {e}")


def set_profile_name(name: str | int, driver: webdriver.Chrome, working_tab: str) -> None:
    try:
        host_tags = [
            "settings-ui",
            "settings-main",
            "settings-basic-page",
            "settings-people-page",
            "settings-manage-profile",
            # "cr-input"
        ]

        driver.get("chrome://settings/manageProfile")
        time.sleep(0.5)

        final_sr = dive_into_shadowroots(driver, host_tags)
        click_to_save_element = final_sr.find_element(By.CSS_SELECTOR, 'h1')
        # driver.execute_script("arguments[0].style.border='3px solid red'", click_to_save_element)

        child_host_tag = final_sr.find_element(By.CSS_SELECTOR, 'cr-input')
        final_sr = child_host_tag.shadow_root

        name_input = final_sr.find_element(By.CSS_SELECTOR, 'input')
        close_all_other_tabs(driver, working_tab)
        name_input.clear()
        name_input.send_keys(name)

        close_all_other_tabs(driver, working_tab)
        click_to_save_element.click()
        time.sleep(0.4)

        logger.info(f'✅  {name} - имя профиля установлено')
    except Exception as e:
        logger.error(f"⛔  {name} - не удалось установить имя профиля")
        logger.debug(f"{name} - не удалось установить имя профиля, причина: {e}")


def turn_off_autofill(name: str | int, driver: webdriver.Chrome, working_tab: str) -> None:
    try:
        host_tags = [
            "password-manager-app",
            "settings-section"
        ]

        driver.get('chrome://password-manager/settings')
        time.sleep(0.5)

        final_sr = dive_into_shadowroots(driver, host_tags)

        pass_toggle_host = final_sr.find_element(By.ID, 'passwordToggle')
        sr = pass_toggle_host.shadow_root
        pass_toggle = sr.find_element(By.CSS_SELECTOR, 'cr-toggle')
        if pass_toggle.get_attribute('aria-pressed') == 'true':
            close_all_other_tabs(driver, working_tab)
            js_click(driver, pass_toggle)
        
        auto_sign_in_toggle_host = final_sr.find_element(By.ID, 'autosigninToggle')
        sr = auto_sign_in_toggle_host.shadow_root
        auto_sign_in_toggle = sr.find_element(By.CSS_SELECTOR, 'cr-toggle')
        if auto_sign_in_toggle.get_attribute('aria-pressed') == 'true':
            close_all_other_tabs(driver, working_tab)
            js_click(driver, auto_sign_in_toggle)
        
        logger.info(f"✅  {name} - автозаполнение паролей отключено")
    except Exception as e:
        logger.error(f"⛔  {name} - не удалось отключить автозаполнение паролей")
        logger.debug(f"{name} - не удалось отключить автозаполнение паролей, причина: {e}")


def adjust_privacy_choices(name: str | int, driver: webdriver.Chrome, working_tab: str) -> None:
    try:
        host_tags = [
            "settings-ui",
            "settings-main",
            "settings-basic-page",
            "settings-privacy-page",
            "settings-privacy-guide-dialog",
            "settings-privacy-guide-page"
        ]

        driver.get('chrome://settings/privacy/guide?step=welcome')
        time.sleep(0.5)

        unique_sr = dive_into_shadowroots(driver, host_tags)

        welcome_fragment_element = unique_sr.find_element(By.CSS_SELECTOR, 'privacy-guide-welcome-fragment')
        welcome_fragment_sr = welcome_fragment_element.shadow_root
        start_button = welcome_fragment_sr.find_element(By.ID, 'startButton')
        close_all_other_tabs(driver, working_tab)
        js_click(driver, start_button)

        host_tags = [
            'privacy-guide-msbb-fragment',
            'settings-toggle-button'
        ]

        searches_and_browser_better_sr = dive_into_shadowroots(unique_sr, host_tags)
        searches_and_browser_better_toggle = searches_and_browser_better_sr.find_element(By.ID, 'control')
        if searches_and_browser_better_toggle.get_attribute('aria-pressed') == 'true':
            close_all_other_tabs(driver, working_tab)
            js_click(driver, searches_and_browser_better_toggle)

        next_button = unique_sr.find_element(By.ID, 'nextButton')
        next_button.click()

        host_tags = [
            'privacy-guide-safe-browsing-fragment',
            'settings-collapse-radio-button#safeBrowsingRadioStandard'
        ]

        safe_browsing_sr = dive_into_shadowroots(unique_sr, host_tags)
        standard_mode_radio_btn = safe_browsing_sr.find_element(By.ID, 'button')
        if standard_mode_radio_btn.get_attribute('aria-checked') == 'false': 
            safe_browsing_btn = safe_browsing_sr.find_element(By.ID, 'radioCollapse')
            close_all_other_tabs(driver, working_tab)
            js_click(driver, safe_browsing_btn)

        next_button = unique_sr.find_element(By.ID, 'nextButton')
        close_all_other_tabs(driver, working_tab)
        js_click(driver, next_button)

        host_tags = [
            'privacy-guide-cookies-fragment',
            'settings-collapse-radio-button#block3PIncognito'
        ]

        block_cookies_in_incognito_sr = dive_into_shadowroots(unique_sr, host_tags)
        block_cookies_in_incognito_radio_btn = block_cookies_in_incognito_sr.find_element(By.ID, 'button')
        if block_cookies_in_incognito_radio_btn.get_attribute('aria-checked') == 'false': 
            block_cookies_in_incognito_btn = block_cookies_in_incognito_sr.find_element(By.ID, 'radioCollapse')
            close_all_other_tabs(driver, working_tab)
            js_click(driver, block_cookies_in_incognito_btn)

        next_button = unique_sr.find_element(By.ID, 'nextButton')
        close_all_other_tabs(driver, working_tab)
        js_click(driver, next_button)

        finish_fragment_element = unique_sr.find_element(By.CSS_SELECTOR, 'privacy-guide-completion-fragment')
        finish_fragment_sr = finish_fragment_element.shadow_root
        done_button = finish_fragment_sr.find_element(By.ID, 'leaveButton')
        close_all_other_tabs(driver, working_tab)
        js_click(driver, done_button)

        logger.info(f"✅  {name} - настройки приватности обновлены")
    except Exception as e:
        logger.error(f"⛔  {name} - не удалось обновить настройки приватности")
        logger.debug(f"{name} - не удалось обновить настройки приватности, причина: {e}")


def adjust_tabs_memorizing(name: str | int, driver: webdriver.Chrome, working_tab: str, remember: bool = True) -> None:
    try:
        host_tags = [
            "settings-ui",
            "settings-main",
            "settings-basic-page",
            "settings-on-startup-page"
        ]

        driver.get('chrome://settings/onStartup')
        time.sleep(0.5)

        final_sr = dive_into_shadowroots(driver, host_tags)

        if remember:
            chosen_option = final_sr.find_element(By.CSS_SELECTOR, f"controlled-radio-button[name='1']")
        else:
            chosen_option = final_sr.find_element(By.CSS_SELECTOR, f"controlled-radio-button[name='5']")

        close_all_other_tabs(driver, working_tab)
        js_click(driver, chosen_option)

        logger.info(f"✅  {name} - настройки запоминания вкладок обновлены")
    except Exception as e:
        logger.error(f"⛔  {name} - не удалось обновить настройки запоминания вкладок")
        logger.debug(f"{name} - не удалось обновить настройки запоминания вкладок, причина: {e}")
