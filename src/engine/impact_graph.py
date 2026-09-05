
from pathlib import Path
from typing import Any

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"


class ImpactGraphBuilder:
    """
    Deterministic supply-chain impact graph builder.

    The graph is derived only from operational data already
    identified by the impact and priority engines.

    Gemini is not used here.
    """

    def __init__(self):
        """
        Load warehouse reference data so graph nodes can display
        real warehouse names and metadata.
        """

        self.warehouses = pd.read_csv(
            DATA_DIR / "warehouses.csv"
        )

        self.warehouse_lookup = {
            str(row["warehouse_id"]): row.to_dict()
            for _, row in self.warehouses.iterrows()
        }

    def build(
        self,
        impact_result: dict[str, Any],
        prioritized_orders: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:

        prioritized_orders = prioritized_orders or []

        nodes: dict[str, dict[str, Any]] = {}
        edges: list[dict[str, Any]] = []
        edge_keys = set()

        # ---------------------------------------------------------
        # Node helper
        # ---------------------------------------------------------

        def add_node(
            node_id: str,
            node_type: str,
            label: str,
            **metadata: Any,
        ):
            if not node_id:
                return

            if node_id not in nodes:

                node = {
                    "id": node_id,
                    "type": node_type,
                    "label": label,
                }

                node.update(metadata)

                nodes[node_id] = node

        # ---------------------------------------------------------
        # Edge helper
        # ---------------------------------------------------------

        def add_edge(
            source: str,
            target: str,
            relationship: str,
        ):
            if not source or not target:
                return

            key = (
                source,
                target,
                relationship,
            )

            if key in edge_keys:
                return

            edge_keys.add(key)

            edges.append(
                {
                    "source": source,
                    "target": target,
                    "relationship": relationship,
                }
            )

        # ---------------------------------------------------------
        # Warehouse helper
        # ---------------------------------------------------------

        def add_warehouse_node(
            warehouse_id: str,
        ):
            """
            Add a warehouse using authoritative warehouse data.

            If the warehouse is referenced by an operational record
            but cannot be found in warehouses.csv, only the identifier
            is shown. No warehouse metadata is invented.
            """

            if not warehouse_id:
                return

            warehouse_id = str(
                warehouse_id
            )

            warehouse = self.warehouse_lookup.get(
                warehouse_id
            )

            if warehouse:

                add_node(
                    warehouse_id,
                    "warehouse",
                    str(
                        warehouse.get(
                            "warehouse_name",
                            warehouse_id,
                        )
                    ),
                    location=warehouse.get(
                        "location"
                    ),
                    capacity=warehouse.get(
                        "capacity"
                    ),
                    status=warehouse.get(
                        "status"
                    ),
                )

            else:

                add_node(
                    warehouse_id,
                    "warehouse",
                    warehouse_id,
                )

        # ---------------------------------------------------------
        # Supplier
        # ---------------------------------------------------------

        supplier = impact_result.get(
            "supplier"
        )

        if supplier:

            supplier_id = str(
                supplier.get(
                    "supplier_id",
                    "",
                )
            )

            supplier_name = str(
                supplier.get(
                    "supplier_name",
                    supplier_id,
                )
            )

            add_node(
                supplier_id,
                "supplier",
                supplier_name,
                location=supplier.get(
                    "location"
                ),
                reliability_score=supplier.get(
                    "reliability_score"
                ),
                status=supplier.get(
                    "status"
                ),
            )

        # ---------------------------------------------------------
        # Products
        # ---------------------------------------------------------

        products = impact_result.get(
            "products",
            []
        )

        for product in products:

            product_id = str(
                product.get(
                    "product_id",
                    "",
                )
            )

            product_name = str(
                product.get(
                    "product_name",
                    product_id,
                )
            )

            add_node(
                product_id,
                "product",
                product_name,
                category=product.get(
                    "category"
                ),
                unit_cost=product.get(
                    "unit_cost"
                ),
            )

            if supplier:

                supplier_id = str(
                    supplier.get(
                        "supplier_id",
                        "",
                    )
                )

                add_edge(
                    supplier_id,
                    product_id,
                    "SUPPLIES",
                )

        # ---------------------------------------------------------
        # Affected shipments
        # ---------------------------------------------------------

        affected_shipments = impact_result.get(
            "affected_shipments",
            []
        )

        for shipment in affected_shipments:

            shipment_id = str(
                shipment.get(
                    "shipment_id",
                    "",
                )
            )

            supplier_id = str(
                shipment.get(
                    "supplier_id",
                    "",
                )
            )

            product_id = str(
                shipment.get(
                    "product_id",
                    "",
                )
            )

            warehouse_id = str(
                shipment.get(
                    "warehouse_id",
                    "",
                )
            )

            quantity = shipment.get(
                "quantity"
            )

            # -----------------------------------------------------
            # Warehouse
            # -----------------------------------------------------

            add_warehouse_node(
                warehouse_id
            )

            # -----------------------------------------------------
            # Shipment
            # -----------------------------------------------------

            add_node(
                shipment_id,
                "shipment",
                shipment_id,
                quantity=quantity,
                risk_status=shipment.get(
                    "risk_status"
                ),
                original_expected_date=shipment.get(
                    "original_expected_date"
                ),
                projected_expected_date=shipment.get(
                    "projected_expected_date"
                ),
            )

            # -----------------------------------------------------
            # Relationships
            # -----------------------------------------------------

            add_edge(
                supplier_id,
                product_id,
                "SUPPLIES",
            )

            add_edge(
                product_id,
                shipment_id,
                "SHIPPED_AS",
            )

            add_edge(
                shipment_id,
                warehouse_id,
                "DELIVERS_TO",
            )

        # ---------------------------------------------------------
        # Inventory
        # ---------------------------------------------------------

        inventory_summary = impact_result.get(
            "inventory_summary",
            []
        )

        for inventory in inventory_summary:

            warehouse_id = str(
                inventory.get(
                    "warehouse_id",
                    "",
                )
            )

            product_id = str(
                inventory.get(
                    "product_id",
                    "",
                )
            )

            inventory_id = (
                f"INV:{warehouse_id}:{product_id}"
            )

            # -----------------------------------------------------
            # Warehouse
            # -----------------------------------------------------

            add_warehouse_node(
                warehouse_id
            )

            # -----------------------------------------------------
            # Inventory
            # -----------------------------------------------------

            add_node(
                inventory_id,
                "inventory",
                f"{warehouse_id} / {product_id}",
                warehouse_id=warehouse_id,
                product_id=product_id,
                quantity=inventory.get(
                    "quantity"
                ),
                reserved_quantity=inventory.get(
                    "reserved_quantity"
                ),
                available_quantity=inventory.get(
                    "available_quantity"
                ),
            )

            add_edge(
                warehouse_id,
                inventory_id,
                "STORES",
            )

            add_edge(
                inventory_id,
                product_id,
                "STOCKS",
            )

        # ---------------------------------------------------------
        # Prioritized orders
        # ---------------------------------------------------------

        for order in prioritized_orders:

            order_id = str(
                order.get(
                    "order_id",
                    "",
                )
            )

            customer_id = str(
                order.get(
                    "customer_id",
                    "",
                )
            )

            product_id = str(
                order.get(
                    "product_id",
                    "",
                )
            )

            warehouse_id = str(
                order.get(
                    "warehouse_id",
                    "",
                )
            )

            # -----------------------------------------------------
            # Warehouse
            # -----------------------------------------------------

            add_warehouse_node(
                warehouse_id
            )

            # -----------------------------------------------------
            # Order
            # -----------------------------------------------------

            add_node(
                order_id,
                "order",
                order_id,
                priority=order.get(
                    "priority"
                ),
                priority_score=order.get(
                    "priority_score"
                ),
                quantity=order.get(
                    "quantity"
                ),
                fulfillable_quantity=order.get(
                    "fulfillable_quantity"
                ),
                shortage_quantity=order.get(
                    "shortage_quantity"
                ),
                required_date=order.get(
                    "required_date"
                ),
            )

            add_edge(
                product_id,
                order_id,
                "FULFILLS",
            )

            add_edge(
                warehouse_id,
                order_id,
                "SERVES",
            )

            # -----------------------------------------------------
            # Customer
            # -----------------------------------------------------

            customer_name = order.get(
                "customer_name",
                customer_id,
            )

            add_node(
                customer_id,
                "customer",
                customer_name,
                customer_type=order.get(
                    "customer_type"
                ),
                service_level=order.get(
                    "service_level"
                ),
            )

            add_edge(
                order_id,
                customer_id,
                "PLACED_BY",
            )

        # ---------------------------------------------------------
        # Graph metadata
        # ---------------------------------------------------------

        return {
            "nodes": list(
                nodes.values()
            ),
            "edges": edges,
            "node_count": len(
                nodes
            ),
            "edge_count": len(
                edges
            ),
        }

