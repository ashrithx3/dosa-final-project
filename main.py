"""
main.py

FastAPI REST API for the Dosa restaurant.
Provides CRUD endpoints for customers, items, and orders.
Reads and writes from db.sqlite.
"""

import sqlite3
from contextlib import contextmanager

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

DB_PATH = "db.sqlite"

app = FastAPI(title="Dosa Restaurant API")


# ---------------------------------------------------------------------------
# Database helper
# ---------------------------------------------------------------------------

@contextmanager
def get_db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    try:
        yield con
        con.commit()
    finally:
        con.close()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class CustomerIn(BaseModel):
    name: str
    phone: str


class CustomerOut(CustomerIn):
    id: int


class ItemIn(BaseModel):
    name: str
    price: float


class ItemOut(ItemIn):
    id: int


class OrderIn(BaseModel):
    customer_id: int
    timestamp: int
    notes: str = ""
    item_ids: list[int] = []


class OrderOut(BaseModel):
    id: int
    customer_id: int
    timestamp: int
    notes: str
    item_ids: list[int]


# ---------------------------------------------------------------------------
# Customers
# ---------------------------------------------------------------------------

@app.post("/customers", response_model=CustomerOut, status_code=201)
def create_customer(customer: CustomerIn):
    with get_db() as con:
        try:
            cur = con.execute(
                "INSERT INTO customers (name, phone) VALUES (?, ?)",
                (customer.name, customer.phone),
            )
            return CustomerOut(id=cur.lastrowid, **customer.model_dump())
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Phone number already exists")


@app.get("/customers/{id}", response_model=CustomerOut)
def get_customer(id: int):
    with get_db() as con:
        row = con.execute("SELECT * FROM customers WHERE id = ?", (id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerOut(**row)


@app.put("/customers/{id}", response_model=CustomerOut)
def update_customer(id: int, customer: CustomerIn):
    with get_db() as con:
        cur = con.execute(
            "UPDATE customers SET name = ?, phone = ? WHERE id = ?",
            (customer.name, customer.phone, id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Customer not found")
        return CustomerOut(id=id, **customer.model_dump())


@app.delete("/customers/{id}", status_code=204)
def delete_customer(id: int):
    with get_db() as con:
        cur = con.execute("DELETE FROM customers WHERE id = ?", (id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Customer not found")


# ---------------------------------------------------------------------------
# Items
# ---------------------------------------------------------------------------

@app.post("/items", response_model=ItemOut, status_code=201)
def create_item(item: ItemIn):
    with get_db() as con:
        try:
            cur = con.execute(
                "INSERT INTO items (name, price) VALUES (?, ?)",
                (item.name, item.price),
            )
            return ItemOut(id=cur.lastrowid, **item.model_dump())
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail="Item name already exists")


@app.get("/items/{id}", response_model=ItemOut)
def get_item(id: int):
    with get_db() as con:
        row = con.execute("SELECT * FROM items WHERE id = ?", (id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return ItemOut(**row)


@app.put("/items/{id}", response_model=ItemOut)
def update_item(id: int, item: ItemIn):
    with get_db() as con:
        cur = con.execute(
            "UPDATE items SET name = ?, price = ? WHERE id = ?",
            (item.name, item.price, id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")
        return ItemOut(id=id, **item.model_dump())


@app.delete("/items/{id}", status_code=204)
def delete_item(id: int):
    with get_db() as con:
        cur = con.execute("DELETE FROM items WHERE id = ?", (id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item not found")


# ---------------------------------------------------------------------------
# Orders
# ---------------------------------------------------------------------------

def _fetch_order(con: sqlite3.Connection, order_id: int) -> OrderOut:
    row = con.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Order not found")
    item_ids = [
        r[0]
        for r in con.execute(
            "SELECT item_id FROM order_items WHERE order_id = ?", (order_id,)
        ).fetchall()
    ]
    return OrderOut(id=row["id"], customer_id=row["customer_id"],
                    timestamp=row["timestamp"], notes=row["notes"],
                    item_ids=item_ids)


@app.post("/orders", response_model=OrderOut, status_code=201)
def create_order(order: OrderIn):
    with get_db() as con:
        # verify customer exists
        if con.execute("SELECT id FROM customers WHERE id = ?",
                       (order.customer_id,)).fetchone() is None:
            raise HTTPException(status_code=404, detail="Customer not found")

        cur = con.execute(
            "INSERT INTO orders (customer_id, timestamp, notes) VALUES (?, ?, ?)",
            (order.customer_id, order.timestamp, order.notes),
        )
        order_id = cur.lastrowid

        for item_id in order.item_ids:
            if con.execute("SELECT id FROM items WHERE id = ?",
                           (item_id,)).fetchone() is None:
                raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
            con.execute(
                "INSERT OR IGNORE INTO order_items (order_id, item_id) VALUES (?, ?)",
                (order_id, item_id),
            )

        return _fetch_order(con, order_id)


@app.get("/orders/{id}", response_model=OrderOut)
def get_order(id: int):
    with get_db() as con:
        return _fetch_order(con, id)


@app.put("/orders/{id}", response_model=OrderOut)
def update_order(id: int, order: OrderIn):
    with get_db() as con:
        cur = con.execute(
            "UPDATE orders SET customer_id = ?, timestamp = ?, notes = ? WHERE id = ?",
            (order.customer_id, order.timestamp, order.notes, id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")

        con.execute("DELETE FROM order_items WHERE order_id = ?", (id,))
        for item_id in order.item_ids:
            con.execute(
                "INSERT OR IGNORE INTO order_items (order_id, item_id) VALUES (?, ?)",
                (id, item_id),
            )

        return _fetch_order(con, id)


@app.delete("/orders/{id}", status_code=204)
def delete_order(id: int):
    with get_db() as con:
        con.execute("DELETE FROM order_items WHERE order_id = ?", (id,))
        cur = con.execute("DELETE FROM orders WHERE id = ?", (id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Order not found")