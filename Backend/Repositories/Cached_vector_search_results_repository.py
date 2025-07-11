from sqlalchemy.ext.asyncio import AsyncSession
from Backend.Entities import Cached_vector_search_results
from sqlalchemy.sql import delete, select, func,  or_, and_

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
            max_price: int,
            min_size: int,
            max_size: int,
            property_types: list[str],
            rooms: list[int],
            page: int = 1,
            page_size: int = 20
    ):
        offset = (page - 1) * page_size

        # Base filters (common to all)
        filters = [
            Cached_vector_search_results.price_total <= max_price,
            Cached_vector_search_results.size >= min_size,
            Cached_vector_search_results.size <= max_size
        ]

        # Build type-specific filter logic
        if rooms and "flat" in property_types:
            filters.append(
                or_(
                    # Non-flat types are filtered only by property_type
                    Cached_vector_search_results.property_type.in_(
                        [pt for pt in property_types if pt != "flat"]
                    ),
                    # Flats are filtered by both type AND rooms
                    and_(
                        Cached_vector_search_results.property_type == "flat",
                        Cached_vector_search_results.rooms.in_(rooms)
                    )
                )
            )
        else:
            # No room filtering; apply only property_type filter
            filters.append(Cached_vector_search_results.property_type.in_(property_types))

        # Total count query
        count_stmt = select(func.count()).where(*filters)
        total_result = await self.db.execute(count_stmt)
        total_count = total_result.scalar()

        # Paginated offers query
        stmt = (
            select(
                Cached_vector_search_results.source_url,
                Cached_vector_search_results.location,
                Cached_vector_search_results.price_total,
                Cached_vector_search_results.title,
                Cached_vector_search_results.description
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