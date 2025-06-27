from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import class_mapper
from sqlalchemy import select, func
from Shared.DB_models import Rent_offer_model


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
            page: int = 1,
            page_size: int = 20
    ):
        offset = (page - 1) * page_size

        # Filters
        filters = (
            Rent_offer_model.price_total <= max_price,
            Rent_offer_model.size >= min_size,
            Rent_offer_model.size <= max_size,
            Rent_offer_model.property_type.in_(property_types),
            Rent_offer_model.rooms.in_(rooms)
        )

        # Total count query
        count_stmt = select(func.count()).where(*filters)
        total_result = await self.db.execute(count_stmt)
        total_count = total_result.scalar()

        # Paginated results query
        stmt = (
            select(
                Rent_offer_model.source_url,
                Rent_offer_model.location,
                Rent_offer_model.price_total
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