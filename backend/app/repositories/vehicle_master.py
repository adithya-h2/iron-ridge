"""Vehicle master repository."""

from sqlalchemy import select

from app.models.vehicle_master import VehicleMaster
from app.repositories.base import BaseRepository


class VehicleMasterRepository(BaseRepository[VehicleMaster]):
    model = VehicleMaster
    pk_column = "vehicle_id"

    async def get_by_category(self, category: str) -> list[VehicleMaster]:
        result = await self.session.execute(
            select(VehicleMaster).where(VehicleMaster.category == category)
        )
        return list(result.scalars().all())

    async def get_by_name_or_type(self, vehicle_type: str) -> VehicleMaster | None:
        result = await self.session.execute(
            select(VehicleMaster).where(
                (VehicleMaster.vehicle_name.ilike(f"%{vehicle_type}%"))
                | (VehicleMaster.category.ilike(f"%{vehicle_type}%"))
            )
        )
        return result.scalars().first()
