# GABS Selenium practicum

Python + Selenium WebDriver + pytest. 12 tests (TC-01 to TC-12).

## Run

```powershell
pip install selenium pytest pytest-html
$env:GABS_ADMIN_USER = "<admin username>"
$env:GABS_ADMIN_PASS = "<admin password>"
$env:GABS_BRANCH_USER = "<branch username>"
$env:GABS_BRANCH_PASS = "<branch password>"
python -m pytest -v --html=evidence/report.html --self-contained-html
```

Default target is `http://localhost/GABS/public`. To test the hosted site set
`GABS_BASE_URL=https://gabsbakeshop.lsu-source.org`.

Tests whose account variables are not set are skipped, not passed.

## Files

| File | Purpose |
|---|---|
| `config.py` | URL, accounts (read from environment variables) |
| `conftest.py` | Chrome start/stop and a screenshot after every test |
| `pages.py` | Login and menu helpers, explicit-wait helpers |
| `tests/test_gabs.py` | The 12 test cases |
| `evidence/` | Screenshots and `report.html` |
| `Selenium Final Activity - Completed.docx` | Filled-in test case table, scripts, evidence, summary, AI log |

`test_accounts.env` holds the password of the test Branch account created on the
local copy. Do not submit it. `build_report.py` rebuilds the Word document.
