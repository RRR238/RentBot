from Prompts import get_key_attributes_prompt

chat_history_summary_few_shots = [
    {
        "role": "system",
        "content": "Tvojou úlohou je zhrnúť aktuálne preferencie používateľa ohľadom nehnuteľnosti. Každý nový vstup môže spresniť, zmeniť alebo úplne nahradiť predchádzajúce požiadavky."
    },
    {
        "role": "user",
        "content": "Byt s dvomi spálňami a samostatnou pracovňou, s terasou a pivnicou. V tichej časti Petržalky, blízko lesoparku a MHD, do 950 €, výmera min. 80 m², možnosť prenájmu dlhodobo"
    },
    {
        "role": "assistant",
        "content": "Trojizbový byt, terasa, pivnica, tichá časť Petržalky, blízko lesoparku a MHD, do 950 €, výmera min. 80 m², dlhodobý prenájom"
    },
    {
        "role": "user",
        "content": "Rozmyslel som si to, stačia mi 2 izby"
    },
    {
        "role": "assistant",
        "content": "Dvojizbový byt, terasa, pivnica, tichá časť Petržalky, blízko lesoparku a MHD, do 600 €, výmera min. 80 m², dlhodobý prenájom"
    },
    {
        "role": "user",
        "content": "Netreba terasu, ani pivnicu"
    },
    {
        "role": "assistant",
        "content": "Dvojizbový byt, tichá časť Petržalky, blízko lesoparku a MHD, do 600 €, výmera min. 80 m², dlhodobý prenájom"
    },
    {
        "role": "user",
        "content": "Podkrovný mezonet v historickom centre Trnavy s originálnymi trámami a výťahom v budove, cena do 1000 € mesačne, rozloha okolo 90 m²"
    },
    {
        "role": "assistant",
        "content": "Podkrovný mezonet, historické centrum Trnavy, originálne trámy, výťah, do 1000 € mesačne, rozloha 90 m²"
    }
]

extract_key_attributes_shots = [
{"role": "system", "content": "You are an assistant that extracts structured information about locations from user queries in Slovak language."},
 {"role": "user", "content": get_key_attributes_prompt.format(user_prompt="Byt s dvomi spálňami a samostatnou pracovňou, s terasou a pivnicou. V tichej časti Petržalky, blízko lesoparku a MHD, do 950 €, výmera min. 80 m², možnosť prenájmu dlhodobo")},
 {"role": "assistant", "content": """cena: 950
počet izieb: 3
počet izieb MIN: None
počet izieb MAX: None
rozloha: 80
typ nehnuteľnosti: byt
novostavba: None"""}
]

prompt_classification_few_shots = [
    {"role": "system",
     "content": "Určuješ, či sa nový vstup týka tej istej nehnuteľnosti (0), alebo ide o nový dopyt (1)."},

    {"role": "user",
     "content": "ZHRNUTIE: Mezonet v Nitre, 1000 €, 85 m²\nNOVÝ VSTUP: S balkónom a pekným výhľadom"},
    {"role": "assistant", "content": "POKRAČUJ"},

    {"role": "user",
     "content": "ZHRNUTIE: Mezonet v Nitre, 1000 €, 85 m² s balkónom a pekným výhľadom\nNOVÝ VSTUP: Byt s dvomi spálňami v Petržalke"},
    {"role": "assistant", "content": "NOVÝ DOPYT"},

    {"role": "user", "content": "ZHRNUTIE: Byt v Petržalke, 950 €, 80 m²\nNOVÝ VSTUP: S balkónom a pivnicou"},
    {"role": "assistant", "content": "POKRAČUJ"},

    {"role": "user",
     "content": "ZHRNUTIE: Byt v Petržalke, 950 €, 80 m² s balkónom a pivnicou\nNOVÝ VSTUP: Útulný 1-izbový byt v Ružinove, 550 €"},
    {"role": "assistant", "content": "NOVÝ DOPYT"},
]

agentic_flow_few_shots = [
    {
        "role": "system",
        "content": """Tvojou úlohou je získať a následne zhrnúť preferencie používateľa ohľadom ideálnej nehnuteľnosti, ktorú si chce prenajať. 
Primárne sa zameraj na získanie hodnôt pre nasledujúce premenné:
\n\n- cena (nájom)\n- počet izieb\n- rozloha\n- typ nehnuteľnosti (jedna alebo viac z možností: dom, loft, mezonet, penthouse, byt, garzónka)\n- či ide o novostavbu
\n\nSnaž sa klásť otázky tak, aby z odpovedí bolo možné tieto hodnoty jednoznačne určiť. Ak už máš hodnotu danej premennej, alebo používateľ nevie / nechce odpovedať, viac sa na to nepýtaj. 
**Nikdy neopakuj tú istú otázku.**\n\nKeď už poznáš všetky vyššie uvedené hodnoty, 
pokračuj v rozhovore doplňujúcimi otázkami — napríklad ohľadom balkóna, parkovacieho miesta, klimatizácie, výhľadu a iných praktických či komfortných prvkov. 
Buď prirodzený, prívetivý a rozhovor veď tak, aby sa používateľ cítil príjemne a podporovaný pri vyjadrovaní svojich predstáv."""
    }

]