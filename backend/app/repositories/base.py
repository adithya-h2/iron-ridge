"""Generic async repository base class."""

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from sqlalchemy import Select, asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.schemas.common import PaginationParams

ModelT = TypeVar("ModelT")


@dataclass
class PaginatedResult(Generic[ModelT]):
    items: list[ModelT]
    total: int
    page: int
    page_size: int
    pages: int


class BaseRepository(Generic[ModelT]):
    """Async CRUD repository — no business logic."""

    model: type[ModelT]
    pk_column: str = "id"

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _pk_attr(self) -> Any:
        return getattr(self.model, self.pk_column)

    async def create(self, **kwargs: Any) -> ModelT:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, entity_id: Any) -> ModelT | None:
        result = await self.session.execute(
            select(self.model).where(self._pk_attr() == entity_id)
        )
        return result.scalar_one_or_none()

    async def get_by_id_or_raise(self, entity_id: Any) -> ModelT:
        entity = await self.get_by_id(entity_id)
        if entity is None:
            raise NotFoundError(
                f"{self.model.__name__} not found",
                details={"id": str(entity_id)},
            )
        return entity

    async def get_all(
        self,
        pagination: PaginationParams | None = None,
        filters: dict[str, Any] | None = None,
    ) -> PaginatedResult[ModelT]:
        pagination = pagination or PaginationParams()
        query: Select[tuple[ModelT]] = select(self.model)

        if filters:
            for key, value in filters.items():
                if value is not None and hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)

        if pagination.sort_by and hasattr(self.model, pagination.sort_by):
            col = getattr(self.model, pagination.sort_by)
            query = query.order_by(desc(col) if pagination.sort_order == "desc" else asc(col))

        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        pages = max(1, (total + pagination.page_size - 1) // pagination.page_size)
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages,
        )

    async def update(self, entity_id: Any, **kwargs: Any) -> ModelT:
        entity = await self.get_by_id_or_raise(entity_id)
        for key, value in kwargs.items():
            if value is not None and hasattr(entity, key):
                setattr(entity, key, value)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity_id: Any) -> None:
        entity = await self.get_by_id_or_raise(entity_id)
        await self.session.delete(entity)
        await self.session.flush()

    async def filter_by(self, **kwargs: Any) -> list[ModelT]:
        query = select(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.where(getattr(self.model, key) == value)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def search(
        self,
        term: str,
        columns: list[str],
        pagination: PaginationParams | None = None,
    ) -> PaginatedResult[ModelT]:
        pagination = pagination or PaginationParams()
        pattern = f"%{term}%"
        conditions = [
            getattr(self.model, col).ilike(pattern)
            for col in columns
            if hasattr(self.model, col)
        ]
        if not conditions:
            return PaginatedResult(items=[], total=0, page=1, page_size=pagination.page_size, pages=1)

        query = select(self.model).where(or_(*conditions))
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar_one()

        offset = (pagination.page - 1) * pagination.page_size
        query = query.offset(offset).limit(pagination.page_size)
        result = await self.session.execute(query)
        items = list(result.scalars().all())
        pages = max(1, (total + pagination.page_size - 1) // pagination.page_size)
        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            pages=pages,
        )
