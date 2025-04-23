chat_history_summary_few_shots = [
    {
        "User": "Byt s dvomi spálňami a samostatnou pracovňou, s terasou a pivnicou. V tichej časti Petržalky, blízko lesoparku a MHD, do 950 €, výmera min. 80 m², možnosť prenájmu dlhodobo",
        "AI": "Trojizbový byt, terasa, pivnica, tichá časť Petržalky, blízko lesoparku a MHD, do 950 €, výmera min. 80 m², dlhodobý prenájom"
    },
    {
        "User": "Rozmyslel som si to, cena max do 600 eur",
        "AI": "Trojizbový byt, terasa, pivnica, tichá časť Petržalky, blízko lesoparku a MHD, do 600 €, výmera min. 80 m², dlhodobý prenájom"
    },
    {
        "User": "Bývanie by malo byť pet friendly",
        "AI": "Trojizbový byt, terasa, pivnica, tichá časť Petržalky, blízko lesoparku a MHD, do 600 €, výmera min. 80 m², dlhodobý prenájom, pet friendly"
    },
    {
        "User": "Podkrovný mezonet v historickom centre Trnavy s originálnymi trámami a výťahom v budove, cena do 1000 € mesačne, rozloha okolo 90 m²",
        "AI": "Podkrovný mezonet, historické centrum Trnavy, originálne trámy, výťah, do 1000 € mesačne, rozloha 90 m²"
    }
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