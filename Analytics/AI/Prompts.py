summarize_chat_history_prompt_v_2 = """
Na základe histórie konverzácie medzi agentom a používateľom nizsie (text medzi symbolmi ```), doplň a aktualizuj sumarizáciu preferencií (text medzi symbomi ''') používateľa ohľadom nehnuteľnosti.
Tvoja odpoveď musí byť v nasledujúcom formáte:

cena: <tvoja dedukcia>, počet izieb: <tvoja dedukcia>, rozloha: <tvoja dedukcia>, typ nehnuteľnosti: <tvoja dedukcia>, stav nehnuteľnosti: <tvoja dedukcia>, lokalita: <tvoja dedukcia>, ostatné preferencie: <tvoja dedukcia>

Pravidlá:

- Zohľadni celú konverzáciu od začiatku až po koniec.

- Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.

- Priraď hodnoty iba k uvedeným kategóriám! Nevytváraj nové kategórie.

- Ak používateľ nemá preferenciu ohľadom nejakého kritéria, alebo vyslovene uvedie, že niečo nechce alebo nepotrebuje (používa slová ako „nechcem“, „neviem“, „netreba“, „je mi to jedno“ a podobne), neuvádzaj toto kritérium do kategórie „ostatné preferencie“.

- Pri kategórii „stav nehnuteľnosti“ iba uveď: novostavba / staršia stavba / bez striktneho vymedzenia (alebo None, ak sa nedá určiť). Nedopĺňaj žiadne ďalšie informácie o stave stavby do kategórie „ostatné preferencie“.

História konverzácie medzi agentom a používateľom:
```{conversation_history}```

Aktuálna sumarizácia preferencií:
'''{original_summary}'''

Aktualizovaná sumarizácia preferencií:

"""

summarize_chat_history_prompt_v_3 = """
Na základe histórie konverzácie medzi agentom a používateľom nizsie (text medzi symbolmi ```), doplň a aktualizuj sumarizáciu preferencií (text medzi symbomi ''') používateľa ohľadom nehnuteľnosti.
Tvoja odpoveď musí byť v nasledujúcom formáte:

cena: <tvoja dedukcia>, počet izieb: <tvoja dedukcia>, rozloha: <tvoja dedukcia>, typ nehnuteľnosti: <tvoja dedukcia>, novostavba: <tvoja dedukcia> (priraď hodnotu True, ak je z promptu zrejmé, že ide o novostavbu. Inak priraď hodnotu None.), lokalita: <tvoja dedukcia> (Urči iba mesto alebo mestskú časť. Konkrétne body na mape, ako napr. „pri lese“, „pri jazere“, a podobne zaraď do kategórie ostatné preferencie), ostatné preferencie: <tvoja dedukcia>

Pravidlá:

- Zohľadni celú konverzáciu od začiatku až po koniec.

- Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.

- Priraď hodnoty iba k uvedeným kategóriám! Nevytváraj nové kategórie.

- Ak používateľ uvedie, že nechce/nepotrebuje nejakú preferenciu, ktorá už je zahrnutá v sumarizácii, tak ju odtiaľ len odstráň.

- Ak používateľ uvedie, že chce zmeniť nejakú preferenciu, ktorá už je zahrnutá v sumarizácii, tak ju zmeň podľa požiadavky používateľa.

História konverzácie medzi agentom a používateľom:
```{conversation_history}```

Aktuálna sumarizácia preferencií:
'''{original_summary}'''

Aktualizovaná sumarizácia preferencií:

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
4. Ak už máš hodnoty pre všetky HLAVNÉ premenné, pýtaj sa na doplnkové detaily ako napr. poloha,balkón,poschodie,parkovanie,pivnica,klimatizácia,zariadenie,občianska vybavenosť, dostupnosť MHD atď. - Vymysli si rôzne doplnkové otázky týkajúce sa exteriéru aj interiéru.
5. Vždy pokladaj iba konkrétne otázky týkajúce sa nejakého kritéria alebo detailu – nepýtaj sa všeobecné otázky typu „aké máte ďalšie preferencie?“, „chceli by ste ešte niečo doplniť?“ a podobne.
6. Nepýtaj sa zbytočností ako napr. či má mať budova výťah, aký typ podlahy používateľ preferuje, aké vysoké stropy a podobne.
6. V odpovedi neuvádzaj sumarizáciu doterajších požiadaviek používateľa !
7. Ak používateľ nemá preferenciu alebo nevie odpovedať, prejdi na ďalšiu otázku.

Tvoj cieľ: získať všetky potrebné informácie, bez opakovania otázok, bez navrhovania riešení – iba otázkami.
"""