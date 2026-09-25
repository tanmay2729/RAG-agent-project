"""
Mock inventory 'database' and lookup function.

Represents the kind of structured tool call an ERP-connected agent would
make (e.g. hitting a real PostgreSQL inventory table) instead of relying on
RAG over free text. Kept as a plain dict for the demo - free, no setup -
swap for a real database query in production.
"""

INVENTORY = {
    "Cotton Fabric": {"stock_units": 1200, "reorder_level": 300},
    "Silk Fabric": {"stock_units": 340, "reorder_level": 200},
    "Zari Thread": {"stock_units": 80, "reorder_level": 150},
    "Sequin Sheets": {"stock_units": 500, "reorder_level": 100},
    "Dye - Red": {"stock_units": 60, "reorder_level": 100},
    "Dye - Blue": {"stock_units": 220, "reorder_level": 100},
    "Packaging Boxes": {"stock_units": 900, "reorder_level": 400},
    "Embroidery Kits": {"stock_units": 45, "reorder_level": 50},
}


def lookup_inventory(item_name: str) -> dict | None:
    """Case-insensitive partial match against the mock inventory table."""
    for name, data in INVENTORY.items():
        if item_name.lower() in name.lower() or name.lower() in item_name.lower():
            below_reorder = data["stock_units"] < data["reorder_level"]
            return {
                "item": name,
                "stock_units": data["stock_units"],
                "reorder_level": data["reorder_level"],
                "needs_reorder": below_reorder,
            }
    return None
