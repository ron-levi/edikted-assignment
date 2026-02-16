from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Material
from app.schemas.material import MaterialCreate


async def get_materials(db: AsyncSession) -> list[Material]:
    result = await db.execute(select(Material))
    return list(result.scalars().all())


async def create_material(db: AsyncSession, data: MaterialCreate) -> Material:
    material = Material(name=data.name)
    db.add(material)
    await db.commit()
    await db.refresh(material)
    return material
