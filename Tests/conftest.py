"""
Root conftest: patches heavy/unavailable imports before any test module loads.
Must live at Tests/ level so it runs before all sub-packages.
"""
import os
import sys
from unittest.mock import MagicMock

# ---------------------------------------------------------------------------
# Make project root and Scrapping/ importable
# ---------------------------------------------------------------------------
_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_SCRAPPING = os.path.join(_ROOT, "Scrapping")
for _p in (_ROOT, _SCRAPPING):
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# Stub every external / heavy dependency so processors can be imported
# without a full environment (no Selenium, no LLM keys, no DB, …)
# ---------------------------------------------------------------------------
_STUBS = [
    # LangChain
    "langchain",
    "langchain.chat_models",
    # Selenium + driver manager
    "selenium",
    "selenium.webdriver",
    "selenium.webdriver.chrome",
    "selenium.webdriver.chrome.service",
    "selenium.webdriver.chrome.options",
    "selenium.webdriver.common",
    "selenium.webdriver.common.by",
    "selenium.webdriver.common.keys",
    "selenium.webdriver.support",
    "selenium.webdriver.support.expected_conditions",
    "selenium.webdriver.support.ui",
    "webdriver_manager",
    "webdriver_manager.chrome",
    # SQLAlchemy (used by Rent_offers_repository)
    "sqlalchemy",
    "sqlalchemy.orm",
    "sqlalchemy.exc",
    # Internal modules with heavy transitive deps
    "Analytics",
    "Analytics.AI",
    "Analytics.AI.utils",
    "Shared",
    "Shared.Geolocation",
    "Shared.LLM",
    "Shared.Vector_database",
    "Shared.Vector_database.Vector_DB_interface",
    "Shared.DB_models",
    # Bare-name variants used inside Reality_sk.py
    "Rent_offers_repository",
]

for _mod in _STUBS:
    sys.modules.setdefault(_mod, MagicMock())

# Give specific return values where the processor logic depends on them
sys.modules["Shared.Geolocation"].get_coordinates = MagicMock(
    return_value=(48.1486, 17.1077)
)
sys.modules["Analytics.AI.utils"].create_chain = MagicMock(
    return_value=MagicMock()
)