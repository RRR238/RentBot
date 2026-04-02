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
        description="Uveď cenový rozsah. Ak používateľ uvedie jediné číslo bez spodnej hranice (napr. '700 eur', 'do 800'), priraď ho ako MAX a MIN nastav na null — NIKDY nepriraďuj rovnakú hodnotu obom. Ak nie je možné určiť žiadne číslo, priraď obom hodnotám null.",
    )
    pocet_izieb: NumberRange = Field(
        default_factory=NumberRange,
        description="Uveď rozsah počtu izieb. Ak nie je možné určiť rozsah, ale iba jediné číslo, priraď toto číslo ako hodnotu MIN a hodnote MAX priraď null. Ak je v popise uvedený počet izieb nepriamo (napr. 'dve spálne a pracovňa' alebo '2 spálne a 1 pracovňa'), uveď počet izieb na základe uvedených miestností. Ak nie je možné určiť rozsah ani konkrétne číslo, priraď obom hodnotám null.",
    )
    rozloha: NumberRange = Field(
        default_factory=NumberRange,
        description="Uveď rozsah. Ak nie je možné určiť rozsah, ale iba jediné číslo, priraď toto číslo ako hodnotu MIN a hodnote MAX priraď null. Ak nie je možné určiť rozsah ani konkrétne číslo, priraď obom hodnotám null.",
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
        description="Zoznam miest alebo mestských častí (nie konkrétne body na mape). Prázdny zoznam ak nie je určená.",
    )
