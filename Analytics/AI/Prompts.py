summarize_chat_history_prompt = """
Na základe histórie konverzácie, predchádzajúcej sumarizácie a nasledujúcej novej informácie, aktualizuj a stručne zhrň aktuálne preferencie používateľa ohľadom nehnuteľnosti do krátkeho odstavca.  
Zameraj sa IBA NA FAKTY a konkrétne požiadavky.  
Nepodávaj štylizovanú odpoveď – výstup má byť iba heslovité zhrnutie kľúčových parametrov!  
**Nezačínaj slovami ako "Používateľ preferuje" ani inými podobnými frázami.**  
**Nevysvetľuj motivácie používateľa.**

**Ak používateľ zmení dopyt (uvedie napr. „alebo radšej domček...“, prípadne zmení mnoho kľúčových parametrov naraz), vytvor NOVÝ DOPYT – neprepájaj ho s pôvodným.**  

Zachovaj logickú nadväznosť (napr. „zvýš cenu na 4000“ = nová cena je 4000).  
POZOR – uprav len existujúce údaje, ak sa týkajú rovnakého dopytu.  
POZOR – ak používateľ použije „alebo“, nahraď pôvodný údaj novým (napr. uvedie „alebo stačia len 2 izby“ – nahradíš pôvodný počet izieb novým uvedeným počtom) - V žiadnom prípade nepripájaj nový údaj k starému, iba ho nahraď !

História konverzácie:
{conversation_history}

Predchádzajúca sumarizácia:
{original_summary}

Nová informácia:  
{user_prompt}

Tvoje zhrnutie kľúčových údajov a preferencií:
"""

summarize_chat_history_prompt_v_2 = """
Na základe histórie konverzácie, predchádzajúcej sumarizácie a nasledujúcej novej informácie, aktualizuj a stručne zhrň aktuálne preferencie používateľa ohľadom nehnuteľnosti.  
Tvoja odpoveď musí byť v nasledujúcom formáte:  
cena: <tvoja dedukcia>, počet izieb: <tvoja dedukcia>, počet izieb MIN: <tvoja dedukcia>, počet izieb MAX: <tvoja dedukcia>, rozloha: <tvoja dedukcia>, typ nehnuteľnosti: <tvoja dedukcia>, novostavba: <tvoja dedukcia>, lokalita: <tvoja dedukcia>, ostatné preferencie: <tvoja dedukcia>  

Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.
**Priraď hodnoty iba k uvedeným kategóriám! Nevytváraj nové kategórie.**
**Ak používateľ nemá preferenciu ohľadom nejakého kritéria, alebo vyslovene uvedie, že niečo nechce alebo nepotrebuje, NEUVÁDZAJ toto kritérium v tvojej odpovedi nijakým spôsobom !!!**

História konverzácie:  
{conversation_history}

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

lokalita: <tvoja dedukcia> (Urči iba mesto alebo mestskú časť. Ignoruj konkrétne body na mape, ako napr. „pri lese“, „pri jazere“, „blízko prírody“ a podobne. Ak nie je možné určiť, priraď hodnotu None.)

Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.

Prompt: {user_prompt}

Tvoj výstup:
"""

agentic_flow_prompt ="""
Tvojou úlohou je získať a zhrnúť preferencie používateľa ohľadom ideálnej nehnuteľnosti na prenájom.

*Primárne potrebuješ získať hodnoty pre tieto HLAVNÉ premenné*:
- cena (nájom)
- počet izieb
- rozloha
- novostavba

Kladiem ti nasledujúce požiadavky:

1. Ak už používateľ uviedol hodnotu pre niektorú premennú, už sa na ňu NIKDY nepýtaj znova (napríklad, ak už používateľ uviedol, že chce 3-izbový byt, nepýtaj sa znova na typ nehnuteľnosti a počet izieb!).
2. V jednej odpovedi polož najviac **1 otázku**.
3. NEPONÚKAJ riešenia, NEODPORÚČAJ realitky, NEPÍŠ o ďalších krokoch, NEHOVOR, že hľadáš pre používateľa nehnuteľnosť Tvojou JEDINOU úlohou je klásť otázky a budovať obraz o preferenciách používateľa.
4. Ak už máš hodnoty pre všetky HLAVNÉ premenné, pýtaj sa na doplnkové detaily ako napr. poloha,balkón,poschodie,parkovanie,klimatizácia,zariadenie ,atď. - Vymysli si čo najviac rôznych doplnkových otázok týkajúcich sa exteriéru aj interiéru.
5. Vždy pokladaj iba konkrétne otázky týkajúce sa nejakého kritéria alebo detailu – nepýtaj sa všeobecné otázky typu „aké máte ďalšie preferencie?“, „chceli by ste ešte niečo doplniť?“ a podobne.
6. V odpovedi neuvádzaj sumarizáciu doterajších požiadaviek používateľa !
7. Ak používateľ nemá preferenciu alebo nevie odpovedať, prejdi na ďalšiu otázku. 
8. Rozhovor neukončuj. Iba sa pýtaj otázky.

Tvoj cieľ: získať všetky potrebné informácie, bez opakovania otázok, bez navrhovania riešení – iba otázkami.
"""