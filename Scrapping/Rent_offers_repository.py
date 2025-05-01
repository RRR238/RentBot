from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import create_engine, exists, and_
from contextlib import contextmanager
from sqlalchemy.exc import SQLAlchemyError
from Shared.DB_models import Rent_offer_model, Offer_image_model

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

    def duplicate_exists(self, price: float, size: float, coordinates: str) -> bool:
        with self.get_session() as session:
            return session.query(
                exists().where(
                    and_(
                        Rent_offer_model.price_rent == price,
                        Rent_offer_model.coordinates == coordinates,
                        Rent_offer_model.size >= size - 1,
                        Rent_offer_model.size <= size + 1
                    )
                )
            ).scalar()

    def insert_offer_images(self, rent_offer_id: int, image_urls: list[str]):
        """Inserts multiple image URLs related to a specific rent offer."""
        if not image_urls:
            return  # Do nothing if the list is empty

        image_records = [Offer_image_model(image_url=url,
                                    rent_offer_id=rent_offer_id) for url in image_urls]

        with self.get_session() as session:
            session.add_all(image_records)
            session.commit()  # Save changes

    def get_all_source_urls(self):
        """Fetch all source_url values from the rent_offers table."""
        with self.get_session() as session:
            return [result[0] for result in session.query(
                                        Rent_offer_model.source_url).all()]

    def delete_by_source_urls(self, source_urls):
        """Delete all records where source_url is in the given list."""
        with self.get_session() as session:
            session.query(Rent_offer_model).filter(
                Rent_offer_model.source_url.in_(source_urls)
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
