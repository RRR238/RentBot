get_key_attributes_prompt = """Z nasledujúceho promptu vydedukuj hodnoty pre tieto premenné:

                                cena: <tvoja dedukcia> (uveď iba číslo. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najvyššiu hodnotu z rozsahu. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak je v popise uvedený počet izieb (napr. "dve spálne a pracovňa" alebo "2 spálne a 1 pracovňa"), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak je uvedený ROZSAH a nie konkrétne číslo, použi najnižšiu hodnotu z rozsahu. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "byt", "garzonka". Ak nie je možné určiť, priraď hodnotu None.).
                                
                                novostavba: <tvoja dedukcia> (priraď iba hodnotu True. Ak nie je možné určiť, priraď hodnotu None.).
                    
                                Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.
                    
                                Prompt: {user_prompt}
                    
                                Tvoj výstup: """