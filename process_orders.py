"""
process_orders.py

Reads a JSON file of restaurant orders and produces two output files:
  - customers.json  : mapping of phone numbers to customer names
  - items.json      : mapping of item names to price and order count
"""

import json
import sys


def format_phone(phone: str) -> str:
    """Normalize a phone number to xxx-xxx-xxxx format."""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 11 and digits[0] == "1":
        digits = digits[1:]
    if len(digits) != 10:
        raise ValueError(f"Cannot normalize phone number: {phone!r}")
    return f"{digits[:3]}-{digits[3:6]}-{digits[6:]}"


def process_orders(input_path: str) -> None:
    """Read orders from *input_path* and write customers.json / items.json."""
    with open(input_path, "r", encoding="utf-8") as fh:
        orders = json.load(fh)

    customers: dict[str, str] = {}
    items: dict[str, dict] = {}

    for order in orders:
        # --- customers ---
        phone = format_phone(order["phone"])
        customers[phone] = order["name"]

        # --- items ---
        for item in order["items"]:
            name = item["name"]
            price = item["price"]
            if name not in items:
                items[name] = {"price": price, "orders": 0}
            items[name]["orders"] += 1

    with open("customers.json", "w", encoding="utf-8") as fh:
        json.dump(customers, fh, indent=4)

    with open("items.json", "w", encoding="utf-8") as fh:
        json.dump(items, fh, indent=4)

    print(f"Processed {len(orders)} orders.")
    print(f"  Unique customers : {len(customers)}")
    print(f"  Unique items     : {len(items)}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python process_orders.py <orders_file.json>", file=sys.stderr)
        sys.exit(1)

    process_orders(sys.argv[1])


if __name__ == "__main__":
    main()