from pathlib import Path
from typing import Any
from datetime import datetime, timedelta

import pandas as pd


DATA_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
)


class ImpactEngine:
    """
    Deterministic supply-chain impact engine.

    Gemini interprets the disruption notice.
    This engine performs all operational calculations.
    """

    def __init__(self):
        self.suppliers = pd.read_csv(DATA_DIR / "suppliers.csv")
        self.products = pd.read_csv(DATA_DIR / "products.csv")
        self.warehouses = pd.read_csv(DATA_DIR / "warehouses.csv")
        self.inventory = pd.read_csv(DATA_DIR / "inventory.csv")
        self.shipments = pd.read_csv(DATA_DIR / "shipments.csv")
        self.orders = pd.read_csv(DATA_DIR / "orders.csv")
        self.customers = pd.read_csv(DATA_DIR / "customers.csv")

    # ---------------------------------------------------------
    # Basic data helpers
    # ---------------------------------------------------------

    def _find_shipments(
        self,
        supplier_id: str | None = None,
        product_ids: list[str] | None = None,
        shipment_id: str | None = None,
    ) -> pd.DataFrame:

        shipments = self.shipments[
            self.shipments["status"] == "in_transit"
        ].copy()

        if supplier_id:
            shipments = shipments[
                shipments["supplier_id"] == supplier_id
            ]

        if product_ids:
            shipments = shipments[
                shipments["product_id"].isin(product_ids)
            ]

        if shipment_id:
            shipments = shipments[
                shipments["shipment_id"] == shipment_id
            ]

        return shipments

    def _calculate_inventory(
        self,
        product_ids: list[str],
        warehouse_id: str | None = None,
    ) -> pd.DataFrame:

        inventory = self.inventory[
            self.inventory["product_id"].isin(product_ids)
        ].copy()

        if warehouse_id:
            inventory = inventory[
                inventory["warehouse_id"] == warehouse_id
            ]

        inventory["available_quantity"] = (
            inventory["quantity"]
            - inventory["reserved_quantity"]
        )

        return inventory

    def _calculate_orders(
        self,
        product_ids: list[str],
        warehouse_id: str | None = None,
    ) -> pd.DataFrame:

        orders = self.orders[
            (self.orders["status"] == "confirmed")
            & (self.orders["product_id"].isin(product_ids))
        ].copy()

        if warehouse_id:
            orders = orders[
                orders["warehouse_id"] == warehouse_id
            ]

        orders = orders.merge(
            self.customers[
                [
                    "customer_id",
                    "customer_name",
                    "customer_type",
                    "region",
                    "service_level",
                ]
            ],
            on="customer_id",
            how="left",
        )

        return orders

    # ---------------------------------------------------------
    # Inventory analysis
    # ---------------------------------------------------------

    def _build_inventory_summary(
        self,
        inventory: pd.DataFrame,
    ) -> list[dict[str, Any]]:

        if inventory.empty:
            return []

        grouped = inventory.groupby(
            ["warehouse_id", "product_id"],
            as_index=False
        ).agg(
            quantity=("quantity", "sum"),
            reserved_quantity=("reserved_quantity", "sum"),
            available_quantity=("available_quantity", "sum"),
        )

        result = []

        for _, row in grouped.iterrows():
            result.append(
                {
                    "warehouse_id": row["warehouse_id"],
                    "product_id": row["product_id"],
                    "quantity": int(row["quantity"]),
                    "reserved_quantity": int(
                        row["reserved_quantity"]
                    ),
                    "available_quantity": int(
                        row["available_quantity"]
                    ),
                }
            )

        return result

    # ---------------------------------------------------------
    # Order analysis
    # ---------------------------------------------------------

    def _build_order_summary(
        self,
        orders: pd.DataFrame,
        inventory_summary: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if orders.empty:
            return []

        grouped = orders.groupby(
            ["warehouse_id", "product_id"],
            as_index=False
        ).agg(
            ordered_quantity=("quantity", "sum")
        )

        result = []

        for _, row in grouped.iterrows():

            key = (
                row["warehouse_id"],
                row["product_id"],
            )

            available = 0

            for inventory in inventory_summary:

                inventory_key = (
                    inventory["warehouse_id"],
                    inventory["product_id"],
                )

                if inventory_key == key:
                    available = inventory[
                        "available_quantity"
                    ]
                    break

            ordered = int(row["ordered_quantity"])

            shortage = max(
                0,
                ordered - available
            )

            result.append(
                {
                    "warehouse_id": row["warehouse_id"],
                    "product_id": row["product_id"],
                    "ordered_quantity": ordered,
                    "available_quantity": available,
                    "shortage_quantity": shortage,
                }
            )

        return result

    def _identify_at_risk_orders(
        self,
        orders: pd.DataFrame,
        order_summary: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        if orders.empty:
            return []

        availability = {}

        for item in order_summary:

            key = (
                item["warehouse_id"],
                item["product_id"],
            )

            availability[key] = {
                "remaining":
                    item["available_quantity"]
            }

        orders = orders.sort_values(
            by=["required_date", "order_id"]
        )

        at_risk = []

        for _, order in orders.iterrows():

            key = (
                order["warehouse_id"],
                order["product_id"],
            )

            remaining = availability.get(
                key,
                {"remaining": 0}
            )["remaining"]

            quantity = int(order["quantity"])

            fulfillable = min(
                quantity,
                max(0, remaining)
            )

            shortage = quantity - fulfillable

            if key in availability:
                availability[key]["remaining"] -= (
                    fulfillable
                )

            if shortage > 0:

                at_risk.append(
                    {
                        "order_id":
                            order["order_id"],
                        "customer_id":
                            order["customer_id"],
                        "customer_name":
                            order["customer_name"],
                        "customer_type":
                            order["customer_type"],
                        "service_level":
                            order["service_level"],
                        "product_id":
                            order["product_id"],
                        "warehouse_id":
                            order["warehouse_id"],
                        "quantity":
                            quantity,
                        "fulfillable_quantity":
                            fulfillable,
                        "shortage_quantity":
                            shortage,
                        "required_date":
                            order["required_date"],
                        "order_date":
                            order["order_date"],
                    }
                )

        return at_risk

    # ---------------------------------------------------------
    # Customer analysis
    # ---------------------------------------------------------

    def _unique_customers(
        self,
        at_risk_orders: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        result = []
        seen = set()

        for order in at_risk_orders:

            customer_id = order["customer_id"]

            if customer_id in seen:
                continue

            seen.add(customer_id)

            result.append(
                {
                    "customer_id":
                        customer_id,
                    "customer_name":
                        order["customer_name"],
                    "customer_type":
                        order["customer_type"],
                    "service_level":
                        order["service_level"],
                }
            )

        return result

    # ---------------------------------------------------------
    # Carrier-delay calculation
    # ---------------------------------------------------------

    def _calculate_carrier_delay(
        self,
        shipments: pd.DataFrame,
        delay_days: int,
    ) -> list[dict[str, Any]]:

        result = []

        for _, shipment in shipments.iterrows():

            original_date = datetime.strptime(
                shipment["expected_date"],
                "%Y-%m-%d"
            )

            new_date = (
                original_date
                + timedelta(days=delay_days)
            )

            result.append(
                {
                    "shipment_id":
                        shipment["shipment_id"],
                    "supplier_id":
                        shipment["supplier_id"],
                    "product_id":
                        shipment["product_id"],
                    "warehouse_id":
                        shipment["warehouse_id"],
                    "quantity":
                        int(shipment["quantity"]),
                    "original_expected_date":
                        shipment["expected_date"],
                    "delay_days":
                        delay_days,
                    "projected_expected_date":
                        new_date.strftime("%Y-%m-%d"),
                }
            )

        return result

    # ---------------------------------------------------------
    # Warehouse incident
    # ---------------------------------------------------------

    def _potential_warehouse_orders(
        self,
        warehouse_id: str,
    ) -> list[dict[str, Any]]:

        orders = self.orders[
            (
                self.orders["warehouse_id"]
                == warehouse_id
            )
            & (
                self.orders["status"]
                == "confirmed"
            )
        ].copy()

        if orders.empty:
            return []

        orders = orders.merge(
            self.customers[
                [
                    "customer_id",
                    "customer_name",
                    "customer_type",
                    "service_level",
                ]
            ],
            on="customer_id",
            how="left",
        )

        result = []

        for _, order in orders.iterrows():

            result.append(
                {
                    "order_id":
                        order["order_id"],
                    "customer_id":
                        order["customer_id"],
                    "customer_name":
                        order["customer_name"],
                    "customer_type":
                        order["customer_type"],
                    "service_level":
                        order["service_level"],
                    "product_id":
                        order["product_id"],
                    "warehouse_id":
                        order["warehouse_id"],
                    "quantity":
                        int(order["quantity"]),
                    "required_date":
                        order["required_date"],
                    "risk_status":
                        "potential",
                    "reason":
                        "Order is fulfilled by a warehouse "
                        "with an active incident, but the "
                        "affected inventory section is not "
                        "specified.",
                }
            )

        return result

    # ---------------------------------------------------------
    # Main disruption-aware analysis
    # ---------------------------------------------------------

    def analyze_disruption(
        self,
        extraction: dict[str, Any],
        resolved: dict[str, Any],
    ) -> dict[str, Any]:

        event_type = extraction.get(
            "event_type",
            "unknown"
        )

        supplier = resolved.get("supplier")
        products = resolved.get("products", [])
        warehouse = resolved.get("warehouse")
        shipment = resolved.get("shipment")

        supplier_id = (
            supplier["supplier_id"]
            if supplier
            else None
        )

        product_ids = [
            product["product_id"]
            for product in products
        ]

        warehouse_id = (
            warehouse["warehouse_id"]
            if warehouse
            else None
        )

        shipment_id = (
            shipment["shipment_id"]
            if shipment
            else None
        )

        # -------------------------------------------------
        # Guard against ambiguous / unmapped notices
        # -------------------------------------------------

        if (
            not supplier_id
            and not product_ids
            and not warehouse_id
            and not shipment_id
        ):

            return {
                "event_type": event_type,
                "impact_found": False,
                "impact_status": "no_impact",
                "reason": (
                    "The disruption notice could not be "
                    "reliably mapped to pending operational "
                    "data. No impact was inferred."
                ),
                "affected_shipments": [],
                "inventory_summary": [],
                "order_summary": [],
                "at_risk_orders": [],
                "potentially_affected_orders": [],
                "affected_customers": [],
            }

        # -------------------------------------------------
        # Shipment lookup
        # -------------------------------------------------

        # For supplier production shutdowns, a supplier alone
        # is not enough to determine which shipments are affected.
        #
        # We require either:
        #   1. a specific product, or
        #   2. a specific shipment.
        #
        # This prevents the system from incorrectly assuming
        # that every shipment from a disrupted supplier is affected.

        if event_type == "production_shutdown":

            if product_ids or shipment_id:
                shipments = self._find_shipments(
                    supplier_id=supplier_id,
                    product_ids=product_ids,
                    shipment_id=shipment_id,
                )
            else:
                shipments = pd.DataFrame(
                    columns=self.shipments.columns
                )

        else:

            shipments = self._find_shipments(
                supplier_id=supplier_id,
                product_ids=product_ids,
                shipment_id=shipment_id,
            )

        # -------------------------------------------------
        # Carrier delay
        # -------------------------------------------------

        delayed_shipments = []

        if event_type == "carrier_delay":

            delay_days = extraction.get(
                "duration_days"
            ) or 0

            delayed_shipments = (
                self._calculate_carrier_delay(
                    shipments,
                    int(delay_days),
                )
            )

        # -------------------------------------------------
        # Supplier shutdown
        # -------------------------------------------------

        elif event_type == "production_shutdown":

            # We know these shipments are connected to
            # the affected supplier/products, but we do
            # NOT invent a delay duration.
            for _, row in shipments.iterrows():

                delayed_shipments.append(
                    {
                        "shipment_id":
                            row["shipment_id"],
                        "supplier_id":
                            row["supplier_id"],
                        "product_id":
                            row["product_id"],
                        "warehouse_id":
                            row["warehouse_id"],
                        "quantity":
                            int(row["quantity"]),
                        "original_expected_date":
                            row["expected_date"],
                        "projected_expected_date":
                            None,
                        "risk_status":
                            "potential_delay",
                    }
                )

        # -------------------------------------------------
        # Warehouse incident
        # -------------------------------------------------

        potentially_affected_orders = []

        if (
            event_type == "warehouse_incident"
            and warehouse_id
        ):

            potentially_affected_orders = (
                self._potential_warehouse_orders(
                    warehouse_id
                )
            )

        # -------------------------------------------------
        # Inventory
        # -------------------------------------------------

        inventory = pd.DataFrame()

        if product_ids:

            inventory = self._calculate_inventory(
                product_ids,
                warehouse_id,
            )

        inventory_summary = (
            self._build_inventory_summary(
                inventory
            )
        )

        # -------------------------------------------------
        # Orders
        # -------------------------------------------------

        orders = pd.DataFrame()

        if product_ids:

            orders = self._calculate_orders(
                product_ids,
                warehouse_id,
            )

        order_summary = self._build_order_summary(
            orders,
            inventory_summary,
        )

        at_risk_orders = (
            self._identify_at_risk_orders(
                orders,
                order_summary,
            )
        )

        affected_customers = (
            self._unique_customers(
                at_risk_orders
            )
        )

        # -------------------------------------------------
        # Determine impact
        # -------------------------------------------------

        impact_found = bool(
            delayed_shipments
            or at_risk_orders
            or potentially_affected_orders
        )

        if not impact_found:

            impact_status = "no_impact"

            if (
                event_type == "production_shutdown"
                and supplier_id
                and not product_ids
                and not shipment_id
            ):
                reason = (
                    "The supplier was identified, but the "
                    "notice did not specify an affected product "
                    "or shipment. No shipment-level impact was "
                    "inferred."
                )
            else:
                reason = (
                    "The disruption was mapped to the "
                    "operational data, but no pending "
                    "shipment or customer order is currently "
                    "shown to be impacted."
                )

        elif at_risk_orders:

            impact_status = "confirmed_impact"

            reason = (
                "The disruption is associated with "
                "operational dependencies and one or more "
                "customer orders have insufficient "
                "available inventory."
            )

        elif potentially_affected_orders:

            impact_status = "potential_impact"

            reason = (
                "Orders depend on the affected warehouse, "
                "but the disruption notice does not identify "
                "the exact inventory section. Impact is "
                "therefore reported as potential rather "
                "than confirmed."
            )

        else:

            impact_status = "supply_impact"

            reason = (
                "The disruption affects one or more "
                "pending inbound shipments, but no "
                "confirmed customer shortage was calculated."
            )

        return {
            "event_type":
                event_type,

            "impact_found":
                impact_found,

            "impact_status":
                impact_status,

            "reason":
                reason,

            "supplier":
                supplier,

            "products":
                products,

            "warehouse":
                warehouse,

            "affected_shipments":
                delayed_shipments,

            "inventory_summary":
                inventory_summary,

            "order_summary":
                order_summary,

            "at_risk_orders":
                at_risk_orders,

            "potentially_affected_orders":
                potentially_affected_orders,

            "affected_customers":
                affected_customers,
        }