"""Shared pytest fixtures: browser setup/cleanup and screenshot evidence."""
import pathlib  # object-oriented file paths

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options  # Chrome startup settings

import config  # our own settings file (URLs, credentials, HEADLESS flag)

# Screenshots are saved in an "evidence" folder next to this file.
EVIDENCE_DIR = pathlib.Path(__file__).parent / "evidence"
# Create the folder if it is missing; exist_ok avoids an error if it already exists.
EVIDENCE_DIR.mkdir(exist_ok=True)


# A fixture is reusable setup/teardown. Any test with a parameter named
# "driver" automatically receives the browser created here.
@pytest.fixture
def driver():
    """Launch Chrome before each test and always close it afterwards."""
    opts = Options()
    # Fixed window size so the page layout is the same on every run.
    opts.add_argument("--window-size=1366,900")
    # Hide the browser window when GABS_HEADLESS=1 (useful for CI / faster runs).
    if config.HEADLESS:
        opts.add_argument("--headless=new")
    drv = webdriver.Chrome(options=opts)  # Selenium Manager fetches chromedriver
    yield drv   # the test runs here, using this browser
    drv.quit()  # teardown: runs even if the test failed, so no stray Chrome windows


# hookwrapper=True lets this function run around pytest's own report creation,
# so we can read the result (outcome) after pytest has built it.
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Save a screenshot of every test's final state (PASS or FAIL)."""
    outcome = yield                  # let pytest create the report first
    report = outcome.get_result()    # the finished report for this test phase
    # A test has setup / call / teardown phases; "call" is the test body itself.
    if report.when == "call":
        # Get the browser if this test used the "driver" fixture (None otherwise).
        drv = item.funcargs.get("driver")
        if drv is not None:
            status = "PASS" if report.passed else "FAIL"
            # File name example: test_tc01_valid_login_PASS.png
            drv.save_screenshot(str(EVIDENCE_DIR / f"{item.name}_{status}.png"))
