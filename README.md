# Dosa Restaurant REST API

A FastAPI + SQLite REST API backend for a Dosa restaurant.
Supports full CRUD operations for customers, items, and orders.

## Design

- `init_db.py` - reads example_orders.json and creates db.sqlite with four relational tables
- `main.py` - FastAPI application that reads and writes from db.sqlite

### Database Schema

- `customers` - id, name, phone
- `items` - id, name, price
- `orders` - id, customer_id (FK), timestamp, notes
- `order_items` - order_id (FK), item_id (FK)

## Setup

pip install fastapi uvicorn
python3 init_db.py example_orders.json
uvicorn main:app --reload

Visit http://localhost:8000/docs to test all endpoints.

## Endpoints

- POST/GET/PUT/DELETE /customers
- POST/GET/PUT/DELETE /items
- POST/GET/PUT/DELETE /orders

## Requirements

Python 3.9+, fastapi, uvicorn