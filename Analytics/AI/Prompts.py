get_key_attributes_prompt = """Z nasledujúceho promptu vydedukuj hodnoty pre tieto premenné:

cena: <tvoja dedukcia> (uveď iba číslo. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najvyššiu hodnotu z rozsahu. Ak nie je možné určiť presné číslo, priraď hodnotu None.),

počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je v popise uvedený počet izieb nepriamo (napr. "dve spálne a pracovňa" alebo "2 spálne a 1 pracovňa"), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť presné číslo, priraď hodnotu None.). Ak je uvedený rozsah (napr. 2-3 izbovy byt), priraď hodnotu None, ,

počet izieb MIN: <tvoja dedukcia> (ak používateľ uvedie rozsah počtu izieb (napr. 2–3 izbový byt), použi minimálnu hranicu. Ak sa nedá určiť, alebo si už určil konkrétnu hodnotu počtu izieb, priraď hodnotu None),

počet izieb MAX: <tvoja dedukcia> (ak používateľ uvedie rozsah počtu izieb (napr. 2–3 izbový byt), použi maximálnu hranicu. Ak sa nedá určiť, alebo si už určil konkrétnu hodnotu počtu izieb, priraď hodnotu None),

rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený rozsah a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak nie je možné určiť presné číslo, priraď hodnotu None.),

typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "byt", "garzónka". Ak nie je možné určiť, priraď hodnotu None.),

novostavba: <tvoja dedukcia> (priraď hodnotu True, ak je z promptu zrejmé, že ide o novostavbu. Inak priraď hodnotu None.)

Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.

Prompt: {user_prompt}

Tvoj výstup:
"""

get_location_info_prompt = """Z nasledujúceho používateľského vstupu urči **hlavné miesto alebo orientačný bod**, ktoré používateľ spomína (napr. "centrum Bratislavy", "Eurovea", "Dunaj", "Štrkovec", "Petržalka").

Pravidlá:
- Ak používateľ spomenie **viacero miest**, vyber to, ktoré **najviac vystupuje ako cieľ alebo zámer hľadania** (napr. ak povie "v Petržalke pri jazere", hlavný bod je "Petržalka").
- Ak používateľ povie **„do X min do centra MHD“**, chápe sa to ako „do X minút do **centra mesta** pomocou MHD“ → nastav `ústredná lokalita = centrum Bratislavy`.
- Vždy uprednostni konkrétnu **destináciu** (napr. štvrť, orientačný bod) pred obecným mestom ("Bratislava").
- Ak sa nedá určiť žiadny vhodný bod, uveď: `ústredná lokalita = None`.

Používateľský vstup: "{user_prompt}"

Tvoj výstup:
ústredná lokalita = ...
"""

get_location_info_2_prompt = """Podľa používateľského vstupu a známej ústrednej lokality urči, či používateľ myslí priestor **v rámci** tejto lokality, alebo **mimo nej / v jej okolí**.

Pravidlá:
- Ak používateľ píše výrazy ako „v {lokalita}“, „v rámci {lokalita}“, „v lokalite {lokalita}“, „v mestskej časti {lokalita}“ → nastav: `lokalizačný rozsah = VRAMCI`
- Ak používateľ píše výrazy ako „pri {lokalita}“, „blízko {lokalita}“, „neďaleko {lokalita}“, „v okolí {lokalita}“ → nastav: `lokalizačný rozsah = MIMO`
- V prípade nejednoznačnosti uveď `lokalizačný rozsah = None`

Používateľský vstup: "{user_prompt}"
Ústredná lokalita: "{lokalita}"

Tvoj výstup:
lokalizačný rozsah = ...
"""

location_extraction_prompt = """
Z nasledujúceho textu extrahuj všetky relevantné **lokality alebo orientačné body**, ktoré by mohli súvisieť s geografickou polohou. Môže ísť o:

- mestá alebo mestské časti (napr. "Ružinov", "Petržalka", "Senec"),
- ulice, štvrte, sídliská (napr. "Mlynské Nivy", "Dlhé diely"),
- jazerá, parky, hory, lesy (napr. "Štrkovec", "Sad Janka Kráľa"),
- obchodné centrá, pamiatky, dopravné uzly (napr. "Eurovea", "Hlavná stanica"),
- prípadne známe budovy alebo komplexy.

Výstup uveď ako **čistý python zoznam reťazcov**, bez komentárov a vysvetlení.
Davaj pozor aby udaje o polohe boli v gramaticky spravnom tvare !! (napr Zilina, centrum, Bratislava, centrum a podobne) 

Text: "{user_prompt}"

Výstup:
"""

location_scope_prompt = """Z nasledujúceho textu:
{user_prompt}

Bola vydedukovaná ako ústredná oblasť: {anchor_location}

Myslí sa v texte miesto VRÁMCI ústrednej oblasti, alebo MIMO (pri, blízko, kúsok) nej? Odpovedz iba slovom VRÁMCI alebo MIMO (napr. Domček na polosamote pri Žiline bude oznaceny ako MIMO)

Tvoj výstup:
"""
