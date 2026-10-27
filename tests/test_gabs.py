"""Selenium WebDriver practicum - Gab's Bakeshop.

Test IDs match the Test Case Table (TC-01 ... TC-12). Every test has at least
one assertion and uses explicit waits (no time.sleep).

Coverage
  Authentication ............ TC-01 (valid), TC-02 (invalid)
  Navigation / page checks .. TC-03 (dashboard), TC-04 (inventory), TC-07, TC-08, TC-09
  Form input & validation ... TC-11 (empty data), TC-12 (valid data)
  Data operation ............ TC-12 (add a product, verify it in the list, delete it)
  System-specific ........... TC-05 (search), TC-06 (place order), TC-10 (logout / protected page)
"""
import time  # used only to build unique values (timestamps), never to pause

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import config  # URLs and credentials
import pages   # reusable helper functions (login, waits, navigation)

# Skip markers: a test with @need_admin is skipped (not failed) when the admin
# credentials environment variables are not set. Same idea for the branch account.
need_admin = pytest.mark.skipif(not (config.ADMIN_USER and config.ADMIN_PASS),
                                reason="GABS_ADMIN_USER / GABS_ADMIN_PASS not set")
need_branch = pytest.mark.skipif(not (config.BRANCH_USER and config.BRANCH_PASS),
                                 reason="GABS_BRANCH_USER / GABS_BRANCH_PASS not set")


def admin_login(driver):
    """Log in as administrator and fail clearly if it does not work."""
    pages.login(driver, config.ADMIN_USER, config.ADMIN_PASS)
    assert pages.login_succeeded(driver), "Admin login did not leave the login page"


def branch_login(driver):
    """Log in as branch owner and fail clearly if it does not work."""
    pages.login(driver, config.BRANCH_USER, config.BRANCH_PASS)
    assert pages.login_succeeded(driver), "Branch login did not leave the login page"


def open_product_inventory(driver):
    """Inventory -> Product Inventory sub-menu."""
    pages.click_main_nav(driver, "Inventory")  # open the Inventory section
    # Wait for the sub-menu link to the product inventory page, then click it.
    sub = pages.wait(driver).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "nav.sub-navbar a[href*='product-inventory']")))
    sub.click()
    # The page is ready once the product table is visible.
    pages.wait(driver).until(EC.visibility_of_element_located((By.ID, "product-table")))


# ---------------- Authentication ----------------
@need_admin
def test_tc01_valid_login(driver):
    # Log in with the correct admin credentials.
    pages.login(driver, config.ADMIN_USER, config.ADMIN_PASS)
    # Expect to leave the login page and land on the dashboard with its welcome heading.
    assert pages.login_succeeded(driver)
    assert "dashboard" in driver.current_url
    assert "Welcome to Gab's Bakeshop" in pages.heading(driver)


def test_tc02_invalid_login(driver):
    # Try credentials that do not exist.
    pages.login(driver, "invalid_user@example.com", "WrongPassword!123")
    # Wait for the red error message to appear.
    error = pages.wait(driver).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "p.error-message")))
    assert error.text.strip() == "Invalid username/email or password."
    assert "auth/login" in driver.current_url  # still on the login page


# ---------------- Dashboard / navigation ----------------
@need_admin
def test_tc03_view_dashboard(driver):
    admin_login(driver)
    assert "Welcome to Gab's Bakeshop" in pages.heading(driver)
    # The dashboard should show the sales chart/section title.
    assert "Monthly Sales" in pages.page_text(driver).title()
    # Every item of the admin top menu must be present and visible.
    for item in ("Dashboard", "Inventory", "Orders", "Reports", "Settings", "Logout"):
        assert pages.main_nav_link(driver, item).is_displayed(), f"Menu link missing: {item}"


@need_admin
def test_tc04_view_inventory(driver):
    admin_login(driver)
    open_product_inventory(driver)
    assert pages.heading(driver) == "Product Inventory"
    # Count the rows in the product table body.
    rows = driver.find_elements(By.CSS_SELECTOR, "#product-table tbody tr")
    assert len(rows) > 0, "Product table has no rows"
    # An empty list still shows one placeholder row, so check it is not that.
    assert "No products yet" not in rows[0].text, "Inventory list is empty"


