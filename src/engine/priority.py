
from datetime import datetime
from typing import Any


class OrderPriorityEngine:
    """
    Deterministic and explainable order-priority scoring engine.

    Gemini is intentionally not used here.
    All scores are calculated from operational data.

    Priority formula:
        Delivery urgency      = 35%
        Customer service      = 30%
        Shortage severity     = 25%
        Customer type         = 10%

    Priority levels:
        90-100 -> CRITICAL
        75-89  -> HIGH
        50-74  -> MEDIUM
        0-49   -> LOW
    """

    SERVICE_LEVEL_SCORES = {
        "critical": 100,
        "high": 80,
        "medium": 60,
        "low": 40,
    }

    CUSTOMER_TYPE_SCORES = {
        "strategic": 100,
        "enterprise": 80,
        "standard": 60,
    }

    def __init__(self):
        pass

    # ------------------------------------------------------------------
    # DELIVERY URGENCY
    # ------------------------------------------------------------------

    @staticmethod
    def _urgency_score(days_until_required: int) -> float:
        """
        Convert days until required delivery into a 0-100 urgency score.
        """

        if days_until_required <= 0:
            return 100.0

        if days_until_required <= 2:
            return 95.0

        if days_until_required <= 4:
            return 85.0

        if days_until_required <= 7:
            return 70.0

        if days_until_required <= 14:
            return 50.0

        return 30.0

    # ------------------------------------------------------------------
    # SHORTAGE SEVERITY
    # ------------------------------------------------------------------

    @staticmethod
    def _shortage_score(
        order_quantity: float,
        shortage_quantity: float,
    ) -> float:
        """
        Convert shortage percentage into a 0-100 severity score.
        """

        if order_quantity <= 0:
            return 0.0

        # Defensive handling in case bad data produces a negative shortage.
        shortage_quantity = max(shortage_quantity, 0.0)

        shortage_ratio = shortage_quantity / order_quantity

        if shortage_ratio >= 1:
            return 100.0

        if shortage_ratio >= 0.75:
            return 90.0

        if shortage_ratio >= 0.50:
            return 80.0

        if shortage_ratio >= 0.25:
            return 65.0

        if shortage_ratio > 0:
            return 50.0

        return 0.0

    # ------------------------------------------------------------------
    # PRIORITY CALCULATION
    # ------------------------------------------------------------------

    def _calculate_priority(
        self,
        order: dict[str, Any],
        analysis_date: str | datetime,
    ) -> dict[str, Any]:
        """
        Calculate the priority score for one affected order.

        Important:
        Operational fields are preserved in the returned object so that
        downstream engines, such as the Phase 7 recommendation engine,
        can continue using the original order information.
        """

        # --------------------------------------------------------------
        # Validate required fields
        # --------------------------------------------------------------

        if "order_id" not in order:
            raise ValueError("Order is missing required field: order_id")

        if "customer_id" not in order:
            raise ValueError("Order is missing required field: customer_id")

        if "product_id" not in order:
            raise ValueError("Order is missing required field: product_id")

        if "quantity" not in order:
            raise ValueError("Order is missing required field: quantity")

        if "required_date" not in order:
            raise ValueError("Order is missing required field: required_date")

        # --------------------------------------------------------------
        # Analysis date
        # --------------------------------------------------------------

        if isinstance(analysis_date, str):
            analysis_date = datetime.strptime(
                analysis_date,
                "%Y-%m-%d",
            )

        # --------------------------------------------------------------
        # Required delivery date
        # --------------------------------------------------------------

        required_date = datetime.strptime(
            str(order["required_date"]),
            "%Y-%m-%d",
        )

        days_until_required = (
            required_date.date() - analysis_date.date()
        ).days

        # --------------------------------------------------------------
        # Delivery urgency
        # --------------------------------------------------------------

        urgency = self._urgency_score(
            days_until_required
        )

        # --------------------------------------------------------------
        # Customer service level
        # --------------------------------------------------------------

        service_level = str(
            order.get("service_level", "medium")
        ).strip().lower()

        service_score = self.SERVICE_LEVEL_SCORES.get(
            service_level,
            60,
        )

        # --------------------------------------------------------------
        # Customer type
        # --------------------------------------------------------------

        customer_type = str(
            order.get("customer_type", "standard")
        ).strip().lower()

        customer_type_score = self.CUSTOMER_TYPE_SCORES.get(
            customer_type,
            60,
        )

        # --------------------------------------------------------------
        # Order quantity
        # --------------------------------------------------------------

        order_quantity = float(
            order["quantity"]
        )

        # --------------------------------------------------------------
        # Shortage quantity
        #
        # Phase 5 ImpactEngine uses:
        #     shortage_quantity
        #
        # Keep that field as the source of truth.
        # --------------------------------------------------------------

        shortage_quantity = float(
            order.get("shortage_quantity", 0)
        )

        # Prevent invalid negative shortage values.
        shortage_quantity = max(
            shortage_quantity,
            0.0,
        )

        # Do not allow shortage to exceed the order quantity.
        shortage_quantity = min(
            shortage_quantity,
            max(order_quantity, 0.0),
        )

        # --------------------------------------------------------------
        # Shortage severity
        # --------------------------------------------------------------

        shortage_score = self._shortage_score(
            order_quantity,
            shortage_quantity,
        )

        # --------------------------------------------------------------
        # Weighted priority score
        # --------------------------------------------------------------

        weighted_score = (
            urgency * 0.35
            + service_score * 0.30
            + shortage_score * 0.25
            + customer_type_score * 0.10
        )

        score = round(
            weighted_score,
            2,
        )

        # --------------------------------------------------------------
        # Priority classification
        # --------------------------------------------------------------

        if score >= 90:
            priority = "CRITICAL"

        elif score >= 75:
            priority = "HIGH"

        elif score >= 50:
            priority = "MEDIUM"

        else:
            priority = "LOW"

        # --------------------------------------------------------------
        # Explainable reasons
        # --------------------------------------------------------------

        reasons = []

        if days_until_required <= 2:
            reasons.append(
                "Required delivery date is extremely close."
            )

        elif days_until_required <= 7:
            reasons.append(
                "Required delivery date is approaching."
            )

        else:
            reasons.append(
                "Required delivery date has more time remaining."
            )

        if service_level == "critical":
            reasons.append(
                "Customer has CRITICAL service level."
            )

        elif service_level == "high":
            reasons.append(
                "Customer has HIGH service level."
            )

        elif service_level == "medium":
            reasons.append(
                "Customer has MEDIUM service level."
            )

        if shortage_quantity >= order_quantity and order_quantity > 0:
            reasons.append(
                "The full order quantity is currently unavailable."
            )

        elif shortage_quantity > 0:
            reasons.append(
                f"{shortage_quantity:g} units are currently unavailable."
            )

        if customer_type == "strategic":
            reasons.append(
                "Customer is classified as STRATEGIC."
            )

        elif customer_type == "enterprise":
            reasons.append(
                "Customer is classified as ENTERPRISE."
            )

        elif customer_type == "standard":
            reasons.append(
                "Customer is classified as STANDARD."
            )

        # --------------------------------------------------------------
        # Preserve operational fields
        #
        # These fields are important for Phase 7.
        # --------------------------------------------------------------

        fulfillable_quantity = float(
            order.get("fulfillable_quantity", 0)
        )

        fulfillable_quantity = max(
            fulfillable_quantity,
            0.0,
        )

        # --------------------------------------------------------------
        # Final enriched priority object
        # --------------------------------------------------------------

        return {
            # ----------------------------------------------------------
            # Identity
            # ----------------------------------------------------------
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "customer_name": order.get("customer_name"),

            # ----------------------------------------------------------
            # Customer information
            # ----------------------------------------------------------
            "customer_type": customer_type,
            "service_level": service_level,

            # ----------------------------------------------------------
            # Operational information
            # ----------------------------------------------------------
            "product_id": order["product_id"],
            "warehouse_id": order.get("warehouse_id"),
            "quantity": order_quantity,
            "fulfillable_quantity": fulfillable_quantity,
            "shortage_quantity": shortage_quantity,

            # ----------------------------------------------------------
            # Delivery information
            # ----------------------------------------------------------
            "required_date": str(
                order["required_date"]
            ),
            "order_date": str(
                order.get("order_date", "")
            ),
            "days_until_required": days_until_required,

            # ----------------------------------------------------------
            # Priority result
            # ----------------------------------------------------------
            "priority_score": score,
            "priority": priority,

            # ----------------------------------------------------------
            # Explainable scoring
            # ----------------------------------------------------------
            "score_breakdown": {
                "delivery_urgency": round(
                    urgency * 0.35,
                    2,
                ),
                "service_level": round(
                    service_score * 0.30,
                    2,
                ),
                "shortage_severity": round(
                    shortage_score * 0.25,
                    2,
                ),
                "customer_type": round(
                    customer_type_score * 0.10,
                    2,
                ),
            },

            # ----------------------------------------------------------
            # Human-readable reasons
            # ----------------------------------------------------------
            "reasons": reasons,
        }

    # ------------------------------------------------------------------
    # PRIORITIZE MULTIPLE ORDERS
    # ------------------------------------------------------------------

    def prioritize(
        self,
        affected_orders: list[dict[str, Any]],
        analysis_date: str | datetime,
    ) -> list[dict[str, Any]]:
        """
        Prioritize affected orders.

        Orders are sorted by:
        1. Priority score descending
        2. Required date ascending
        3. Order ID ascending
        """

        if not affected_orders:
            return []

        results = []

        for order in affected_orders:
            result = self._calculate_priority(
                order,
                analysis_date,
            )

            results.append(result)

        # --------------------------------------------------------------
        # Deterministic sorting
        # --------------------------------------------------------------

        results.sort(
            key=lambda item: (
                -item["priority_score"],
                item["required_date"],
                item["order_id"],
            )
        )

        return results
