from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Material, Attribute, AttributeIncompatibility, Supplier


async def _get_attr_id(db: AsyncSession, name: str) -> int:
    result = await db.execute(select(Attribute.id).where(Attribute.name == name))
    return result.scalar_one()


async def seed_data(db: AsyncSession) -> None:
    # Check if already seeded
    result = await db.execute(select(Material))
    if result.first():
        return

    # Materials (10)
    materials = [
        "denim", "cotton", "lycra", "polyester", "silk",
        "wool", "linen", "nylon", "viscose", "cashmere",
    ]
    for name in materials:
        db.add(Material(name=name))

    # Attributes (15 across 5 categories)
    attributes = [
        # SLEEVE_TYPE
        ("long sleeve", "SLEEVE_TYPE"),
        ("short sleeve", "SLEEVE_TYPE"),
        ("sleeveless", "SLEEVE_TYPE"),
        # NECKLINE
        ("crew neck", "NECKLINE"),
        ("v-neck", "NECKLINE"),
        ("mock neck", "NECKLINE"),
        # GARMENT_CATEGORY
        ("nightwear", "GARMENT_CATEGORY"),
        ("activewear", "GARMENT_CATEGORY"),
        ("casual", "GARMENT_CATEGORY"),
        ("formal", "GARMENT_CATEGORY"),
        # FIT
        ("slim", "FIT"),
        ("regular", "FIT"),
        ("oversized", "FIT"),
        # FEATURE
        ("with logo", "FEATURE"),
        ("with pocket", "FEATURE"),
        ("with zipper", "FEATURE"),
    ]
    for name, category in attributes:
        db.add(Attribute(name=name, category=category))

    # Flush to assign IDs
    await db.flush()

    # Incompatibility rules (5) — ordered pairs (id_1 < id_2)
    incompatible_pairs = [
        ("nightwear", "activewear"),
        ("formal", "activewear"),
        ("sleeveless", "long sleeve"),
        ("short sleeve", "long sleeve"),
        ("short sleeve", "sleeveless"),
    ]
    for name_a, name_b in incompatible_pairs:
        id_a = await _get_attr_id(db, name_a)
        id_b = await _get_attr_id(db, name_b)
        low, high = min(id_a, id_b), max(id_a, id_b)
        db.add(AttributeIncompatibility(attribute_id_1=low, attribute_id_2=high))

    # Sample suppliers (3)
    suppliers = [
        Supplier(name="Fabric Co Ltd", contact_info="contact@fabricco.com"),
        Supplier(name="Budget Textiles", contact_info="sales@budgettextiles.com"),
        Supplier(name="Premium Mills", contact_info="info@premiummills.com"),
    ]
    for s in suppliers:
        db.add(s)

    await db.commit()
