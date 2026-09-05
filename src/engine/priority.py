from datetime import datetime
from typing import Any

import pandas as pd


class OrderPriorityEngine:
    """
    Deterministic and explainable order-priority scoring engine.

    Gemini is intentionally not used here.
    All scores are calculated from operational data.
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

    @staticmethod
    def _shortage_score(order_quantity: float, shortage_quantity: float) -> float:
        """
        Convert shortage percentage into a 0-100 severity score.
        """

        if order_quantity <= 0:
            return 0.0

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

    def _calculate_priority(
        self,
        order: dict[str, Any],
        analysis_date: str | datetime,
    ) -> dict[str, Any]:

        if isinstance(analysis_date, str):
            analysis_date = datetime.strptime(
                analysis_date,
                "%Y-%m-%d"
            )

        required_date = datetime.strptime(
            str(order["required_date"]),
            "%Y-%m-%d"
        )

        days_until_required = (
            required_date.date() - analysis_date.date()
        ).days

        urgency = self._urgency_score(days_until_required)

        service_level = str(
            order.get("service_level", "medium")
        ).lower()

        service_score = self.SERVICE_LEVEL_SCORES.get(
            service_level,
            60
        )

        customer_type = str(
            order.get("customer_type", "standard")
        ).lower()

        customer_type_score = self.CUSTOMER_TYPE_SCORES.get(
            customer_type,
            60
        )

        order_quantity = float(order["quantity"])

        shortage_quantity = float(
            order.get("shortage_quantity", 0)
        )

        shortage_score = self._shortage_score(
            order_quantity,
            shortage_quantity
        )

        weighted_score = (
            urgency * 0.35
            + service_score * 0.30
            + shortage_score * 0.25
            + customer_type_score * 0.10
        )

        score = round(weighted_score, 2)

        if score >= 90:
            priority = "CRITICAL"
        elif score >= 75:
            priority = "HIGH"
        elif score >= 50:
            priority = "MEDIUM"
        else:
            priority = "LOW"

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

        if shortage_quantity >= order_quantity:
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

        return {
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "customer_name": order.get("customer_name"),
            "product_id": order["product_id"],
            "quantity": order_quantity,
            "shortage": shortage_quantity,
            "required_date": str(order["required_date"]),
            "days_until_required": days_until_required,
            "service_level": service_level,
            "customer_type": customer_type,
            "priority_score": score,
            "priority": priority,
            "score_breakdown": {
                "delivery_urgency": round(urgency * 0.35, 2),
                "service_level": round(service_score * 0.30, 2),
                "shortage_severity": round(shortage_score * 0.25, 2),
                "customer_type": round(
                    customer_type_score * 0.10,
                    2
                ),
            },
            "reasons": reasons,
        }

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

        results = []

        for order in affected_orders:
            results.append(
                self._calculate_priority(
                    order,
                    analysis_date
                )
            )

        results.sort(
            key=lambda item: (
                -item["priority_score"],
                item["required_date"],
                item["order_id"],
            )
        )

        return results