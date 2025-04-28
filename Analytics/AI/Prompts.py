check_conversation_prompt = """
Tvojou úlohou je určiť, či sa nový vstup používateľa stále týka tej istej nehnuteľnosti ako predchádzajúca konverzácia, alebo ide o nový a samostatný dopyt.

KONVERZÁCIA:
{chat_history}

NOVÝ VSTUP:
{user_prompt}

Pravidlá:
- Ak nový vstup odpovedá na otázku asistenta → odpovedz: `POKRAČUJ`
- Ak nový vstup mení alebo spresňuje parametre tej istej nehnuteľnosti (napr. cena, počet izieb, rozloha, lokalita v tom istom meste, terasa, parkovanie, vybavenie, upresnenie preferencií ako poschodie, výhľad...), stále ide o rovnaký dopyt → odpovedz: `POKRAČUJ`
- Ak nový vstup naznačuje úplne inú nehnuteľnosť (HLAVNE iný typ bývania – dom/chalupa vs byt, mezonet vs byt, alebo zmena viacerých kľúčových parametrov naraz, ako cena výrazne vyššia, úplne iná lokalita alebo požiadavky na rozlohu) → odpovedz: `NOVÝ DOPYT`
- Ak nový vstup len pridáva alebo maže parametre (napr. cena, rozloha, počet izieb, záhrada, terasa, balkón, parkovanie, upresnenie lokality alebo poschodia), považuj to za ten istý dopyt → odpovedz: `POKRAČUJ`
- Ak nový vstup je iba jediné slovo týkajúce sa vybavenia alebo časti nehnuteľnosti (napr. "klimatizácia", "balkón", "garáž" atď.), považuj to stále za ten istý dopyt → odpovedz: `POKRAČUJ`

Dôležité:  
- Nepíš žiadne vysvetlenia, odpovedz **LEN** jedným slovom: `POKRAČUJ` alebo `NOVÝ DOPYT`
"""

summarize_chat_history_prompt = """
Na základe predchádzajúcej sumarizácie a nasledujúcej novej informácie aktualizuj a zhrň aktuálne preferencie používateľa ohľadom nehnuteľnosti do krátkeho odstavca.  
Zameraj sa IBA NA FAKTY a konkrétne požiadavky.  
Nepodávaj štylizovanú odpoveď – výstup má byť iba heslovité zhrnutie kľúčových parametrov!  
**Nezačínaj slovami ako "Používateľ preferuje" ani inými podobnými frázami.**  
**Nevysvetľuj motivácie používateľa.**

**Ak používateľ zmení dopyt (uvedie napr. „alebo radšej domček...“, prípadne zmení mnoho kľúčových parametrov naraz), vytvor NOVÝ DOPYT – neprepájaj ho s pôvodným.**  
**Ak niečo už nie je podmienkou, jednoducho to vynechaj. Nespomínaj to žiadnym spôsobom.**

Zachovaj logickú nadväznosť (napr. „zvýš cenu na 4000“ = nová cena je 4000).  
POZOR – uprav len existujúce údaje, ak sa týkajú rovnakého dopytu.  
POZOR – ak používateľ použije „alebo“, nahraď pôvodný údaj novým (napr. uvedie „alebo stačia len 2 izby“ – nahradíš pôvodný počet izieb novým uvedeným počtom) - V žiadnom prípade nepripájaj nový údaj k starému, iba ho nahraď !  
POZOR – ak používateľ vyradí požiadavku (použije slová ako napr. „nechcem“, „bez“,  „nemusí“, „netreba“, „vynechaj“), len ju vynechaj – **NEUVÁDZAJ, že nie je potrebná.**

Predchádzajúca sumarizácia:
{original_summary}

Nová informácia:  
{user_prompt}

Tvoje zhrnutie kľúčových údajov a preferencií:
"""

