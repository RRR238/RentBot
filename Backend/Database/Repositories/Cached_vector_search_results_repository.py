from sqlalchemy.ext.asyncio import AsyncSession
from Backend.Database.Entity_registration import Cached_vector_search_results
from sqlalchemy.sql import delete, select, func,  or_, and_
from Shared.DB_models import Rent_offer_model
from sqlalchemy.orm import aliased

class Cached_vector_search_results_repository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_item(self,
                        new_cached_result:Cached_vector_search_results
                        )->Cached_vector_search_results:
        self.db.add(new_cached_result)
        await self.db.commit()
        await self.db.refresh(new_cached_result)
        return new_cached_result

    async def delete_items_by_session_id(self,
                                         session_id:int):
        await self.db.execute(
            delete(Cached_vector_search_results
                   ).where(
                Cached_vector_search_results.session_id == session_id)
                )
        await self.db.commit()

    async def get_filtered_vector_search_results(
            self,
            session_id: int,
            max_price: int,
            min_size: int,
            max_size: int,
            property_types: list[str],
            rooms: list[int],
            page: int = 1,
            page_size: int = 20
    ):
        offset = (page - 1) * page_size

        Offer = aliased(Rent_offer_model)
        Cached = Cached_vector_search_results

        # Base filters on offer attributes
        filters = [
            Offer.price_total <= max_price,
            Offer.size >= min_size,
            Offer.size <= max_size,
            Cached.session_id == session_id  # 🔸 Add session filter
        ]

        # Conditional room/property type filter
        if rooms and "flat" in property_types:
            filters.append(
                or_(
                    Offer.property_type.in_([pt for pt in property_types if pt != "flat"]),
                    and_(
                        Offer.property_type == "flat",
                        Offer.rooms.in_(rooms)
                    )
                )
            )
        else:
            filters.append(Offer.property_type.in_(property_types))

        # Count total results
        count_stmt = (
            select(func.count())
            .select_from(Offer)
            .join(Cached, Cached.offer_id == Offer.id)
            .where(*filters)
        )
        total_result = await self.db.execute(count_stmt)
        total_count = total_result.scalar()

        # Query offers with sorting by score DESC
        stmt = (
            select(
                Offer.source_url,
                Offer.location,
                Offer.price_total,
                Offer.title,
                Offer.preview_image,
                Cached.score  # Optional: include score in result
            )
            .join(Cached, Cached.offer_id == Offer.id)
            .where(*filters)
            .order_by(Cached.score.desc())  # 🔸 Sort by score descending
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
