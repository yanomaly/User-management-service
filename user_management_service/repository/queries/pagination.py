from domain.base import OrderEnum, Pagination
from fastapi import HTTPException
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession


class PaginationRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def paginate(self, table, paginate_data: Pagination, filters: dict):
        order = None
        try:
            if paginate_data.order and paginate_data.order_by:
                order_type = desc if paginate_data.order is OrderEnum.DESC else asc
                order = order_type(getattr(table, paginate_data.order_by))
            page_start = (
                0
                if paginate_data.page == 1
                else (paginate_data.page - 1) * paginate_data.per_page
            )
            query = (
                select(table)
                .filter_by(**filters)
                .order_by(order)
                .slice(page_start, page_start + paginate_data.per_page)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

        return await self.session.scalars(query)
