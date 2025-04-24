check_conversation_prompt = """
Tvojou úlohou je určiť, či sa nový vstup používateľa stále týka tej istej nehnuteľnosti ako predchádzajúca konverzácia, alebo ide o nový a samostatný dopyt.

ZHRNUTIE PREDCHÁDZAJÚCEJ KONVERZÁCIE:
{original_summary}

NOVÝ VSTUP:
{user_prompt}

Pravidlá:
- Ak nový vstup mení alebo spresňuje parametre tej istej nehnuteľnosti (napr. cena, počet izieb, rozloha, lokalita v tom istom meste, terasa, parkovanie, vybavenie...), stále ide o rovnaký dopyt → odpovedz: `POKRAČUJ`
- Ak nový vstup naznačuje úplne inú nehnuteľnosť (HLAVNE iný typ bývania – dom/chalupa vs byt, mezonet vs byt a podobne) kedy sa mení viacero kľúčových parametrov naraz, ide o nový dopyt → odpovedz: `NOVÝ DOPYT`
- Ak nový vstup len pridáva, alebo maže parametre (napr. cena, rozloha, počet izieb, záhrada, terasa, balkón, parkovanie, vybavenie, upresnenie lokality), považuj to za ten istý dopyt → `POKRAČUJ`

Pomôcky:
- Zmena z "1-izbový byt" na "2-izbový" = `POKRAČUJ`
- Zmena z "byt v Bratislave" na "chalupa pri Žiline" = `NOVÝ DOPYT`
- Zmena z "dom v Trnave" na "byt v Žiline" = `NOVÝ DOPYT`
- Zmena z "Petržalka, 1i byt, 400€" na "Karlova Ves, 2i novostavba, 900€" = `NOVÝ DOPYT`
- Vstup "netreba garáž" alebo "s balkónom" alebo "so záhradou" = `POKRAČUJ`
- Vstup "toto isté ale v Bratislave namiesto Nitry" = `POKRAČUJ`
- Vstup "alebo radšej dom s garážou v Nitre" = `NOVÝ DOPYT`
- Vstup "do "600 eur" = `POKRAČUJ`

Dôležité:  
Nepíš žiadne vysvetlenia, odpovedz **LEN** jedným slovom: `POKRAČUJ` alebo `NOVÝ DOPYT`
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
Tvojou úlohou je získať a následne zhrnúť preferencie používateľa ohľadom ideálnej nehnuteľnosti, ktorú si chce prenajať. 
Primárne sa zameraj na získanie hodnôt pre nasledujúce premenné:

- cena (nájom)
- počet izieb
- rozloha
- typ nehnuteľnosti (dom, loft, mezonet, penthouse, byt, garzónka)
- či ide o novostavbu

Snaž sa klásť otázky tak, aby z odpovedí bolo možné tieto hodnoty jednoznačne určiť. 
Ak už máš hodnotu danej premennej, alebo používateľ nevie / nechce odpovedať, viac sa na to nepýtaj. 
Nikdy neopakuj tú istú otázku.

Keď už poznáš všetky vyššie uvedené hodnoty, pokračuj v rozhovore doplňujúcimi otázkami — 
napríklad ohľadom balkóna, parkovacieho miesta, klimatizácie, výhľadu a iných praktických či komfortných prvkov. 
Buď prirodzený, prívetivý a rozhovor veď tak, aby sa používateľ cítil príjemne a podporovaný pri vyjadrovaní svojich predstáv.
"""