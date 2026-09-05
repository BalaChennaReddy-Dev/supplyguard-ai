from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
)


class EntityMatcher:
    """
    Deterministically maps entities extracted by Gemini
    to trusted operational data.

    Gemini provides names.
    This class resolves those names to internal IDs.
    """

    def __init__(self):
        self.suppliers = pd.read_csv(
            DATA_DIR / "suppliers.csv"
        )

        self.products = pd.read_csv(
            DATA_DIR / "products.csv"
        )

        self.warehouses = pd.read_csv(
            DATA_DIR / "warehouses.csv"
        )

        self.shipments = pd.read_csv(
            DATA_DIR / "shipments.csv"
        )

    @staticmethod
    def _normalize(value: Any) -> str:
        """
        Normalize text for deterministic matching.
        """
        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace("-", " ")
            .replace("_", " ")
        )

    def match_supplier(
        self,
        supplier_name: str | None
    ) -> dict[str, Any] | None:

        if not supplier_name:
            return None

        target = self._normalize(supplier_name)

        for _, supplier in self.suppliers.iterrows():
            candidate = self._normalize(
                supplier["supplier_name"]
            )

            if target == candidate:
                return supplier.to_dict()

        return None

    def match_product(
        self,
        product_name: str
    ) -> dict[str, Any] | None:

        if not product_name:
            return None

        target = self._normalize(product_name)

        # Exact normalized match first.
        for _, product in self.products.iterrows():
            candidate = self._normalize(
                product["product_name"]
            )

            if target == candidate:
                return product.to_dict()

        # Handle simple plural forms such as:
        # "Motor Controllers" -> "Motor Controller"
        # "Power Supply Modules" -> "Power Supply Module"
        if target.endswith("s"):
            singular_target = target[:-1]

            for _, product in self.products.iterrows():
                candidate = self._normalize(
                    product["product_name"]
                )

                if singular_target == candidate:
                    return product.to_dict()

        return None

    def match_products(
        self,
        product_names: list[str]
    ) -> list[dict[str, Any]]:

        matches = []

        for product_name in product_names:
            match = self.match_product(product_name)

            if match:
                matches.append(match)

        return matches

    def match_warehouse(
        self,
        warehouse_name: str | None
    ) -> dict[str, Any] | None:

        if not warehouse_name:
            return None

        target = self._normalize(warehouse_name)

        for _, warehouse in self.warehouses.iterrows():
            candidate = self._normalize(
                warehouse["warehouse_name"]
            )

            if target == candidate:
                return warehouse.to_dict()

        return None

    def match_shipment(
        self,
        shipment_id: str | None
    ) -> dict[str, Any] | None:

        if not shipment_id:
            return None

        target = self._normalize(shipment_id)

        for _, shipment in self.shipments.iterrows():
            candidate = self._normalize(
                shipment["shipment_id"]
            )

            if target == candidate:
                return shipment.to_dict()

        return None

    def resolve(
        self,
        extraction: dict[str, Any]
    ) -> dict[str, Any]:

        supplier = self.match_supplier(
            extraction.get("supplier_name")
        )

        products = self.match_products(
            extraction.get("affected_products", [])
        )

        warehouse = self.match_warehouse(
            extraction.get("warehouse_name")
        )

        shipment = self.match_shipment(
            extraction.get("shipment_id")
        )

        return {
            "supplier": supplier,
            "products": products,
            "warehouse": warehouse,
            "shipment": shipment,
        }