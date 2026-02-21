# Dosa Order Processor

## What it does
Reads a JSON file of restaurant orders and produces two output files:
- `customers.json` - maps phone numbers to customer names
- `items.json` - maps item names to price and order count

## Usage
```
python3 process_orders.py <orders_file.json>
```

## Example
```
python3 process_orders.py example_orders.json
```

## Requirements
Python 3.9+, no third-party packages needed.
