"""
Preprocessing utilities for rent offer descriptions before embedding.
Removes noise that degrades vector search quality:
  1. Title duplication from the first lines of description
  2. Price / payment blocks
  3. Boilerplate / marketing phrases
"""

import json
import re
from pathlib import Path

EXAMPLES_PATH = Path(__file__).parent / "description_examples.json"


# ──────────────────────────────────────────────────────────────────
# 1. TITLE DEDUP
# ──────────────────────────────────────────────────────────────────

def _token_overlap(a: str, b: str) -> float:
    """Jaccard similarity on word sets (punctuation stripped)."""
    clean = lambda s: re.sub(r'[^\w\s]', '', s.lower()).split()
    ta, tb = set(clean(a)), set(clean(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)


def dedup_title_from_description(description: str, title: str, threshold: float = 0.6) -> str:
    """Remove first 1-3 lines of description if they closely repeat the title."""
    if not description or not title:
        return description or ""
    lines = description.split('\n')
    result = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if i < 3 and stripped and _token_overlap(stripped, title) >= threshold:
            continue
        result.append(line)
    return '\n'.join(result)


# ──────────────────────────────────────────────────────────────────
# 2. PRICE / PAYMENT BLOCK REMOVAL
# ──────────────────────────────────────────────────────────────────

# Named section headers that introduce a pure pricing block — removed until next blank line
_PRICE_SECTION_RE = re.compile(
    r'(?:^|\n)[ \t]*(?:CENA|KOMERČNÉ\s+PODMIENKY|CENA\s+PRENÁJMU|CENOVÉ\s+PODMIENKY)[ \t]*:?[ \t]*\n'
    r'.+?'
    r'(?=\n\n|\Z)',
    re.DOTALL | re.IGNORECASE,
)

# Money amount: digits followed by optional separators then €/eur/EUR
# Handles: 800 €, 800,-€, 800,- €, 800€, 1 600 eur, 1600,-eur
_MONEY_RE = re.compile(
    r'\d[\d\s,.]*(?:,-\s*)?\s*(?:€|EUR)\b',
    re.IGNORECASE,
)

# Patterns that unambiguously mark a standalone price/payment line
# re.MULTILINE so ^ matches start of each line (used inside remove_price_blocks on full text)
_PRICE_LINE_RE = re.compile(
    r'(?:'
    r'^\s*\+\s*energie\b'                                        # + energie 200 €
    r'|^\s*spolu\s*:'                                            # Spolu: 1 000 €
    r'|^\s*pri podpise\b'                                        # Pri podpise (nájomnej) zmluvy...
    r'|^\s*(?:depozit|kaucia|záloha|zábezpeka)\s*[:\-–]'        # Depozit: / Depozit –
    r'|^\s*(?:odmena|provízia)\s+(?:rk|realitnej)\b'            # Odmena RK / Provízia realitnej
    r'|^\s*\d+\s*[×x]\s*(?:nájom|kaucia|depozit|mesačný)\b'    # 1× kaucia vo výške...
    r'|^\s*nájom\s*(?:bytu)?\s*:'                               # Nájom: / Nájom bytu:
    r'|^\s*energie\s*:'                                          # Energie:
    r'|^\s*prevádzkové\s+náklady\s*:'                           # Prevádzkové náklady:
    r'|^\s*parkovani[ea]\s*:'                                    # Parkovanie: (v cenovej sekcii)
    r'|^\s*pivnica\s*:'                                          # Pivnica: (v cenovej sekcii)
    r'|^\s*cena\b'                                              # Cena ... (akýkoľvek riadok začínajúci Cena)
    r'|^\s*výmera\s*:'                                          # Výmera: X m2 (size metadata)
    r')',
    re.IGNORECASE | re.MULTILINE,
)

# Payment keywords — when combined with a money amount on a short line
# NOTE: no trailing \b — some keywords end with ':' which is a non-word char
_PAYMENT_KW_RE = re.compile(
    r'\b(?:'
    r'cena\s*:'                                   # Cena:
    r'|cena\s+(?:prenájmu|nájmu|za\s+prenájom|za\s+byt|za\s+dom)'
    r'|celková\s+cena'
    r'|mesačné\s+nájomné'
    r'|mesačný\s+nájom'
    r'|nájom(?:né)?\s+je'
    r'|nájom(?:né)?\s+\d'                         # nájomné 800 €
    r'|provízia'
    r'|odmena\s+rk'
    r'|výška\s+nájmu'
    r')',
    re.IGNORECASE,
)


def _is_price_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    if _PRICE_LINE_RE.match(stripped):
        return True
    # Short line with both a money amount and a clear payment keyword
    if len(stripped) < 180 and _MONEY_RE.search(stripped) and _PAYMENT_KW_RE.search(stripped):
        return True
    return False


def remove_price_blocks(text: str) -> str:
    # Remove named pricing section blocks first (multiline)
    text = _PRICE_SECTION_RE.sub('\n', text)
    # Then remove individual price lines
    lines = text.split('\n')
    lines = [ln for ln in lines if not _is_price_line(ln)]
    return '\n'.join(lines)


# ──────────────────────────────────────────────────────────────────
# 3. BOILERPLATE / MARKETING REMOVAL
# ──────────────────────────────────────────────────────────────────

_BOILERPLATE: list[re.Pattern] = [
    # ── Agency taglines ──
    re.compile(r'VYMEŇ SUSEDA!.*?sme tu pre teba\.?', re.IGNORECASE | re.DOTALL),
    re.compile(r'Follow the rivers?,?\s*find your home[. ]{0,5}', re.IGNORECASE),
    re.compile(r'Šťastie je doma\.?', re.IGNORECASE),

    # ── "Zobraziť" scraping artifacts ──
    # Removes everything from the last word-char before "..." up to end of that segment
    re.compile(r'[^\n]{0,120}\.\.\.[ \t]*Zobraziť (?:telefón|email|číslo)[^\n]*', re.IGNORECASE),

    # ── Copyright / authorship ──
    re.compile(r'©[^\n]*'),
    re.compile(r'(?:fotografie\s+a\s+text|text\s+inzerátu)[^.\n]*(?:autorským\s+dielom|majetkom)[^.\n]*\.', re.IGNORECASE),
    re.compile(r'Vyhotovené fotografie[^.]*\.', re.IGNORECASE),

    # ── Arvin & Benet Homestaging boilerplate (very common) ──
    re.compile(r'Nehnuteľnosť bola naaranžovaná[^.]*\.', re.IGNORECASE),
    re.compile(r'[Bb]yt bol naaranžovaný[^.]*\.', re.IGNORECASE),
    re.compile(r'[Vv]elmi radi V[aá]m pomôžeme pri efektívnom[^.]*\.', re.IGNORECASE),
    re.compile(r'[Rr]adi v[aá]m pomôžeme aj s efektívnym[^.]*\.', re.IGNORECASE),
    re.compile(r'[Rr]adi v[aá]m pomôžeme aj s profesionálnym[^.]*\.', re.IGNORECASE),
    re.compile(r'[Bb]udeme sa tešiť[^.]*\.', re.IGNORECASE),
    re.compile(r'[Tt]ešíme sa na v[aá]š nezáväzný kontakt\.?', re.IGNORECASE),

    # ── CTAs (call to action) ──
    re.compile(r'Určite odporúčame danú nehnuteľnosť[^.]*\.', re.IGNORECASE),
    re.compile(r'Pre termín obhliadky[^.]*(?:kontaktovať|kontaktujte|kontakt)[^.]*\.', re.IGNORECASE),
    re.compile(r'V prípade (?:záujmu|obhliadky)[^.]*(?:kontaktovať|kontaktujte|kontaktujte)[^.]*\.', re.IGNORECASE),
    re.compile(r'V prípade (?:záujmu|obhliadky)[^\n]*(?:prosím\s+)?kontaktujte[^\n]*', re.IGNORECASE),
    re.compile(r'Neváhajte nás kontaktovať[^.]*\.', re.IGNORECASE),
    re.compile(r'[Rr]adi (?:Vás|vás) uvítame na obhliadkach?[^.]*\.', re.IGNORECASE),
    re.compile(r'[Vv]olajte alebo p[ií]šte pre viac inform[aá]cií[^.]*\.', re.IGNORECASE),
    re.compile(r'[Tt]ešíme sa na [Vv]ás\.?', re.IGNORECASE),
    re.compile(r'[Vv]iac inform[aá]cií V[aá]m radi poskytneme[^.]*\.', re.IGNORECASE),

    # ── Contact lines ──
    re.compile(r'Kontakt(?:\s+na\s+[\w\s]{1,30})?\s*:\s*[^\n]*', re.IGNORECASE),

    # ── Agency memberships / self-promo ──
    re.compile(r'[Ss]me členmi Realitnej únie[^.]*\.', re.IGNORECASE),
    re.compile(r'NARKS[^\n]*', re.IGNORECASE),
    re.compile(r'V\s+\w+(?:\s+\w+){0,3}\s+poskytujeme profesionálne služby[^.]*\.', re.IGNORECASE),
    re.compile(r's viac ako \d+-ročnými skúsenosťami[^.]*\.', re.IGNORECASE),

    # ── "Spoluprácou s nami získate:" promo block ──
    # Removes from the header line until end of the bullet list (next blank line or end)
    re.compile(r'Spoluprácou s nami získate\s*:.*?(?=\n\n|\Z)', re.IGNORECASE | re.DOTALL),

    # ── Agency disclaimers ──
    re.compile(r'Nie sme realitná kancelária[^.]*\.', re.IGNORECASE),
    re.compile(r'[Pp]oprosíme realitné kancelárie[^.]*\.', re.IGNORECASE),
    re.compile(r'[Zz]áujemca neplatí RK[^.]*\.', re.IGNORECASE),
]


def remove_boilerplate(text: str) -> str:
    for pattern in _BOILERPLATE:
        text = pattern.sub('', text)
    return text


# ──────────────────────────────────────────────────────────────────
# 4. TRAILING BOILERPLATE STRIPPING (generic, agency-agnostic)
# ──────────────────────────────────────────────────────────────────

# Words that signal a CTA / contact / self-promo paragraph
_TRAILING_NOISE_RE = re.compile(
    r'\b('
    r'kontaktujte|kontaktovať|kontaktujeme|kontaktova[ťt]'
    r'|obhliadka|obhliadke|obhliadku'
    r'|nezáväzne|nezáväzný'
    r'|pomôžeme|pomôcť'
    r'|tešíme\s+sa|tešíme'
    r'|neváhajte'
    r'|sprostredkovanie|sprostredkovateľ'
    r'|realitná\s+kancelária\s+.{0,40}ponúka'  # "RK X ponúka" self-intro in trailing position
    r')\b',
    re.IGNORECASE,
)

# Max paragraph length (chars) to still consider it a boilerplate candidate
_TRAILING_MAX_CHARS = 350


def strip_trailing_boilerplate(text: str) -> str:
    """
    Removes trailing paragraphs that look like CTA / contact / agency self-promo.
    Works on any agency without knowing specific phrases.
    Stops as soon as it hits a paragraph that looks like real content.
    """
    paragraphs = text.split('\n\n')
    while paragraphs:
        last = paragraphs[-1].strip()
        if last and len(last) <= _TRAILING_MAX_CHARS and _TRAILING_NOISE_RE.search(last):
            paragraphs.pop()
        else:
            break
    return '\n\n'.join(paragraphs)


# ──────────────────────────────────────────────────────────────────
# Master cleaning function
# ──────────────────────────────────────────────────────────────────

def clean_description_for_embedding(description: str, title: str = "") -> str:
    if not description:
        return description or ""
    text = dedup_title_from_description(description, title)
    text = remove_price_blocks(text)
    text = remove_boilerplate(text)
    text = strip_trailing_boilerplate(text)
    # Normalize whitespace
    text = re.sub(r'[ \t]+\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


# ──────────────────────────────────────────────────────────────────
# Interactive preview
# ──────────────────────────────────────────────────────────────────

def _diff_summary(original: str, cleaned: str) -> str:
    orig_chars = len(original)
    clean_chars = len(cleaned)
    removed = orig_chars - clean_chars
    pct = removed / orig_chars * 100 if orig_chars else 0
    return f"  znakov: {orig_chars} → {clean_chars}  (odstranene {removed}, {pct:.1f} %)"


SEP  = "─" * 90
SEP2 = "═" * 90


def preview():
    with open(EXAMPLES_PATH, encoding='utf-8') as f:
        examples = json.load(f)

    skipped = 0
    shown = 0
    total = len(examples)

    for i, item in enumerate(examples, 1):
        title       = item.get('title', '').strip()
        description = item.get('description', '').strip()

        if not description:
            skipped += 1
            continue

        cleaned = clean_description_for_embedding(description, title)
        shown += 1

        print(f"\n{SEP2}")
        print(f"  [{i}/{total}]  (zobrazene: {shown}, preskocene bez opisu: {skipped})")
        print(SEP2)

        print(f"\nORIGINAL NADPIS:\n  {title}")
        print(f"\nORIGINAL OPIS:\n{description}")

        print(f"\n{SEP}")
        print(f"\nCLEANED NADPIS:\n  {title}")
        print(f"\nCLEANED OPIS:\n{cleaned}")
        print(f"\n{_diff_summary(description, cleaned)}")
        print(SEP2)

        try:
            input("\n  [Enter] dalsi  |  Ctrl+C koniec\n")
        except KeyboardInterrupt:
            print(f"\n\nUkoncene. Zobrazene {shown} inzeratov.")
            break


if __name__ == '__main__':
    preview()
