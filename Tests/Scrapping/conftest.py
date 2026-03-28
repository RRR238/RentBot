"""
Fixtures shared across all Scrapping tests.
Heavy external dependencies are already stubbed by the root Tests/conftest.py.
"""
from unittest.mock import MagicMock

import pytest
from bs4 import BeautifulSoup

from Scrapping.Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Scrapping.Reality_sk import Reality_sk_processor


def make_soup(html: str) -> BeautifulSoup:
    """Parse an HTML string into a BeautifulSoup object."""
    return BeautifulSoup(html, "html.parser")


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def mock_llm():
    return MagicMock()


@pytest.fixture
def mock_vdb():
    return MagicMock()


@pytest.fixture
def nehnutelnosti_processor(mock_db, mock_llm, mock_vdb):
    return Nehnutelnosti_sk_processor(
        base_url="https://www.nehnutelnosti.sk/prenajom/byty/",
        auth_token="test-token",
        db_repository=mock_db,
        llm=mock_llm,
        vector_db=mock_vdb,
    )


@pytest.fixture
def reality_processor(mock_db, mock_llm, mock_vdb):
    return Reality_sk_processor(
        base_url="https://www.reality.sk/prenajom/byty/",
        auth_token="test-token",
        db_repository=mock_db,
        llm=mock_llm,
        vector_db=mock_vdb,
    )
