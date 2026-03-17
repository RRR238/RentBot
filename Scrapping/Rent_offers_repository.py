from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, exists, and_
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from Shared.DB_models import Rent_offer_model

class Rent_offers_repository:
    def __init__(self,
                 connection_string):

        self.connection_string = connection_string
        self.engine = create_engine(self.connection_string)
        self.session_local = scoped_session(
                                    sessionmaker(
                                    bind=self.engine))

    @contextmanager
    def get_session(self):
        """Opens a session and ensures it's closed after use"""
        session = self.session_local()
        try:
            yield session
        finally:
            session.close()

    def insert_rent_offer(self, rent_offer_model_data):

        with self.get_session() as session:
            try:
                new_property = Rent_offer_model(**rent_offer_model_data)
                session.add(new_property)
                session.commit()  # Ensure data is written to the DB
                session.refresh(new_property)  # Load generated fields (e.g., ID)
                print("✅ Property inserted successfully!")
                return new_property
            except SQLAlchemyError as e:
                session.rollback()  # Rollback if error occurs
                print(f"❌ Error inserting property: {e}")
                return None

    def record_exists(self, source_url: str) -> bool:
        with self.get_session() as session:
            return session.query(exists(
                                ).where(
                                Rent_offer_model.source_url == source_url)
                                ).scalar()

    def find_duplicates(self,
                        price_rent: float | None,
                        price_energies: float | None,
                        size: float | None,
                        rooms: int | None,
                        ownership: str | None,
                        lat: float | None,
                        lon: float | None,
                        url: str | None = None,
                        precision_coordinates:float=0.001,
                        precision_size:float=1):
        with self.get_session() as session:
            conditions = [
                Rent_offer_model.price_rent == price_rent,
                Rent_offer_model.price_energies == price_energies,
                Rent_offer_model.rooms == rooms,
                Rent_offer_model.ownership == ownership,
            ]

            if size is not None:
                conditions.append(Rent_offer_model.size >= size - precision_size)
                conditions.append(Rent_offer_model.size <= size + precision_size)
            else:
                conditions.append(Rent_offer_model.size == size)

            if lat is not None and lon is not None:
                conditions.append(Rent_offer_model.latitude >= lat - precision_coordinates)
                conditions.append(Rent_offer_model.latitude <= lat + precision_coordinates)
                conditions.append(Rent_offer_model.longtitude >= lon - precision_coordinates)
                conditions.append(Rent_offer_model.longtitude <= lon + precision_coordinates)

            if url:
                conditions.append(Rent_offer_model.source_url != url)

            return session.query(Rent_offer_model).filter(and_(*conditions)).all()

    def get_all_items(self):
        """Fetch all source_url values from the rent_offers table."""
        with self.get_session() as session:
            return [result for result in session.query(
                                        Rent_offer_model).all()]

    def get_all_source_urls(self):
        """Fetch all source_url values from the rent_offers table."""
        with self.get_session() as session:
            return [result[0] for result in session.query(
                                        Rent_offer_model.source_url).all()]

    def delete_by_source_urls(self, source_urls:list[str]):
        """Delete all records where source_url is in the given list."""
        with self.get_session() as session:
            session.query(Rent_offer_model).filter(
                Rent_offer_model.source_url.in_(source_urls)
            ).delete(synchronize_session=False)
            session.commit()

    def delete_by_ids(self, ids:list[int]):
        """Delete all records where source_url is in the given list."""
        with self.get_session() as session:
            session.query(Rent_offer_model).filter(
                Rent_offer_model.id.in_(ids)
            ).delete(synchronize_session=False)
            session.commit()

    def get_offer_by_id_or_url(self, identifier):
        with self.get_session() as session:
            if isinstance(identifier, int):
                # Assume it's an ID
                return session.query(Rent_offer_model
                                     ).filter(
                                        Rent_offer_model.id == identifier
                                        ).first()
            else:
                # Assume it's a URL
                return session.query(Rent_offer_model
                                     ).filter(
                                    Rent_offer_model.source_url == identifier
                                    ).first()

    def update_offer(self,
                     identifier,
                     updates: dict) -> bool:
        with (self.get_session() as session):
            if isinstance(identifier, int):
                offer = session.query(Rent_offer_model
                                      ).filter(Rent_offer_model.id == identifier
                                                                        ).first()
            else:
                offer = session.query(Rent_offer_model
                                      ).filter(Rent_offer_model.source_url == identifier
                                                                            ).first()

            if not offer:
                return False

            for key, value in updates.items():
                if hasattr(offer, key):
                    setattr(offer, key, value)

            session.commit()
            return True