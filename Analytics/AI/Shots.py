from Prompts import get_key_attributes_prompt

chat_history_summary_few_shots = [
    {
        "role": "system",
        "content": """Tvojou úlohou je upraviť aktuálne preferencie používateľa ohľadom hľadanej nehnuteľnosti.

Pravidlá:
- Z aktuálnych preferencií vždy vynechaj tie, ktoré:
    - majú negatívne vymedzenie (napr. používateľ niečo nechce alebo nepotrebuje. ❗️ POZOR: Výrazy ako „pre bandu alkoholikov“, „pre partiu kokotov“, „na žúry“ alebo iné subjektívne či kontroverzné požiadavky **nepovažuj za negatívne preferencie** — tieto ponechaj.),
    - majú neurčité vymedzenie (napr. používateľ si nie je istý).
    - opisujú stav nehnuteľnosti (novostavba, starší byt, zrekonštruovaný byt a podobne)
- Všetky pozitívne preferencie zachovaj – nič nevynechávaj.
- Nepíš nič naviac – iba skopíruj komplet všetky preferencie (nič nevynechaj) a uprav ich podľa uvedených pravidiel."""
    },
    {
        "role": "user",
        "content": "blízko prírody a jazera, bez potreby parkovacieho miesta, vhodný pre rodinu s deťmi, klimatizácia, balkón, netreba pivnicu"
    },
    {
        "role": "assistant",
        "content": "blízko prírody a jazera, vhodný pre rodinu s deťmi, klimatizácia, balkón"
    },
    {
        "role": "user",
        "content": "dobrá občianska vybavenosť, nemusí to byť novostavba, blízko centra, priestranný byt, bez preferencie ohľadom vybavenia, parkovacie miesto"
    },
    {
        "role": "assistant",
        "content": "dobrá občianska vybavenosť, blízko centra, priestranný byt, parkovacie miesto"
    },
    {
        "role": "user",
        "content": "útulný, jednoduchý, blízko prírody, domáce zviera povolené, netreba záhradu, bez klimatizácie, nepotrebuje garáž"
    },
    {
        "role": "assistant",
        "content": "útulný, jednoduchý, blízko prírody, domáce zviera povolené"
    },
    {
        "role": "user",
        "content": "luxusný, plne zariadený, nemusí mať balkón, pekný výhľad, klimatizácia, bez potreby výťahu"
    },
    {
        "role": "assistant",
        "content": "luxusný, plne zariadený, pekný výhľad, klimatizácia"
    }
]