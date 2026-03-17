from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func,  or_, and_
from Backend.Database.Entity_registration import Rent_offer_model


class Offers_repository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_filtered_rent_offers(
            self,
            max_price: int,
            min_size: int,
            max_size: int,
            property_types: list[str],
            rooms: list[int],
            coordinates_bounding_boxes:list[dict],
            page: int = 1,
            page_size: int = 20
    ):
        offset = (page - 1) * page_size
        location_filters = []
        for box in coordinates_bounding_boxes:  # each box is a dict with north_lat, south_lat, east_lon, west_lon
            location_filters.append(and_(
                Rent_offer_model.latitude >= box['south_lat'],
                Rent_offer_model.latitude <= box['north_lat'],
                Rent_offer_model.longtitude >= box['west_lon'],
                Rent_offer_model.longtitude <= box['east_lon']
            ))
        # Base filters (common to all)
        filters = [
            Rent_offer_model.price_total <= max_price,
            Rent_offer_model.size >= min_size,
            Rent_offer_model.size <= max_size,
            or_(*location_filters)
        ]

        # Build type-specific filter logic
        if rooms and "flat" in property_types:
            filters.append(
                or_(
                    # Non-flat types are filtered only by property_type
                    Rent_offer_model.property_type.in_(
                        [pt for pt in property_types if pt != "flat"]
                    ),
                    # Flats are filtered by both type AND rooms
                    and_(
                        Rent_offer_model.property_type == "flat",
                        Rent_offer_model.rooms.in_(rooms)
                    )
                )
            )
        else:
            # No room filtering; apply only property_type filter
            filters.append(Rent_offer_model.property_type.in_(property_types))

        # Total count query
        count_stmt = select(func.count()).where(*filters)
        total_result = await self.db.execute(count_stmt)
        total_count = total_result.scalar()

        # Paginated offers query
        stmt = (
            select(
                Rent_offer_model.source_url,
                Rent_offer_model.location,
                Rent_offer_model.price_total,
                Rent_offer_model.title,
                Rent_offer_model.description,
                Rent_offer_model.preview_image
            )
            .where(*filters)
            .offset(offset)
            .limit(page_size)
        )
        result = await self.db.execute(stmt)
        offers = [dict(row._mapping) for row in result.fetchall()]

        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "offers": offers
        }