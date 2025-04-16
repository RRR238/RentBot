get_key_attributes_prompt = """Z nasledujúceho promptu vydedukuj hodnoty pre tieto premenné:

                                cena: <tvoja dedukcia> (uveď iba číslo. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najvyššiu hodnotu z rozsahu. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak je v popise uvedený počet izieb (napr. "dve spálne a pracovňa" alebo "2 spálne a 1 pracovňa"), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "byt", "garzonka". Ak nie je možné určiť, priraď hodnotu None.).
                                
                                novostavba: <tvoja dedukcia> (priraď iba hodnotu True. Ak nie je možné určiť, priraď hodnotu None.).
                    
                                Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.
                    
                                Prompt: {user_prompt}
                    
                                Tvoj výstup: """

get_location_info_prompt = """Z nasledujúceho používateľského vstupu extrahuj informáciu o polohe podľa týchto pravidiel:

1. Urči **hlavné miesto**, ktoré používateľ spomína (napr. "centrum Bratislavy", "Eurovea", "Dunaj", "Štrkovecké jazero",...).
   - Ak používateľ spomenie **viacero miest**, vyber to, ktoré **najviac vystupuje ako cieľ alebo zámer hľadania** (napr. ak povie "v Petržalke pri jazere", hlavný bod je "petržalské jazero").
   - POZOR: Ak používateľ povie **„do X min do centra MHD“**, chápe sa to ako „do X minút do **centra mesta** pomocou MHD“ → vtedy nastav `ústredná lokalita = centrum Bratislavy`.
   - Vždy uprednostni konkrétnu **destináciu** (napr. centrum mesta, obchodné centrum, štvrť) pred obecným mestom ("Bratislava").
   - Ak sa nedá určiť žiadny vhodný bod, uveď: `ústredná lokalita = None`.
   - Inak: `ústredná lokalita = <tvoja odpoveď>`

Používateľský vstup: "{user_prompt}"

Tvoj výstup:
ústredná lokalita = ...
"""

get_location_info_2_prompt = """Z nasledujúceho používateľského vstupu urci sekundarnu lokalitu, ak je to mozne, podla nasledujucich pravidiel:

1. Urči **hlavny bod**, ktoré používateľ spomína (napr. "Eurovea", "Dunaj", "Štrkovecké jazero",...).
   - Ak používateľ spomenie **viacero miest**, vyber to, ktoré **najviac vystupuje ako cieľ alebo zámer hľadania** (napr. ak povie "v Mocenku pri jazere", sekundarna lokalita je "mocenske jazero").
   - Sekundarna lokalita je bod v ramci primarnej lokality, uvedenej nizsie.
   - Ak sa nedá určiť žiadny vhodný bod, uveď: `ústredná lokalita = None`.
   - Inak: `ústredná lokalita = <tvoja odpoveď>`

Používateľský vstup: "{user_prompt}"
Primarna lokalita: "{primary_location}"

Tvoj výstup:
sekundarna lokalita = ...
"""