get_key_attributes_prompt = """Na základe nasledujúceho promptu používateľa vydedukuj hodnoty pre tieto premenné:

cena: <tvoja dedukcia> (uveď iba číslo. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najvyššiu hodnotu z rozsahu. Ak nie je možné určiť presné číslo, priraď hodnotu None.),

počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je v popise uvedený počet izieb nepriamo (napr. "dve spálne a pracovňa" alebo "2 spálne a 1 pracovňa"), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť presné číslo, priraď hodnotu None.). Ak je uvedený rozsah (napr. 2-3 izbovy byt), priraď hodnotu None, ,

počet izieb MIN: <tvoja dedukcia> (ak používateľ uvedie rozsah počtu izieb (napr. 2–3 izbový byt), použi minimálnu hranicu. Ak sa nedá určiť, alebo si už určil konkrétnu hodnotu počtu izieb, priraď hodnotu None),

počet izieb MAX: <tvoja dedukcia> (ak používateľ uvedie rozsah počtu izieb (napr. 2–3 izbový byt), použi maximálnu hranicu. Ak sa nedá určiť, alebo si už určil konkrétnu hodnotu počtu izieb, priraď hodnotu None),

rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený rozsah a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak nie je možné určiť presné číslo, priraď hodnotu None.),

typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "penthouse", "byt", "garzónka". Ak nie je možné určiť, priraď hodnotu None.),

novostavba: <tvoja dedukcia> (priraď hodnotu True, ak je z promptu zrejmé, že ide o novostavbu. Inak priraď hodnotu None.)

Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.

Prompt: {user_prompt}

Tvoj výstup:
"""

follow_up_questions_prompt = """Toto je dopyt používateľa ohľadom požadovanej nehnuteľnosti:  
{original_summary}

Toto sú vydedukované kľúčové údaje:  
{key_attributes}

Niektorým kľúčovým atribútom bola priradená hodnota *None*, pretože z používateľovho dopytu sa nedali jednoznačne určiť.  
Navrhni doplňujúce otázky, pomocou ktorých by sa dali tieto údaje získať.

Ak *žiadnemu* z atribútov nebola priradená hodnota *None*, polož otázky, ktoré pomôžu spresniť preferencie používateľa — napríklad, či má záujem o balkón, parkovanie, klimatizáciu a podobne. Buď kreatívny.
POZOR - polož najviac 2 otázky, ktoré považuješ za najdôležitejšie.
Výstup v tomto formate:
· <otázka 1>
· <otázka 2>

Tvoje otázky:
"""

agentic_flow_prompt ="""
Tvojou úlohou je získať a zhrnúť preferencie používateľa ohľadom ideálnej nehnuteľnosti na prenájom.

Primárne potrebuješ získať hodnoty pre tieto premenné:
- cena (nájom)
- počet izieb
- rozloha
- typ nehnuteľnosti (dom, loft, mezonet, penthouse, byt, garzónka)
- či ide o novostavbu

Kladiem ti nasledujúce požiadavky:

1. Ak už používateľ uviedol hodnotu pre niektorú premennú, už sa na ňu NIKDY nepýtaj znova (napríklad, ak už používateľ uviedol, že chce 3-izbový byt, nepýtaj sa znova na typ nehnuteľnosti a počet izieb!).
2. V jednej odpovedi polož najviac **2 otázky**.
3. NEPONÚKAJ riešenia, NEODPORÚČAJ realitky, NEPÍŠ o ďalších krokoch. Tvojou JEDINOU úlohou je klásť otázky a budovať obraz o preferenciách používateľa.
4. Ak už máš všetky hlavné hodnoty, pýtaj sa na doplnkové detaily ako napr. balkón, výhľad, poschodie, parkovanie, klimatizácia, zariadenie atď.
5. V rozhovore buď prirodzený, príjemný a rešpektujúci. Pomáhaj používateľovi vyjadriť svoje predstavy bez nátlaku.
6. Ak sa rozhovor zatúla mimo tému, jemne ho nasmeruj späť k preferenciám pre prenájom nehnuteľnosti.

Tvoj cieľ: získať všetky potrebné informácie, bez opakovania otázok, bez navrhovania riešení – iba otázkami.
"""