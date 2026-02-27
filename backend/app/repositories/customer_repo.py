from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    def __init__(self, db: AsyncSession):
        super().__init__(Customer, db)

    async def get_by_code(self, customer_code: str) -> Customer | None:
        result = await self.db.execute(
            select(Customer).where(Customer.customer_code == customer_code)
        )
        return result.scalar_one_or_none()

    async def get_next_sequence(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Customer))
        count = result.scalar_one()
        return count + 1

    async def search(
        self,
        *,
        keyword: str | None = None,
        country: str | None = None,
        offset: int = 0,
        limit: int = 20,
        order_by: str = "created_at",
        order_desc: bool = True,
    ) -> tuple[list[Customer], int]:
        filters = []
        if keyword:
            filters.append(
                or_(
                    Customer.customer_code.ilike(f"%{keyword}%"),
                    Customer.name.ilike(f"%{keyword}%"),
                    Customer.short_name.ilike(f"%{keyword}%"),
                    Customer.contact_person.ilike(f"%{keyword}%"),
                )
            )
        if country:
            filters.append(Customer.country == country)

        return await self.get_list(
            offset=offset,
            limit=limit,
            order_by=order_by,
            order_desc=order_desc,
            filters=filters,
        )
