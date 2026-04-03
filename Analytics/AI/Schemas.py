from typing import Optional, Literal
from pydantic import BaseModel, Field

PropertyType = Literal["dom", "loft", "mezonet", "penthouse", "byt", "garzónka"]


class NumberRange(BaseModel):
    min: Optional[float] = Field(
        None,
        description=(
            "Dolná hranica rozsahu, null ak nie je určená. "
            "Ak je zadané jediné číslo bez spodnej hranice (napr. 'do 700€', 'max 700'), "
            "priraď ho do max a min nastav na null."
        ),
    )
    max: Optional[float] = Field(None, description="Horná hranica rozsahu, null ak nie je určená.")


class KeyAttributes(BaseModel):
    cena: NumberRange = Field(
        default_factory=NumberRange,
        description=(
            "Cenový rozsah mesačného nájmu. "
            "Ak používateľ uvedie jediné číslo alebo hornú hranicu (napr. '700 eur', 'do 800', 'max 900'), priraď ho ako MAX a MIN nastav na null. "
            "Ak používateľ uvedie rozsah (napr. '600-800', 'okolo 600-700'), priraď nižšie číslo ako MIN a vyššie ako MAX. "
            "NIKDY nepriraďuj rovnakú hodnotu obom. Ak nie je možné určiť žiadne číslo, priraď obom null."
        ),
    )
    pocet_izieb: NumberRange = Field(
        default_factory=NumberRange,
        description="Uveď rozsah počtu izieb. Ak nie je možné určiť rozsah, ale iba jediné číslo, priraď toto číslo ako hodnotu MIN a hodnote MAX priraď null. Ak je v popise uvedený počet izieb nepriamo (napr. 'dve spálne a pracovňa' alebo '2 spálne a 1 pracovňa'), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť rozsah ani konkrétne číslo, priraď obom hodnotám null.",
    )
    rozloha: NumberRange = Field(
        default_factory=NumberRange,
        description=(
            "Rozsah rozlohy v m². "
            "Ak používateľ uvedie jediné číslo alebo spodnú hranicu (napr. 'aspoň 60 m²', 'min 50'), priraď ho ako MIN a MAX nastav na null. "
            "Ak používateľ uvedie rozsah (napr. '50-70 m²', 'okolo 50-60'), priraď nižšie číslo ako MIN a vyššie ako MAX. "
            "NIKDY nepriraďuj rovnakú hodnotu obom. Ak nie je možné určiť žiadne číslo, priraď obom null."
        ),
    )
    typ_nehnutelnosti: list[PropertyType] = Field(
        default_factory=list,
        description="Typy nehnuteľností. Vyber všetky relevantné z: dom, loft, mezonet, penthouse, byt, garzónka. Prázdny zoznam ak typ nie je určený.",
    )
    novostavba: bool = Field(
        False,
        description="True len ak je jednoznačne jasné, že ide o novostavbu. Inak False.",
    )
    lokalita: list[str] = Field(
        default_factory=list,
        description=(
            "Zoznam lokalít: mestá alebo mestské časti. "
            "Ak používateľ uviedol konkrétne mestské časti (napr. 'Petržalka', 'Ružinov'), "
            "uveď IBA tie — nie nadradené mesto (teda nie 'Bratislava', ak sú časti known). "
            "Ak uviedol iba mesto bez konkrétnych častí, uveď mesto. "
            "Ak uviedol mesto aj časti, uveď iba časti. "
            "Ignoruj konkrétne body na mape ako 'pri jazere', 'pri lese', 'blízko centra', 'v tichej štvrti' — tie nepatria sem. "
            "Prázdny zoznam ak lokalita nie je určená."
        ),
    )
    ostatne_preferencie: str = Field(
        "",
        description=(
            "Volný text s ostatnými preferenciami používateľa, ktoré nepatria do iných polí "
            "(napr. balkón, parkovanie, poschodie, zariadenie, blízkosť MHD, domáce zviera, životný štýl). "
            "Nezahŕňaj sem cenu, počet izieb, rozlohu, typ nehnuteľnosti, novostavbu ani lokalitu — "
            "tie patria do vlastných polí. Ak žiadne ostatné preferencie nie sú, použi prázdny reťazec."
        ),
    )
