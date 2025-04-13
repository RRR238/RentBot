get_key_attributes_prompt = """Z nasledujúceho promptu vydedukuj hodnoty pre tieto premenné:

                                cena: <tvoja dedukcia> (uveď iba číslo. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                poloha: <tvoja dedukcia> (Uveď mesto A mestský obvod, ak je to možné. Ak nie je možné určiť PRESNE mesto a obvod, priraď hodnotu None.),
                    
                                počet izieb: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                rozloha: <tvoja dedukcia> (uveď iba číslo, ak je to možné. Ak nie je možné určiť presne číslo, priraď hodnotu None.),
                    
                                typ nehnuteľnosti: <tvoja dedukcia> (vyber iba jednu z nasledujúcich možností: "dom", "loft", "mezonet", "byt", "garzonka". Ak nie je možné určiť, priraď hodnotu None.).
                    
                                Ak niektoré hodnoty nie je možné určiť, priraď k danej premennej hodnotu None.
                    
                                Prompt: {user_prompt}
                    
                                Tvoj výstup: """