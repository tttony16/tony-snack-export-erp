import math
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.models.customer import Customer
from app.repositories.customer_repo import CustomerRepository
from app.schemas.common import PaginatedData
from app.schemas.customer import CustomerCreate, CustomerListParams, CustomerRead, CustomerUpdate
from app.utils.code_generator import generate_entity_code


class CustomerService:
    def __init__(self, db: AsyncSession):
        self.repo = CustomerRepository(db)

    async def create(self, data: CustomerCreate, user_id: uuid.UUID) -> Customer:
        seq = await self.repo.get_next_sequence()
        customer_code = generate_entity_code("CUS", seq)

        customer = Customer(
            customer_code=customer_code,
            **data.model_dump(),
            created_by=user_id,
            updated_by=user_id,
        )
        return await self.repo.create(customer)

    async def get_by_id(self, id: uuid.UUID) -> Customer:
        customer = await self.repo.get_by_id(id)
        if not customer:
            raise NotFoundError("客户", str(id))
        return customer

    async def update(self, id: uuid.UUID, data: CustomerUpdate, user_id: uuid.UUID) -> Customer:
        customer = await self.get_by_id(id)
        update_data = data.model_dump(exclude_unset=True)
        update_data["updated_by"] = user_id
        return await self.repo.update(customer, update_data)

    async def list_customers(self, params: CustomerListParams) -> PaginatedData[CustomerRead]:
        offset = (params.page - 1) * params.page_size
        items, total = await self.repo.search(
            keyword=params.keyword,
            country=params.country,
            offset=offset,
            limit=params.page_size,
            order_by=params.sort_by,
            order_desc=params.sort_order == "desc",
        )
        return PaginatedData(
            items=[CustomerRead.model_validate(item) for item in items],
            total=total,
            page=params.page,
            page_size=params.page_size,
            total_pages=math.ceil(total / params.page_size) if total > 0 else 0,
        )
