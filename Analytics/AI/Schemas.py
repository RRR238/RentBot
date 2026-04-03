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
            "Pravidlá v poradí priority: "
            "(1) Ak používateľ uviedol konkrétne pomenované mestské časti (napr. 'Petržalka', 'Ružinov', 'Karlova Ves'), uveď IBA tie. "
            "(2) Ak uviedol iba mesto (napr. 'Bratislava', 'Košice'), uveď mesto. "
            "(3) Ak uviedol mesto aj pomenované časti, uveď iba časti. "
            "POZOR: opisné frázy ako 'moderná štvrť', 'nový downtown', 'blízko centra', 'pri lese', 'tichá štvrť' NIE SÚ názvy lokalít — ignoruj ich tu (patria do ostatne_preferencie). "
            "Ak opisná fráza doprevádza konkrétne mesto (napr. 'v Bratislave, v modernej štvrti'), uveď mesto. "
            "Prázdny zoznam len ak lokalita nie je vôbec určená."
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
