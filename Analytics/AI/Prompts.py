get_key_attributes_prompt = """Z nasledujúceho promptu vydedukuj hodnoty pre tieto premenné:

                                cena: <tvoja dedukcia> (uveď iba číslo. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najvyššiu hodnotu z rozsahu. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak je v popise uvedený počet izieb (napr. "dve spálne a pracovňa" alebo "2 spálne a 1 pracovňa"), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "byt", "garzonka". Ak nie je možné určiť, priraď hodnotu None.).
                                
                                novostavba: <tvoja dedukcia> (priraď iba hodnotu True. Ak nie je možné určiť, priraď hodnotu None.).
                    
                                Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.
                    
                                Prompt: {user_prompt}
                    
                                Tvoj výstup: """

get_location_info_prompt = """Z nasledujúceho používateľského vstupu:

                            1. Urči **hlavné miesto alebo orientačný bod**, ktoré používateľ spomína (napr. "centrum Bratislavy", "Eurovea", "Dunaj").
                               - Ak sa nedá určiť, uveď: `anchor_location = None`
                               - Inak: `anchor_location = <tvoja odpoveď>`
                            
                            2. Urči, či používateľ hovorí o:
                               - presnej oblasti - v takom prípade uveď `location_scope = within`
                               - alebo o jej okolí, predmestí, blízkosti (používa slová ako napr. pri, blízko a podobne...) - v takom prípade uveď `location_scope = outskirts`
                            
                            3. Ak ide o "outskirts", urči vzdialenostnú kategóriu, ktorú pravdepodobne zamýšľa:
                               - 1 = do 15 minút pešo (~1.5 km)
                               - 2 = do 10 minút MHD (~3 km)
                               - 3 = do 10 minút autom (~5-7 km)
                               - 4 = do 30 minút autom (~15 km)
                               - Ak nehovorí o outskirts, uveď `distance_category = None`
                            
                            Používateľský vstup: "{user_prompt}"
                            
                            Tvoj výstup v tomto formáte:
                            anchor_location = ...
                            location_scope = ...
                            distance_category = ... """