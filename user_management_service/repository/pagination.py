from dependencies import base_logger, get_session
from domain.base import OrderEnum, Pagination
from fastapi import Depends
from sqlalchemy import asc, desc, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession


class PaginationRepo:
    def __init__(self, session: AsyncSession = Depends(get_session)):
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
        except SQLAlchemyError as e:
            base_logger.info(
                f"Unknown SQLAlchemy error during pagination: {e}", exc_info=True
            )
            raise e
        except Exception as e:
            base_logger.info(f"Unknown error during pagination: {e}", exc_info=True)
            raise e

        return await self.session.scalars(query)
