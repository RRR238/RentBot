from pydantic import BaseModel
from typing import List

class Key_attributes_interface(BaseModel):
    house: bool
    loft: bool
    mezonet: bool
    apartmen: bool
    flat: bool
    studio: bool
    double_studio: bool
    rooms: int | None
    size: float | None
    property_status: str | None

class Price_data_interface(BaseModel):
    rent: float| None
    meter_squared: float| None
    energies: float| None

class Property_data_interface(BaseModel):
    title: str | None
    location: str | None
    key_attributes: Key_attributes_interface
    year_of_construction: int | None
    approval_year: int | None
    last_reconstruction_year: int | None
    balconies: int | None
    ownership: str | None
    other_properties: List[str] | None
    prices: Price_data_interface
    floor: int | str | None
    positioning: str | None
    description: str | None
    images: List[str] | None
    coordinates: List[float] | None
    source_url:str
    source:str


property_data_list = List[Property_data_interface]