@need_admin
def test_tc05_search_product(driver):
    admin_login(driver)
    open_product_inventory(driver)
    # Use a product that really exists: take the first name in the list.
    first = driver.find_element(By.CSS_SELECTOR, "#product-table tbody tr button.name-link")
    keyword = first.text.strip()
    # Type that name into the search box and submit the search form.
    box = driver.find_element(By.CSS_SELECTOR, "form.list-search input[name='q']")
    box.clear()
    box.send_keys(keyword)
    driver.find_element(By.CSS_SELECTOR, "form.list-search button[type='submit']").click()
    # Wait for the reloaded table to show at least one row.
    pages.wait(driver).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#product-table tbody tr")))
    # Collect the product names now shown (lower-cased for comparison).
    names = [e.text.strip().lower() for e in
             driver.find_elements(By.CSS_SELECTOR, "#product-table tbody tr button.name-link")]
    assert names, "Search returned no products"
    # Every result must contain the keyword; otherwise the filter is wrong.
    assert all(keyword.lower() in n for n in names), f"Unrelated products returned: {names}"


# ---------------- Order management ----------------
@need_branch
def test_tc06_submit_order(driver):
    branch_login(driver)
    pages.click_main_nav(driver, "Orders")
    # Open the "Place Order" pop-up window (modal).
    pages.wait(driver).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[data-modal-open='place-order-modal']"))).click()
    # Wait for the first quantity input inside the modal.
    qty_box = pages.wait(driver).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#place-order-table input[name='qty[]']")))
    qty_box.clear()
    # Varying quantity avoids the app's "same open order already exists" rule on re-runs.
    qty_box.send_keys(str(int(time.time()) % 90 + 1))
    # Submit the order form.
    driver.find_element(By.CSS_SELECTOR, "#place-order-modal button[type='submit']").click()
    # The app confirms with a success message.
    pages.wait_for_text(driver, "Order placed.")
    assert "order placed." in pages.page_text(driver)


@need_branch
def test_tc07_view_order_status(driver):
    branch_login(driver)
    pages.click_main_nav(driver, "Orders")
    pages.wait(driver).until(EC.visibility_of_element_located((By.ID, "orders-table")))
    assert pages.heading(driver) == "Orders"
    # The orders table must have a "Status" column.
    headers = [h.text.strip().lower() for h in
               driver.find_elements(By.CSS_SELECTOR, "#orders-table thead th")]
    assert "status" in headers
    # Rows carry their status in a data-status attribute; the first one must have a value.
    rows = driver.find_elements(By.CSS_SELECTOR, "#orders-table tbody tr[data-status]")
    assert rows, "No submitted orders to check"
    assert rows[0].get_attribute("data-status"), "Order row has no status"


# ---------------- Delivery ----------------
@need_branch
def test_tc08_view_delivery(driver):
    branch_login(driver)
    pages.click_main_nav(driver, "Reports")  # Branch 'Reports' = Delivery Receipts
    pages.wait(driver).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "table.recent-table")))
    assert pages.heading(driver) == "Delivery Receipts"
    assert "delivery-receipts" in driver.current_url


# ---------------- Reports ----------------
@need_admin
def test_tc09_view_reports(driver):
    admin_login(driver)
    pages.click_main_nav(driver, "Reports")
    # The Reports menu opens one of several report pages; accept any of them.
    assert pages.heading(driver) in ("Sales Report", "Ingredient Audit", "Product Audit",
                                     "Delivery Receipts", "Account Reports")
    # The sub-menu should list at least one report link.
    sub_links = driver.find_elements(By.CSS_SELECTOR, "nav.sub-navbar a")
    assert len(sub_links) >= 1, "No report links displayed"


# ---------------- Logout / protected page ----------------
@need_admin
def test_tc10_logout(driver):
    admin_login(driver)
    protected_url = driver.current_url  # a page that requires being logged in
    pages.click_main_nav(driver, "Logout")
    # After logout the app sends us back to the login page.
    pages.wait(driver).until(lambda d: "auth/login" in d.current_url)
    driver.get(protected_url)  # protected page after logout
    # Without a session, the app must redirect to login again instead of showing the page.
    pages.wait(driver).until(EC.visibility_of_element_located((By.ID, "username_or_email")))
    assert "auth/login" in driver.current_url


