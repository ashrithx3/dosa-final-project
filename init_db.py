"""
init_db.py

Reads example_orders.json and initializes db.sqlite with relational tables:
  - customers (id, name, phone)
  - items     (id, name, price)
  - orders    (id, customer_id, timestamp, notes)
  - order_items (order_id, item_id)
"""

import json
import sqlite3
import sys


def init_db(orders_path: str, db_path: str = "db.sqlite") -> None:
    """Create and populate the SQLite database from a JSON orders file."""
    with open(orders_path, "r", encoding="utf-8") as fh:
        orders = json.load(fh)

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    cur.executescript("""
        PRAGMA foreign_keys = ON;

        CREATE TABLE IF NOT EXISTS customers (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL,
            phone TEXT    NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS items (
            id    INTEGER PRIMARY KEY AUTOINCREMENT,
            name  TEXT    NOT NULL UNIQUE,
            price REAL    NOT NULL
        );

        CREATE TABLE IF NOT EXISTS orders (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            timestamp   INTEGER NOT NULL,
            notes       TEXT    NOT NULL DEFAULT ''
        );

        CREATE TABLE IF NOT EXISTS order_items (
            order_id INTEGER NOT NULL REFERENCES orders(id),
            item_id  INTEGER NOT NULL REFERENCES items(id),
            PRIMARY KEY (order_id, item_id)
        );
    """)

    for order in orders:
        # customers
        cur.execute(
            "INSERT OR IGNORE INTO customers (name, phone) VALUES (?, ?)",
            (order["name"], order["phone"]),
        )
        cur.execute("SELECT id FROM customers WHERE phone = ?", (order["phone"],))
        customer_id = cur.fetchone()[0]

        # orders
        cur.execute(
            "INSERT INTO orders (customer_id, timestamp, notes) VALUES (?, ?, ?)",
            (customer_id, order["timestamp"], order.get("notes", "")),
        )
        order_id = cur.lastrowid

        # items + order_items
        for item in order["items"]:
            cur.execute(
                "INSERT OR IGNORE INTO items (name, price) VALUES (?, ?)",
                (item["name"], item["price"]),
            )
            cur.execute("SELECT id FROM items WHERE name = ?", (item["name"],))
            item_id = cur.fetchone()[0]

            cur.execute(
                "INSERT OR IGNORE INTO order_items (order_id, item_id) VALUES (?, ?)",
                (order_id, item_id),
            )

    con.commit()
    con.close()
    print(f"Database initialized: {db_path}")


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "example_orders.json"
    init_db(path)