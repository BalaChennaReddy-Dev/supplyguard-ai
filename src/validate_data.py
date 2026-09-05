from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_csv(filename):
    path = DATA_DIR / filename
    return pd.read_csv(path)


def validate():
    suppliers = load_csv("suppliers.csv")
    products = load_csv("products.csv")
    warehouses = load_csv("warehouses.csv")
    inventory = load_csv("inventory.csv")
    shipments = load_csv("shipments.csv")
    customers = load_csv("customers.csv")
    orders = load_csv("orders.csv")

    supplier_ids = set(suppliers["supplier_id"])
    product_ids = set(products["product_id"])
    warehouse_ids = set(warehouses["warehouse_id"])
    customer_ids = set(customers["customer_id"])

    errors = []

    # Products → Suppliers
    invalid = products[~products["supplier_id"].isin(supplier_ids)]
    if not invalid.empty:
        errors.append(
            f"Products with invalid suppliers: {len(invalid)}"
        )

    # Inventory → Products
    invalid = inventory[~inventory["product_id"].isin(product_ids)]
    if not invalid.empty:
        errors.append(
            f"Inventory with invalid products: {len(invalid)}"
        )

    # Inventory → Warehouses
    invalid = inventory[
        ~inventory["warehouse_id"].isin(warehouse_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Inventory with invalid warehouses: {len(invalid)}"
        )

    # Shipments → Suppliers
    invalid = shipments[
        ~shipments["supplier_id"].isin(supplier_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Shipments with invalid suppliers: {len(invalid)}"
        )

    # Shipments → Products
    invalid = shipments[
        ~shipments["product_id"].isin(product_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Shipments with invalid products: {len(invalid)}"
        )

    # Shipments → Warehouses
    invalid = shipments[
        ~shipments["warehouse_id"].isin(warehouse_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Shipments with invalid warehouses: {len(invalid)}"
        )

    # Orders → Customers
    invalid = orders[
        ~orders["customer_id"].isin(customer_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Orders with invalid customers: {len(invalid)}"
        )

    # Orders → Products
    invalid = orders[
        ~orders["product_id"].isin(product_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Orders with invalid products: {len(invalid)}"
        )

    # Orders → Warehouses
    invalid = orders[
        ~orders["warehouse_id"].isin(warehouse_ids)
    ]
    if not invalid.empty:
        errors.append(
            f"Orders with invalid warehouses: {len(invalid)}"
        )

    if errors:
        print("❌ DATA VALIDATION FAILED")
        for error in errors:
            print(f"- {error}")
        return False

    print("✅ DATA VALIDATION PASSED")
    print()
    print(f"Suppliers:  {len(suppliers)}")
    print(f"Products:   {len(products)}")
    print(f"Warehouses: {len(warehouses)}")
    print(f"Inventory:  {len(inventory)}")
    print(f"Shipments:  {len(shipments)}")
    print(f"Customers:  {len(customers)}")
    print(f"Orders:     {len(orders)}")

    return True


if __name__ == "__main__":
    validate()