# ---------------- Form validation / data operation ----------------
@need_admin
def test_tc11_add_product_empty_name(driver):
    admin_login(driver)
    open_product_inventory(driver)
    # Open the "Add Product" pop-up window (modal).
    pages.wait(driver).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[data-modal-open='add-product-modal']"))).click()
    name = pages.wait(driver).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#add-product-modal input[name='name']")))
    # Fill cost and price but deliberately leave the name empty.
    driver.find_element(By.CSS_SELECTOR, "#add-product-modal input[name='cost']").send_keys("5")
    driver.find_element(By.CSS_SELECTOR, "#add-product-modal input[name='price']").send_keys("10")
    driver.find_element(By.CSS_SELECTOR, "#add-product-modal button[type='submit']").click()
    # The browser blocks the submit because the name field is required and empty.
    # validity.valueMissing is the browser's own "required field is empty" flag.
    assert driver.execute_script("return arguments[0].validity.valueMissing", name)
    assert "product-inventory" in driver.current_url
    assert "product added." not in pages.page_text(driver)  # nothing was saved


# Every product created by the tests starts with this prefix, so cleanup can
# find and delete them without touching real products.
TEST_PRODUCT_PREFIX = "Selenium Test"


def search_products(driver, keyword):
    """Use the Product Inventory search box and wait for the filtered list."""
    box = pages.wait(driver).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "form.list-search input[name='q']")))
    box.clear()
    box.send_keys(keyword)
    driver.find_element(By.CSS_SELECTOR, "form.list-search button[type='submit']").click()
    # The old search box goes "stale" when the page reloads; that signals the new page is loading.
    pages.wait(driver).until(EC.staleness_of(box))
    pages.wait(driver).until(EC.visibility_of_element_located((By.ID, "product-table")))


def product_rows(driver, keyword):
    """Table rows whose product-name button contains `keyword`."""
    # XPath: a <tr> in #product-table that contains a name-link button with the keyword.
    xpath = ("//table[@id='product-table']//tr[.//button[contains(@class,'name-link') "
             f"and contains(normalize-space(), '{keyword}')]]")
    return driver.find_elements(By.XPATH, xpath)


def delete_test_products(driver):
    """Delete every product whose name starts with the test prefix (cleanup)."""
    search_products(driver, TEST_PRODUCT_PREFIX)
    # Keep deleting the first match until none are left.
    while product_rows(driver, TEST_PRODUCT_PREFIX):
        product_rows(driver, TEST_PRODUCT_PREFIX)[0].find_element(
            By.XPATH, ".//form//button[normalize-space()='Delete']").click()
        # The app asks "are you sure?" with a browser alert; accept it.
        pages.wait(driver).until(EC.alert_is_present()).accept()
        pages.wait_for_text(driver, "Product removed.")
        # Search again, because the page reloaded after the delete.
        search_products(driver, TEST_PRODUCT_PREFIX)


@need_admin
def test_tc12_add_and_delete_product(driver):
    admin_login(driver)
    open_product_inventory(driver)
    delete_test_products(driver)  # clear leftovers from any aborted earlier run
    # Unique name (prefix + timestamp) so this run's product can be told apart.
    product = f"{TEST_PRODUCT_PREFIX} {int(time.time())}"
    # Open the "Add Product" modal and fill in the form.
    pages.wait(driver).until(EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[data-modal-open='add-product-modal']"))).click()
    pages.wait(driver).until(EC.visibility_of_element_located(
        (By.CSS_SELECTOR, "#add-product-modal input[name='name']"))).send_keys(product)
    driver.find_element(By.CSS_SELECTOR, "#add-product-modal input[name='cost']").send_keys("5")
    driver.find_element(By.CSS_SELECTOR, "#add-product-modal input[name='price']").send_keys("10")
    driver.find_element(By.CSS_SELECTOR, "#add-product-modal button[type='submit']").click()
    pages.wait_for_text(driver, "Product added.")  # success message
    # The list is alphabetical and paged, so find the new record through search.
    search_products(driver, product)
    rows = product_rows(driver, product)
    assert len(rows) == 1, "New product does not appear in the product list"
    assert product in rows[0].text
    # Clean up so the data stays tidy, and check the record is gone.
    delete_test_products(driver)
    assert not product_rows(driver, product)
