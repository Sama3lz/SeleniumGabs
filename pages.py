"""Reusable helpers (a light page-object layer) for the GABS tests."""
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By  # ways to locate elements (ID, CSS, XPATH...)
from selenium.webdriver.support import expected_conditions as EC  # ready-made wait conditions
from selenium.webdriver.support.ui import WebDriverWait  # explicit-wait helper

import config


def wait(driver, seconds=config.WAIT_SECONDS):
    """Build a WebDriverWait with the project's default timeout."""
    # A form submit reloads the page; ignore elements that go stale mid-wait.
    return WebDriverWait(driver, seconds, ignored_exceptions=(StaleElementReferenceException,))


def open_login(driver):
    """Go to the login page and wait until the username box is visible."""
    driver.get(config.LOGIN_URL)
    wait(driver).until(EC.visibility_of_element_located((By.ID, "username_or_email")))


def login(driver, username, password):
    """Fill in and submit the login form."""
    open_login(driver)
    # Type the credentials into the two fields, found by their HTML ids.
    driver.find_element(By.ID, "username_or_email").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    # Click the login button (CSS selector: <button class="login-btn">).
    driver.find_element(By.CSS_SELECTOR, "button.login-btn").click()


def login_succeeded(driver):
    """True once we have left the login page."""
    try:
        # Success means the URL no longer contains "auth/login".
        wait(driver).until(lambda d: "auth/login" not in d.current_url)
        return True
    except TimeoutException:
        # Still on the login page after the timeout, so the login failed.
        return False


def main_nav_link(driver, text):
    """The top-menu link whose visible text is exactly `text`."""
    # XPath: an <a> inside the #main-nav-links div, matched on its trimmed text.
    xpath = f"//div[@id='main-nav-links']/a[normalize-space()='{text}']"
    return wait(driver).until(EC.element_to_be_clickable((By.XPATH, xpath)))


def click_main_nav(driver, text):
    """Click a top-menu link by its visible text (e.g. "Inventory")."""
    main_nav_link(driver, text).click()


def heading(driver):
    """Text of the page's <h1>."""
    return wait(driver).until(
        EC.visibility_of_element_located((By.TAG_NAME, "h1"))).text


def page_text(driver):
    """All visible text of the page, lower-cased for case-insensitive checks."""
    body = wait(driver).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
    return body.text.lower()


def wait_for_text(driver, text):
    """Wait until `text` (case-insensitive) is anywhere on the page."""
    wait(driver).until(lambda d: text.lower() in page_text(d))
