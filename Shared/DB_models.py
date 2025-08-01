from sqlalchemy import Column, BigInteger, Integer, SmallInteger, String, Text, Float, JSON, TIMESTAMP, ForeignKey
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from Shared.Declarative_base import Base
#from Backend.Backend_entities import Cached_vector_search_results

#Base = declarative_base()

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
    year_of_construction = Column(SmallInteger, nullable=True)
    approval_year = Column(SmallInteger, nullable=True)
    last_reconstruction_year = Column(SmallInteger, nullable=True)
    balconies = Column(SmallInteger, nullable=True)
    ownership = Column(Text, nullable=True)
    price_rent = Column(Integer, nullable=True)
    price_ms = Column(Float, nullable=True)
    price_energies = Column(SmallInteger, nullable=True)
    description = Column(Text, nullable=True)
    floor = Column(SmallInteger, nullable=True)
    positioning = Column(Text, nullable=True)
    other_properties = Column(JSONB, nullable=True)  # Use JSONB for PostgreSQL optimization
    source = Column(Text, nullable=True)
    source_url = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longtitude = Column(Float, nullable=True)
    price_total = Column(Integer, nullable=True)
    preview_image= Column(Text, nullable=True)

    cached_vector_search_results = relationship('Cached_vector_search_results',
                                                back_populates='rent_offer')

