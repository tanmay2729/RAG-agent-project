"""
Generates synthetic business documents (invoices, purchase orders) for the
RAG demo. Mimics the kind of documents an ERP system like the one in the
Shree Radha Studio job posting would store. No external data or API needed
- fully free and offline.

Run: python data/generate_data.py
Output: data/sample_docs.json
"""

import json
import random
from pathlib import Path

random.seed(42)

VENDORS = ["Anand Textiles", "Meera Fabrics", "Suraj Dyeing Works", "Radhika Prints", "Kalpana Threads"]
ITEMS = ["Cotton Fabric", "Silk Fabric", "Zari Thread", "Sequin Sheets", "Dye - Red", "Dye - Blue", "Packaging Boxes", "Embroidery Kits"]
STATUSES = ["Paid", "Pending", "Overdue"]


def make_invoice(i: int) -> dict:
    vendor = random.choice(VENDORS)
    item = random.choice(ITEMS)
    qty = random.randint(10, 500)
    price = round(random.uniform(50, 2000), 2)
    total = round(qty * price, 2)
    status = random.choice(STATUSES)
    text = (
        f"Invoice #INV-{1000+i}. Vendor: {vendor}. "
        f"Item: {item}, Quantity: {qty} units, Unit Price: Rs.{price}, "
        f"Total Amount: Rs.{total}. Payment Status: {status}. "
        f"Issued on 2026-0{random.randint(1,9)}-{random.randint(10,28)}."
    )
    return {"id": f"INV-{1000+i}", "type": "invoice", "text": text}


def make_purchase_order(i: int) -> dict:
    vendor = random.choice(VENDORS)
    item = random.choice(ITEMS)
    qty = random.randint(20, 1000)
    text = (
        f"Purchase Order #PO-{2000+i}. Vendor: {vendor}. "
        f"Ordered Item: {item}, Quantity Requested: {qty} units. "
        f"Expected Delivery: within 7 business days. Approved by Operations."
    )
    return {"id": f"PO-{2000+i}", "type": "purchase_order", "text": text}


def main():
    docs = []
    for i in range(15):
        docs.append(make_invoice(i))
    for i in range(10):
        docs.append(make_purchase_order(i))

    out_path = Path(__file__).parent / "sample_docs.json"
    out_path.write_text(json.dumps(docs, indent=2))
    print(f"Wrote {len(docs)} documents to {out_path}")


if __name__ == "__main__":
    main()
