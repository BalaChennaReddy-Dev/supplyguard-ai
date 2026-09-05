from typing import Any


class EvidenceEngine:
    """
    Builds traceable evidence records from deterministic
    supply-chain analysis results.

    Every evidence item contains:
    - source dataset
    - record identifier
    - factual explanation
    """

    @staticmethod
    def create_evidence(
        source: str,
        record_id: str,
        fact: str,
    ) -> dict[str, str]:
        if not source:
            raise ValueError("Evidence source cannot be empty.")

        if not record_id:
            raise ValueError("Evidence record_id cannot be empty.")

        if not fact:
            raise ValueError("Evidence fact cannot be empty.")

        return {
            "source": source,
            "record_id": str(record_id),
            "fact": fact,
        }

    def order_evidence(
        self,
        order: dict[str, Any],
    ) -> list[dict[str, str]]:
        evidence = []

        order_id = order.get("order_id")
        customer_id = order.get("customer_id")
        product_id = order.get("product_id")
        warehouse_id = order.get("warehouse_id")

        quantity = order.get("quantity")
        fulfillable_quantity = order.get(
            "fulfillable_quantity",
            0,
        )
        shortage_quantity = order.get(
            "shortage_quantity",
            0,
        )
        required_date = order.get("required_date")

        if order_id:
            evidence.append(
                self.create_evidence(
                    source="orders.csv",
                    record_id=str(order_id),
                    fact=(
                        f"Order {order_id} requires "
                        f"{quantity} units of {product_id} "
                        f"from warehouse {warehouse_id} "
                        f"by {required_date}."
                    ),
                )
            )

        if warehouse_id and product_id:
            evidence.append(
                self.create_evidence(
                    source="inventory.csv",
                    record_id=f"{warehouse_id}:{product_id}",
                    fact=(
                        f"Warehouse {warehouse_id} currently has "
                        f"{fulfillable_quantity} units available "
                        f"for this order after existing reservations."
                    ),
                )
            )

        if shortage_quantity > 0:
            evidence.append(
                self.create_evidence(
                    source="orders.csv",
                    record_id=str(order_id),
                    fact=(
                        f"The order has a shortage of "
                        f"{shortage_quantity} units."
                    ),
                )
            )

        if customer_id:
            evidence.append(
                self.create_evidence(
                    source="customers.csv",
                    record_id=str(customer_id),
                    fact=(
                        f"Customer {customer_id} is associated "
                        f"with this affected order."
                    ),
                )
            )

        return evidence

    def shipment_evidence(
        self,
        shipment: dict[str, Any],
    ) -> dict[str, str]:
        shipment_id = shipment.get("shipment_id")

        expected_date = shipment.get(
            "original_expected_date",
            shipment.get("expected_date"),
        )

        quantity = shipment.get("quantity")
        product_id = shipment.get("product_id")
        warehouse_id = shipment.get("warehouse_id")

        return self.create_evidence(
            source="shipments.csv",
            record_id=str(shipment_id),
            fact=(
                f"Shipment {shipment_id} contains "
                f"{quantity} units of {product_id} "
                f"for warehouse {warehouse_id}, "
                f"with expected arrival {expected_date}."
            ),
        )

    def inventory_evidence(
        self,
        inventory: dict[str, Any],
    ) -> dict[str, str]:
        warehouse_id = inventory.get("warehouse_id")
        product_id = inventory.get("product_id")

        quantity = inventory.get("quantity", 0)
        reserved_quantity = inventory.get(
            "reserved_quantity",
            0,
        )

        available = quantity - reserved_quantity

        return self.create_evidence(
            source="inventory.csv",
            record_id=f"{warehouse_id}:{product_id}",
            fact=(
                f"Warehouse {warehouse_id} has {quantity} total "
                f"units of {product_id}, with {reserved_quantity} "
                f"reserved and {available} available."
            ),
        )