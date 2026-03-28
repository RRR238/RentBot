from typing import Optional

from pydantic import BaseModel


class KeyAttributes(BaseModel):
    house: bool = False
    loft: bool = False
    mezonet: bool = False
    apartmen: bool = False
    flat: bool = False
    studio: bool = False
    double_studio: bool = False
    rooms: Optional[int] = None
    size: Optional[float] = None
    property_status: Optional[str] = None


class Prices(BaseModel):
    rent: Optional[int] = None
    energies: Optional[int] = None
    meter_squared: Optional[float] = None


class PropertyDetail(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    key_attributes: KeyAttributes
    year_of_construction: Optional[int] = None
    approval_year: Optional[int] = None
    last_reconstruction_year: Optional[int] = None
    balconies: Optional[int] = None
    ownership: Optional[str] = None
    other_properties: dict
    prices: Prices
    floor: Optional[int] = None
    positioning: Optional[str] = None
    description: Optional[str] = None
    preview_image: Optional[str] = None
    coordinates: Optional[tuple] = None
    source_url: Optional[str] = None


class RentOfferInsert(BaseModel):
    title: Optional[str] = None
    location: Optional[str] = None
    property_type: Optional[str] = None
    property_status: Optional[str] = None
    rooms: Optional[int] = None
    size: Optional[float] = None
    year_of_construction: Optional[int] = None
    approval_year: Optional[int] = None
    last_reconstruction_year: Optional[int] = None
    balconies: Optional[int] = None
    ownership: Optional[str] = None
    price_rent: Optional[int] = None
    price_ms: Optional[float] = None
    price_energies: Optional[int] = None
    price_total: Optional[int] = None
    description: Optional[str] = None
    other_properties: Optional[dict] = None
    floor: Optional[int] = None
    positioning: Optional[str] = None
    source: Optional[str] = None
    source_url: Optional[str] = None
    latitude: Optional[float] = None
    longtitude: Optional[float] = None
    preview_image: Optional[str] = None


class PriceUpdate(BaseModel):
    price_rent: Optional[int] = None
    price_energies: Optional[int] = None


class ProcessingError(BaseModel):
    link: str
    error: str