from sqlalchemy import Column, BigInteger, Integer, SmallInteger, String, Text, Float, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

Base = declarative_base()

class Rent_offer_model(Base):
    __tablename__ = "rent_offers"  # Change to the actual table name

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    title = Column(Text, nullable=False)
    location = Column(Text, nullable=False)
    property_type = Column(Text, nullable=False)
    property_status = Column(Text, nullable=False)
    rooms = Column(SmallInteger, nullable=True)
    size = Column(Float, nullable=True)
    approval_year = Column(SmallInteger, nullable=True)
    last_reconstruction_year = Column(SmallInteger, nullable=True)
    balconies = Column(SmallInteger, nullable=True)
    ownership = Column(Text, nullable=True)
    price_rent = Column(Integer, nullable=True)
    price_ms = Column(Float, nullable=True)
    price_energies = Column(SmallInteger, nullable=True)
    description = Column(Text, nullable=True)
    other_properties = Column(JSONB, nullable=True)  # Use JSONB for PostgreSQL optimization
    source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    coordinates = Column(Text, nullable=True)

class Offer_image_model(Base):
    __tablename__ = "images"  # Change to actual table name

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    image_url = Column(Text, nullable=False)
    rent_offer_id = Column(BigInteger, ForeignKey("rent_offers.id"), nullable=False)
