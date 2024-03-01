from schemas import OrderEnum, Pagination
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession


async def paginate(
    table, session: AsyncSession, paginate_data: Pagination, filters=None
):
    if filters is None:
        filters = {}
    order = desc if paginate_data.order is OrderEnum.DESC else asc
    page_start = (
        0
        if paginate_data.page == 1
        else (paginate_data.page - 1) * paginate_data.per_page - 1
    )
    query = (
        select(table)
        .filter_by(**filters)
        .order_by(order(getattr(table, paginate_data.order_by)))
        .slice(page_start, paginate_data.per_page)
    )

    return await session.scalars(query)
