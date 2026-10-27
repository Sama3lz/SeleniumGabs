"""Central settings for the GABS Bakeshop Selenium practicum.

Credentials are NOT stored in the code. Set them as environment variables
before running (see README.md).
"""
import os  # needed for os.getenv(), which reads environment variables

# Default target is the local XAMPP copy. Point GABS_BASE_URL elsewhere to test
# another deployment, e.g. https://gabsbakeshop.lsu-source.org
# .rstrip("/") removes a trailing slash so URLs built from it never contain "//".
BASE_URL = os.getenv("GABS_BASE_URL", "http://localhost/GABS/public").rstrip("/")
# Login page address; built from BASE_URL unless GABS_LOGIN_URL overrides it.
LOGIN_URL = os.getenv("GABS_LOGIN_URL", f"{BASE_URL}/index.php?/auth/login")

# Administrator account (TC-01, TC-03, TC-04, TC-05, TC-09, TC-10, TC-11, TC-12)
# Defaults are empty strings so no real password is ever stored in the code.
ADMIN_USER = os.getenv("GABS_ADMIN_USER", "")
ADMIN_PASS = os.getenv("GABS_ADMIN_PASS", "")

# Branch owner account (TC-06, TC-07, TC-08)
BRANCH_USER = os.getenv("GABS_BRANCH_USER", "")
BRANCH_PASS = os.getenv("GABS_BRANCH_PASS", "")

# Maximum seconds an explicit wait (WebDriverWait) polls before timing out.
WAIT_SECONDS = 10
# True only when GABS_HEADLESS=1; makes Chrome run without a visible window.
HEADLESS = os.getenv("GABS_HEADLESS", "0") == "1"
