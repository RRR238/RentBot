"""
Unit tests for Nehnutelnosti_sk_processor.

Covers all static/pure methods and instance methods that do not require
live HTTP requests.  Methods that call requests.get are tested with a
unittest.mock.patch on the requests module.
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from Scrapping.Nehnutelnosti_sk import Nehnutelnosti_sk_processor
from Tests.Scrapping.conftest import make_soup


# ---------------------------------------------------------------------------
# get_title
# ---------------------------------------------------------------------------

class TestGetTitle:
    def test_returns_text_for_primary_class(self):
        html = '<h1 class="MuiTypography-root MuiTypography-h4 mui-1wj7mln">  3-izbový byt  </h1>'
        assert Nehnutelnosti_sk_processor.get_title(make_soup(html)) == "3-izbový byt"

    def test_returns_text_for_fallback_class(self):
        html = '<h1 class="MuiTypography-root MuiTypography-h4 mui-hrlyv4">  2-izbový byt  </h1>'
        assert Nehnutelnosti_sk_processor.get_title(make_soup(html)) == "2-izbový byt"

    def test_returns_none_when_element_absent(self):
        assert Nehnutelnosti_sk_processor.get_title(make_soup("<div>nothing</div>")) is None


# ---------------------------------------------------------------------------
# get_location
# ---------------------------------------------------------------------------

class TestGetLocation:
    def test_returns_text_for_primary_class(self):
        html = (
            '<p class="MuiTypography-root MuiTypography-body2 '
            'MuiTypography-noWrap mui-3vjwr4">  Bratislava  </p>'
        )
        assert Nehnutelnosti_sk_processor.get_location(make_soup(html)) == "Bratislava"

    def test_returns_text_for_fallback_class(self):
        html = (
            '<p class="MuiTypography-root MuiTypography-body2 '
            'MuiTypography-noWrap mui-kri7tw">Košice</p>'
        )
        assert Nehnutelnosti_sk_processor.get_location(make_soup(html)) == "Košice"

    def test_returns_none_when_element_absent(self):
        assert Nehnutelnosti_sk_processor.get_location(make_soup("<div>nothing</div>")) is None


# ---------------------------------------------------------------------------
# _parse_property_paragraphs
# ---------------------------------------------------------------------------

class TestParsePropertyParagraphs:
    def _make_paragraphs(self, texts):
        from bs4 import BeautifulSoup
        html = "".join(f"<p>{t}</p>" for t in texts)
        return BeautifulSoup(html, "html.parser").find_all("p")

    def test_builds_key_value_dict(self):
        result = Nehnutelnosti_sk_processor._parse_property_paragraphs(
            self._make_paragraphs(["Rok výstavby:", "2005", "Vlastníctvo:", "osobné"])
        )
        assert result == {"Rok výstavby:": "2005", "Vlastníctvo:": "osobné"}

    def test_ignores_standalone_value_without_key(self):
        result = Nehnutelnosti_sk_processor._parse_property_paragraphs(
            self._make_paragraphs(["Kľúč:", "hodnota", "Orphan"])
        )
        assert result == {"Kľúč:": "hodnota"}

    def test_returns_empty_dict_for_empty_input(self):
        assert Nehnutelnosti_sk_processor._parse_property_paragraphs([]) == {}


# ---------------------------------------------------------------------------
# get_detail_properties
# ---------------------------------------------------------------------------

class TestGetDetailProperties:
    def test_builds_dict_from_stable_container(self):
        html = """
        <div class="MuiGrid-spacing-md-1">
          <p data-test-id="text">Podlažie:</p>
          <p data-test-id="text">3/8</p>
          <p data-test-id="text">Rok výstavby:</p>
          <p data-test-id="text">2010</p>
        </div>
        """
        result = Nehnutelnosti_sk_processor.get_detail_properties(make_soup(html))
        assert result == {"Podlažie:": "3/8", "Rok výstavby:": "2010"}

    def test_returns_empty_dict_when_container_absent(self):
        assert Nehnutelnosti_sk_processor.get_detail_properties(make_soup("<div>nothing</div>")) == {}


# ---------------------------------------------------------------------------
# get_other_properties
# ---------------------------------------------------------------------------

class TestGetOtherProperties:
    def _make_section(self, pairs):
        items = ""
        for key, val in pairs:
            items += f"""
            <div class="MuiStack-root mui-inner">
              <p data-test-id="text">{key}</p>
              <p data-test-id="text">{val}</p>
            </div>"""
        return f"""
        <div class="MuiStack-root mui-outer">
          <h3>Vlastnosti nehnuteľnosti</h3>
          {items}
        </div>"""

    def test_builds_key_value_dict(self):
        html = self._make_section([("Vybavenie:", "Výťah"), ("Počet loggí:", "1")])
        result = Nehnutelnosti_sk_processor.get_other_properties(make_soup(html))
        assert result == {"Vybavenie:": "Výťah", "Počet loggí:": "1"}

    def test_returns_empty_dict_when_heading_absent(self):
        assert Nehnutelnosti_sk_processor.get_other_properties(make_soup("<div>nothing</div>")) == {}

    def test_ignores_standalone_paragraph_without_pair(self):
        html = self._make_section([("Kľúč:", "hodnota")]) + "<p data-test-id='text'>Orphan</p>"
        result = Nehnutelnosti_sk_processor.get_other_properties(make_soup(html))
        assert result == {"Kľúč:": "hodnota"}


# ---------------------------------------------------------------------------
# get_description
# ---------------------------------------------------------------------------

class TestGetDescription:
    def _mock_driver(self, page_source: str):
        driver = MagicMock()
        driver.page_source = page_source
        return driver

    def test_returns_stripped_text(self):
        html = '<p id="detail-description">  Krásny byt v centre.  </p>'
        with patch.object(Nehnutelnosti_sk_processor, '_make_headless_driver',
                          return_value=self._mock_driver(html)):
            result = Nehnutelnosti_sk_processor.get_description("https://example.com/detail/123")
        assert result == "Krásny byt v centre."

    def test_strips_citat_dalej(self):
        html = '<p id="detail-description">Krásny byt. Čítať ďalej</p>'
        with patch.object(Nehnutelnosti_sk_processor, '_make_headless_driver',
                          return_value=self._mock_driver(html)):
            result = Nehnutelnosti_sk_processor.get_description("https://example.com/detail/123")
        assert "Čítať ďalej" not in result

    def test_returns_none_when_element_absent(self):
        with patch.object(Nehnutelnosti_sk_processor, '_make_headless_driver',
                          return_value=self._mock_driver("<div>nothing</div>")):
            result = Nehnutelnosti_sk_processor.get_description("https://example.com/detail/123")
        assert result is None


# ---------------------------------------------------------------------------
# get_images_url
# ---------------------------------------------------------------------------

class TestGetImagesUrl:
    def test_constructs_gallery_url(self):
        link = "https://www.nehnutelnosti.sk/detail/12345/"
        result = Nehnutelnosti_sk_processor.get_images_url(link)
        assert result == "https://www.nehnutelnosti.sk/detail/galeria/foto/12345/"

    def test_handles_id_with_slug(self):
        link = "https://www.nehnutelnosti.sk/detail/3-izbovy-byt-456"
        result = Nehnutelnosti_sk_processor.get_images_url(link)
        assert result == "https://www.nehnutelnosti.sk/detail/galeria/foto/3-izbovy-byt-456"


# ---------------------------------------------------------------------------
# get_price
# ---------------------------------------------------------------------------

class TestGetPrice:
    def test_parses_rent_from_primary_class(self):
        html = '<p class="MuiTypography-root MuiTypography-h3 mui-fm8hb4">850\xa0€/mes.</p>'
        prices = Nehnutelnosti_sk_processor.get_price(make_soup(html))
        assert prices.rent == 850

    def test_parses_rent_from_fallback_class(self):
        html = '<p class="MuiTypography-root MuiTypography-h3 mui-9867wo">1\xa0200\xa0€</p>'
        prices = Nehnutelnosti_sk_processor.get_price(make_soup(html))
        assert prices.rent == 1200

    def test_parses_energies(self):
        html = """
        <p class="MuiTypography-root MuiTypography-h3 mui-fm8hb4">850\xa0€</p>
        <p class="MuiTypography-root MuiTypography-label2 mui-180mgf9">+ 150 €/mes.</p>
        """
        prices = Nehnutelnosti_sk_processor.get_price(make_soup(html))
        assert prices.energies == 150

    def test_parses_meter_squared(self):
        html = """
        <p class="MuiTypography-root MuiTypography-h3 mui-fm8hb4">850\xa0€</p>
        <p class="MuiTypography-root MuiTypography-label2 mui-dqi7hg">8,50\xa0€/m²</p>
        """
        prices = Nehnutelnosti_sk_processor.get_price(make_soup(html))
        assert prices.meter_squared == 8.50

    def test_returns_none_fields_when_elements_absent(self):
        prices = Nehnutelnosti_sk_processor.get_price(make_soup("<div>nothing</div>"))
        assert prices.rent is None
        assert prices.energies is None
        assert prices.meter_squared is None


# ---------------------------------------------------------------------------
# extract_energy_price_by_pattern  (pure regex – no mocking needed)
# ---------------------------------------------------------------------------

class TestExtractEnergyPriceByPattern:
    @pytest.mark.parametrize("text,expected", [
        ("energie:100", "100"),
        ("+150energie", "150"),
        ("+200€energie", "200"),
        ("+300eurenergie", "300"),
        ("energievrátaneinternetuatv:250", "250"),
        ("+180,-", "180"),
        ("+energie120", "120"),
        ("cenanezahŕňaenergie350", "350"),
        ("no match here", None),
        ("", None),
    ])
    def test_pattern(self, text, expected):
        assert Nehnutelnosti_sk_processor.extract_energy_price_by_pattern(text) == expected


# ---------------------------------------------------------------------------
# remove_non_slovak_sections
# ---------------------------------------------------------------------------

class TestRemoveNonSlovakSections:
    def test_keeps_slovak_lines(self):
        with patch("Scrapping.Nehnutelnosti_sk.detect", return_value="sk"):
            result = Nehnutelnosti_sk_processor.remove_non_slovak_sections(
                "Krásny byt.\nPrenájom."
            )
        assert result == "Krásny byt.\nPrenájom."

    def test_removes_non_slovak_lines(self):
        def mock_detect(s):
            return "sk" if "byt" in s else "en"

        with patch("Scrapping.Nehnutelnosti_sk.detect", side_effect=mock_detect):
            result = Nehnutelnosti_sk_processor.remove_non_slovak_sections(
                "Krásny byt.\nBeautiful flat."
            )
        assert result == "Krásny byt."

    def test_skips_empty_lines(self):
        with patch("Scrapping.Nehnutelnosti_sk.detect", return_value="sk"):
            result = Nehnutelnosti_sk_processor.remove_non_slovak_sections(
                "Byt.\n\n  \nPrenájom."
            )
        assert result == "Byt.\nPrenájom."

    def test_returns_empty_string_for_all_non_slovak(self):
        with patch("Scrapping.Nehnutelnosti_sk.detect", return_value="en"):
            result = Nehnutelnosti_sk_processor.remove_non_slovak_sections(
                "Hello.\nGoodbye."
            )
        assert result == ""


# ---------------------------------------------------------------------------
# get_details_links
# ---------------------------------------------------------------------------

class TestGetDetailsLinks:
    def test_returns_links_containing_keyword(self, nehnutelnosti_processor):
        html = """
        <a href="/detail/123-byt">Link 1</a>
        <a href="https://www.nehnutelnosti.sk/detail/456">Link 2</a>
        <a href="/other/page">Other</a>
        """
        links = nehnutelnosti_processor.get_details_links(make_soup(html))
        assert any("detail/123" in l for l in links)
        assert any("detail/456" in l for l in links)
        assert all("other/page" not in l for l in links)

    def test_constructs_full_url_for_relative_href(self, nehnutelnosti_processor):
        html = '<a href="/detail/789">Link</a>'
        links = nehnutelnosti_processor.get_details_links(make_soup(html))
        assert links == ["https://www.nehnutelnosti.sk/detail/789"]

    def test_excludes_urls_containing_test(self, nehnutelnosti_processor):
        html = '<a href="https://www.nehnutelnosti.sk/detail/test-flat">Test</a>'
        links = nehnutelnosti_processor.get_details_links(make_soup(html))
        assert links == []

    def test_deduplicates_links(self, nehnutelnosti_processor):
        html = """
        <a href="/detail/123">Link</a>
        <a href="/detail/123">Duplicate</a>
        """
        links = nehnutelnosti_processor.get_details_links(make_soup(html))
        assert len(links) == 1

    def test_returns_empty_list_when_no_matching_links(self, nehnutelnosti_processor):
        html = '<a href="/search?page=2">Next page</a>'
        links = nehnutelnosti_processor.get_details_links(make_soup(html))
        assert links == []


# ---------------------------------------------------------------------------
# get_key_attributes – only the safe no-SVG path (empty container)
# ---------------------------------------------------------------------------

class TestGetKeyAttributes:
    def test_returns_defaults_when_container_absent(self):
        attrs = Nehnutelnosti_sk_processor.get_key_attributes(make_soup("<div>nothing</div>"))
        assert attrs.flat is False
        assert attrs.house is False
        assert attrs.studio is False
        assert attrs.rooms is None
        assert attrs.size is None
        assert attrs.property_status is None


# ---------------------------------------------------------------------------
# is_update_newer
# ---------------------------------------------------------------------------

class TestIsUpdateNewer:
    # Build minimal HTML that satisfies xpath
    # /html/body/div[7]/div[2]/div/div[1]/div[2]/p/span[2]
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
        mock_resp.content = self._HTML_TEMPLATE.format(date="15. 01. 2026").encode()
        mock_get.return_value = mock_resp

        result = Nehnutelnosti_sk_processor.is_update_newer(
            "https://www.nehnutelnosti.sk/detail/123",
            datetime(2025, 6, 1),
        )
        assert result is True

    @patch("requests.get")
    def test_returns_false_when_scraped_date_is_older(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.content = self._HTML_TEMPLATE.format(date="15. 01. 2024").encode()
        mock_get.return_value = mock_resp

        result = Nehnutelnosti_sk_processor.is_update_newer(
            "https://www.nehnutelnosti.sk/detail/123",
            datetime(2025, 6, 1),
        )
        assert result is False

    @patch("requests.get")
    def test_returns_false_when_element_absent(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.content = b"<html><body></body></html>"
        mock_get.return_value = mock_resp

        result = Nehnutelnosti_sk_processor.is_update_newer(
            "https://www.nehnutelnosti.sk/detail/123",
            datetime(2025, 6, 1),
        )
        assert result is False

    @patch("requests.get")
    def test_strips_timezone_from_reference_time(self, mock_get):
        from datetime import timezone

        mock_resp = MagicMock()
        mock_resp.content = self._HTML_TEMPLATE.format(date="15. 01. 2026").encode()
        mock_get.return_value = mock_resp

        result = Nehnutelnosti_sk_processor.is_update_newer(
            "https://www.nehnutelnosti.sk/detail/123",
            datetime(2025, 6, 1, tzinfo=timezone.utc),
        )
        assert result is True
