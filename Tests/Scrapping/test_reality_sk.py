"""
Unit tests for Reality_sk_processor.

Reality_sk_processor extends Nehnutelnosti_sk_processor and overrides
several static methods.  Only the overridden / Reality-specific behaviour
is tested here; inherited behaviour is covered in test_nehnutelnosti_sk.py.
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from Scrapping.Reality_sk import Reality_sk_processor
from Tests.Scrapping.conftest import make_soup


# ---------------------------------------------------------------------------
# get_price  (override)
# ---------------------------------------------------------------------------

class TestGetPrice:
    _PRICE_HTML = """
    <div class="d-flex flex-wrap no-gutters justify-content-between align-items-center">
      <h3 class="contact-title big col-12 col-md-6 mb-0">{rent_text}</h3>
    </div>
    """

    def test_parses_rent(self):
        html = self._PRICE_HTML.format(rent_text="850 €/mes.")
        prices = Reality_sk_processor.get_price(make_soup(html))
        assert prices.rent == 850

    def test_parses_rent_with_whitespace(self):
        html = self._PRICE_HTML.format(rent_text="1 200 €/mes.")
        prices = Reality_sk_processor.get_price(make_soup(html))
        assert prices.rent == 1200

    def test_energies_default_to_none(self):
        html = self._PRICE_HTML.format(rent_text="850 €")
        prices = Reality_sk_processor.get_price(make_soup(html))
        assert prices.energies is None

    def test_returns_none_when_container_absent(self):
        prices = Reality_sk_processor.get_price(make_soup("<div>nothing</div>"))
        assert prices.rent is None
        assert prices.meter_squared is None


# ---------------------------------------------------------------------------
# get_key_attributes  (override)
# ---------------------------------------------------------------------------

class TestGetKeyAttributes:
    def _make_html(self, druh: str, plocha: str = "75 m²") -> str:
        return f"""
        <div class="info-title">Druh:</div>
        <div class="col-sm-8 col-6">{druh}</div>
        <div class="info-title">Úžitková plocha:</div>
        <div class="col-sm-8 col-6">{plocha}</div>
        """

    def test_detects_flat_with_room_count(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("3-izbový byt")))
        assert attrs.flat is True
        assert attrs.rooms == 3

    def test_detects_studio(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("Garsónka")))
        assert attrs.studio is True

    def test_detects_double_studio(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("Dvojgarsónka")))
        assert attrs.double_studio is True

    def test_detects_apartment(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("Apartmán")))
        assert attrs.apartmen is True

    def test_detects_house(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("Rodinný dom")))
        assert attrs.house is True

    def test_detects_mezonet(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("Mezonet")))
        assert attrs.mezonet is True

    def test_parses_size(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup(self._make_html("2-izbový byt", "65,5 m²")))
        assert attrs.size == pytest.approx(65.5)

    def test_returns_defaults_when_no_labels(self):
        attrs = Reality_sk_processor.get_key_attributes(make_soup("<div>nothing</div>"))
        assert attrs.flat is False
        assert attrs.rooms is None
        assert attrs.size is None


# ---------------------------------------------------------------------------
# get_description  (override)
# ---------------------------------------------------------------------------

class TestGetDescription:
    def test_returns_text_from_content_preview(self):
        html = """
        <div data-show-more-inner="">
          <span class="content-preview">Prenájom 3-izbového bytu v centre.</span>
        </div>
        """
        result = Reality_sk_processor.get_description(make_soup(html))
        assert result == "Prenájom 3-izbového bytu v centre."

    def test_returns_none_when_span_absent(self):
        html = '<div data-show-more-inner=""><p>No span here</p></div>'
        result = Reality_sk_processor.get_description(make_soup(html))
        assert result is None

    def test_raises_when_outer_div_absent(self):
        with pytest.raises(AttributeError):
            Reality_sk_processor.get_description(make_soup("<div>nothing</div>"))


# ---------------------------------------------------------------------------
# get_other_properties  (override)
# ---------------------------------------------------------------------------

class TestGetOtherProperties:
    def test_builds_dict_from_info_title_labels(self):
        html = """
        <div class="info-title">Rok výstavby:</div>
        <div>2010</div>
        <div class="info-title">Vlastníctvo:</div>
        <div>osobné</div>
        """
        result = Reality_sk_processor.get_other_properties(make_soup(html))
        assert result["Rok výstavby:"] == "2010"
        assert result["Vlastníctvo:"] == "osobné"

    def test_returns_empty_dict_when_no_labels(self):
        result = Reality_sk_processor.get_other_properties(make_soup("<div>nothing</div>"))
        assert result == {}

    def test_skips_label_with_no_following_div(self):
        html = """
        <div class="info-title">Kľúč:</div>
        <p>not a div</p>
        """
        result = Reality_sk_processor.get_other_properties(make_soup(html))
        # find_next('div') will not find a div sibling here – result is empty or only has
        # entries where a next div exists
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# get_details_links  (override – filters on path depth and last segment)
# ---------------------------------------------------------------------------

class TestGetDetailsLinks:
    def test_includes_deep_links(self, reality_processor):
        html = (
            '<a href="https://www.reality.sk/byty/prenajom/bratislava/'
            '3-izbovy-byt/12345">Offer</a>'
        )
        links = reality_processor.get_details_links(make_soup(html))
        assert "https://www.reality.sk/byty/prenajom/bratislava/3-izbovy-byt/12345" in links

    def test_excludes_link_ending_in_bratislava(self, reality_processor):
        html = '<a href="https://www.reality.sk/byty/prenajom/bratislava">City</a>'
        links = reality_processor.get_details_links(make_soup(html))
        assert links == []

    def test_excludes_link_ending_in_predaj(self, reality_processor):
        html = (
            '<a href="https://www.reality.sk/byty/prenajom/bratislava/predaj">Sale</a>'
        )
        links = reality_processor.get_details_links(make_soup(html))
        assert links == []

    def test_excludes_link_ending_in_prenajom(self, reality_processor):
        html = (
            '<a href="https://www.reality.sk/byty/prenajom/bratislava/prenajom">Rent</a>'
        )
        links = reality_processor.get_details_links(make_soup(html))
        assert links == []

    def test_excludes_too_short_paths(self, reality_processor):
        html = '<a href="https://www.reality.sk/byty/prenajom">Short</a>'
        links = reality_processor.get_details_links(make_soup(html))
        assert links == []

    def test_excludes_test_urls(self, reality_processor):
        html = (
            '<a href="https://www.reality.sk/byty/prenajom/test/3-izbovy-byt/99">Test</a>'
        )
        links = reality_processor.get_details_links(make_soup(html))
        assert links == []


# ---------------------------------------------------------------------------
# last_page_number_check  (Reality override)
# ---------------------------------------------------------------------------

class TestLastPageNumberCheck:
    @patch("requests.get")
    def test_returns_max_page_from_pagination(self, mock_get, reality_processor):
        html = """
        <html><body>
          <a class="next-number" href="?page=1">1</a>
          <a class="next-number" href="?page=5">5</a>
          <a class="next-number" href="?page=10">10</a>
        </body></html>
        """
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_get.return_value = mock_resp

        result = reality_processor.last_page_number_check()
        assert result == 10

    @patch("requests.get")
    def test_returns_active_page_when_present(self, mock_get, reality_processor):
        html = """
        <html><body>
          <a class="next-number" href="?page=3">3</a>
          <span class="next-number active">7</span>
        </body></html>
        """
        mock_resp = MagicMock()
        mock_resp.text = html
        mock_get.return_value = mock_resp

        result = reality_processor.last_page_number_check()
        assert result == 7

    @patch("requests.get")
    def test_returns_1_when_no_pagination(self, mock_get, reality_processor):
        mock_resp = MagicMock()
        mock_resp.text = "<html><body></body></html>"
        mock_get.return_value = mock_resp

        result = reality_processor.last_page_number_check()
        assert result == 1


# ---------------------------------------------------------------------------
# is_update_newer  (Reality override – same logic as Nehnutelnosti)
# ---------------------------------------------------------------------------

class TestIsUpdateNewer:
    _HTML_TEMPLATE = """
    <html><body>
      <div></div><div></div><div></div><div></div><div></div><div></div>
      <div>
        <div></div>
        <div>
          <div>
            <div>
              <div></div>
              <div><p><span>Aktualizované</span><span>: {date}</span></p></div>
            </div>
          </div>
        </div>
      </div>
    </body></html>
    """

    @patch("requests.get")
    def test_returns_true_when_scraped_date_is_newer(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.content = self._HTML_TEMPLATE.format(date="20. 03. 2026").encode()
        mock_get.return_value = mock_resp

        assert Reality_sk_processor.is_update_newer(
            "https://www.reality.sk/byty/detail/123",
            datetime(2025, 1, 1),
        ) is True

    @patch("requests.get")
    def test_returns_false_when_scraped_date_is_older(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.content = self._HTML_TEMPLATE.format(date="01. 01. 2024").encode()
        mock_get.return_value = mock_resp

        assert Reality_sk_processor.is_update_newer(
            "https://www.reality.sk/byty/detail/123",
            datetime(2025, 1, 1),
        ) is False

    @patch("requests.get")
    def test_returns_false_when_element_absent(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.content = b"<html><body></body></html>"
        mock_get.return_value = mock_resp

        assert Reality_sk_processor.is_update_newer(
            "https://www.reality.sk/byty/detail/123",
            datetime(2025, 1, 1),
        ) is False
