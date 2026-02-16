from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    Material, Attribute, AttributeIncompatibility, Supplier,
    Garment, GarmentMaterial, GarmentAttribute, GarmentSupplier,
)


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

    await db.flush()

    # Helper to look up material ID by name
    async def _get_mat_id(name: str) -> int:
        result = await db.execute(select(Material.id).where(Material.name == name))
        return result.scalar_one()

    # Sample garments (4) across different lifecycle stages
    g1 = Garment(name="Classic Denim Jacket", description="A timeless denim jacket with modern fit", lifecycle_stage="DESIGN")
    g2 = Garment(name="Summer Cotton Tee", description="Lightweight cotton t-shirt for everyday wear", lifecycle_stage="CONCEPT")
    g3 = Garment(name="Silk Evening Blouse", description="Elegant silk blouse for formal occasions", lifecycle_stage="DEVELOPMENT")
    g4 = Garment(name="Wool Winter Coat", description="Heavy wool coat for cold weather", lifecycle_stage="SAMPLING")
    db.add_all([g1, g2, g3, g4])
    await db.flush()

    # Materials for each garment
    mat_denim = await _get_mat_id("denim")
    mat_cotton = await _get_mat_id("cotton")
    mat_lycra = await _get_mat_id("lycra")
    mat_silk = await _get_mat_id("silk")
    mat_polyester = await _get_mat_id("polyester")
    mat_wool = await _get_mat_id("wool")
    mat_nylon = await _get_mat_id("nylon")

    db.add_all([
        GarmentMaterial(garment_id=g1.id, material_id=mat_denim, percentage=85),
        GarmentMaterial(garment_id=g1.id, material_id=mat_lycra, percentage=15),
        GarmentMaterial(garment_id=g2.id, material_id=mat_cotton, percentage=95),
        GarmentMaterial(garment_id=g2.id, material_id=mat_polyester, percentage=5),
        GarmentMaterial(garment_id=g3.id, material_id=mat_silk, percentage=100),
        GarmentMaterial(garment_id=g4.id, material_id=mat_wool, percentage=70),
        GarmentMaterial(garment_id=g4.id, material_id=mat_nylon, percentage=30),
    ])

    # Attributes for each garment
    attr_long = await _get_attr_id(db, "long sleeve")
    attr_short = await _get_attr_id(db, "short sleeve")
    attr_sleeveless = await _get_attr_id(db, "sleeveless")
    attr_crew = await _get_attr_id(db, "crew neck")
    attr_vneck = await _get_attr_id(db, "v-neck")
    attr_casual = await _get_attr_id(db, "casual")
    attr_formal = await _get_attr_id(db, "formal")
    attr_regular = await _get_attr_id(db, "regular")
    attr_slim = await _get_attr_id(db, "slim")
    attr_pocket = await _get_attr_id(db, "with pocket")

    db.add_all([
        GarmentAttribute(garment_id=g1.id, attribute_id=attr_long),
        GarmentAttribute(garment_id=g1.id, attribute_id=attr_casual),
        GarmentAttribute(garment_id=g1.id, attribute_id=attr_regular),
        GarmentAttribute(garment_id=g1.id, attribute_id=attr_pocket),
        GarmentAttribute(garment_id=g2.id, attribute_id=attr_short),
        GarmentAttribute(garment_id=g2.id, attribute_id=attr_crew),
        GarmentAttribute(garment_id=g2.id, attribute_id=attr_casual),
        GarmentAttribute(garment_id=g2.id, attribute_id=attr_regular),
        GarmentAttribute(garment_id=g3.id, attribute_id=attr_sleeveless),
        GarmentAttribute(garment_id=g3.id, attribute_id=attr_vneck),
        GarmentAttribute(garment_id=g3.id, attribute_id=attr_formal),
        GarmentAttribute(garment_id=g3.id, attribute_id=attr_slim),
        GarmentAttribute(garment_id=g4.id, attribute_id=attr_long),
        GarmentAttribute(garment_id=g4.id, attribute_id=attr_casual),
        GarmentAttribute(garment_id=g4.id, attribute_id=attr_regular),
    ])

    # Supplier assignments
    db.add_all([
        GarmentSupplier(garment_id=g1.id, supplier_id=suppliers[0].id, status="SAMPLING", offer_price=45.00, lead_time_days=30),
        GarmentSupplier(garment_id=g1.id, supplier_id=suppliers[2].id, status="OFFERED", offer_price=52.00, lead_time_days=25),
        GarmentSupplier(garment_id=g3.id, supplier_id=suppliers[2].id, status="APPROVED", offer_price=78.00, lead_time_days=45),
        GarmentSupplier(garment_id=g4.id, supplier_id=suppliers[0].id, status="OFFERED", offer_price=95.00, lead_time_days=60),
        GarmentSupplier(garment_id=g4.id, supplier_id=suppliers[1].id, status="OFFERED", offer_price=82.00, lead_time_days=55),
    ])

    await db.commit()
