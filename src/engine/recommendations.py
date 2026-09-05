from engine.evidence import EvidenceEngine
from pathlib import Path
from typing import Any

import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"


class ResponseRecommendationEngine:
    """
    Deterministic response recommendation engine.

    Gemini is intentionally not used here.

    Responsibilities:
        - Evaluate operational response options.
        - Calculate fulfillment coverage.
        - Compare feasible options.
        - Attach evidence to recommendations.
        - Apply response-playbook rules.
        - Require human approval.

    The engine NEVER:
        - Moves inventory.
        - Expedites shipments.
        - Changes orders.
        - Sends customer messages.
    """

    # --------------------------------------------------------------
    # Recommendation ranking
    # --------------------------------------------------------------

    ACTION_RANK = {
        "REALLOCATE": 1,
        "EXPEDITE": 2,
        "PART_SHIP": 3,
        "NOTIFY_CUSTOMER": 4,
    }

    def __init__(self):
        self.inventory = pd.read_csv(
            DATA_DIR / "inventory.csv"
        )

        self.shipments = pd.read_csv(
            DATA_DIR / "shipments.csv"
        )

        self.orders = pd.read_csv(
            DATA_DIR / "orders.csv"
        )
        self.evidence_engine = EvidenceEngine()

    # ==============================================================
    # EVIDENCE
    # ==============================================================

    @staticmethod
    def _evidence(
        source: str,
        record_id: str,
        detail: str,
    ) -> dict[str, str]:
        """
        Create a traceable evidence record.
        """

        return {
            "source": source,
            "record_id": record_id,
            "detail": detail,
        }

    # ==============================================================
    # REALLOCATION
    # ==============================================================

    def evaluate_reallocation(
        self,
        order: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Determine whether stock from another warehouse can cover
        some or all of the order shortage.
        """

        product_id = order["product_id"]
        order_warehouse = order.get("warehouse_id")
        shortage = float(
            order.get("shortage_quantity", 0)
        )

        if shortage <= 0:
            return {
                "action": "REALLOCATE",
                "feasible": False,
                "coverage_quantity": 0,
                "coverage_percentage": 0.0,
                "fully_resolves_shortage": False,
                "policy_rule": "R01",
                "reason": (
                    "The order has no shortage requiring "
                    "reallocation."
                ),
                "trade_off": None,
                "evidence": [],
            }

        if not order_warehouse:
            return {
                "action": "REALLOCATE",
                "feasible": False,
                "coverage_quantity": 0,
                "coverage_percentage": 0.0,
                "fully_resolves_shortage": False,
                "policy_rule": "R02",
                "reason": (
                    "The affected warehouse is unknown, so "
                    "a safe source warehouse cannot be identified."
                ),
                "trade_off": None,
                "evidence": [],
            }

        candidates = self.inventory[
            (self.inventory["product_id"] == product_id)
            & (
                self.inventory["warehouse_id"]
                != order_warehouse
            )
        ].copy()

        if candidates.empty:
            return {
                "action": "REALLOCATE",
                "feasible": False,
                "coverage_quantity": 0,
                "coverage_percentage": 0.0,
                "fully_resolves_shortage": False,
                "policy_rule": "R01",
                "reason": (
                    "No inventory record for this product exists "
                    "at another warehouse."
                ),
                "trade_off": (
                    "Reallocation cannot currently be evaluated."
                ),
                "evidence": [],
            }

        candidates["available_quantity"] = (
            candidates["quantity"]
            - candidates["reserved_quantity"]
        )

        candidates = candidates[
            candidates["available_quantity"] > 0
        ]

        if candidates.empty:
            return {
                "action": "REALLOCATE",
                "feasible": False,
                "coverage_quantity": 0,
                "coverage_percentage": 0.0,
                "fully_resolves_shortage": False,
                "policy_rule": "R01",
                "reason": (
                    "No unreserved inventory is currently "
                    "available at another warehouse."
                ),
                "trade_off": (
                    "Reallocation cannot currently cover "
                    "the shortage."
                ),
                "evidence": [],
            }

        # Prefer the source warehouse with the largest available stock.
        candidates = candidates.sort_values(
            by=[
                "available_quantity",
                "warehouse_id",
            ],
            ascending=[
                False,
                True,
            ],
        )

        candidate = candidates.iloc[0]

        available = float(
            candidate["available_quantity"]
        )

        transfer_quantity = min(
            shortage,
            available,
        )

        coverage_percentage = round(
            (transfer_quantity / shortage) * 100,
            2,
        )

        fully_resolves = (
            transfer_quantity >= shortage
        )

        evidence = [
            self._evidence(
                "inventory.csv",
                f"{candidate['warehouse_id']}/{product_id}",
                (
                    f"{available:g} units available at "
                    f"{candidate['warehouse_id']} after "
                    f"reserved stock."
                ),
            ),
            self._evidence(
                "orders.csv",
                order["order_id"],
                (
                    f"Order requires {shortage:g} additional "
                    f"units."
                ),
            ),
        ]

        if fully_resolves:
            reason = (
                f"{transfer_quantity:g} units can be "
                f"reallocated from "
                f"{candidate['warehouse_id']} to fully "
                f"cover the shortage."
            )

            trade_off = (
                f"Reallocation reduces available stock at "
                f"{candidate['warehouse_id']} by "
                f"{transfer_quantity:g} units."
            )

        else:
            remaining = shortage - transfer_quantity

            reason = (
                f"{transfer_quantity:g} units can be "
                f"reallocated from "
                f"{candidate['warehouse_id']}, covering "
                f"{coverage_percentage}% of the shortage."
            )

            trade_off = (
                f"Reallocation leaves {remaining:g} units "
                f"of shortage unresolved and reduces available "
                f"stock at {candidate['warehouse_id']}."
            )

        return {
            "action": "REALLOCATE",
            "feasible": True,
            "coverage_quantity": transfer_quantity,
            "coverage_percentage": coverage_percentage,
            "fully_resolves_shortage": fully_resolves,
            "source_warehouse": candidate["warehouse_id"],
            "policy_rule": (
                "R01"
                if fully_resolves
                else "R02"
            ),
            "reason": reason,
            "trade_off": trade_off,
            "evidence": evidence,
        }

    # ==============================================================
    # EXPEDITE
    # ==============================================================

    def evaluate_expedite(
        self,
        order: dict[str, Any],
        impact_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate inbound shipments that may help recover the order.

        Expedite is only considered beneficial when the current
        expected arrival is after the customer's required date.

        The engine does not invent an expedite cost.
        """

        product_id = order["product_id"]
        warehouse_id = order.get("warehouse_id")

        required_date = str(
            order["required_date"]
        )

        if not warehouse_id:
            return {
                "action": "EXPEDITE",
                "feasible": False,
                "policy_rule": "R03",
                "reason": (
                    "Affected warehouse is unknown, so an "
                    "inbound shipment cannot be safely matched."
                ),
                "trade_off": None,
                "evidence": [],
            }

        shipments = self.shipments[
            (self.shipments["product_id"] == product_id)
            & (
                self.shipments["warehouse_id"]
                == warehouse_id
            )
            & (
                self.shipments["status"]
                == "in_transit"
            )
        ].copy()

        if shipments.empty:
            return {
                "action": "EXPEDITE",
                "feasible": False,
                "policy_rule": "R03",
                "reason": (
                    "No in-transit shipment for this product "
                    "and warehouse was found."
                ),
                "trade_off": None,
                "evidence": [],
            }

        shipments["expected_date_dt"] = pd.to_datetime(
            shipments["expected_date"]
        )

        shipments = shipments.sort_values(
            by=[
                "expected_date_dt",
                "shipment_id",
            ]
        )

        shipment = shipments.iloc[0]

        quantity = float(
            shipment["quantity"]
        )

        expected_date = str(
            shipment["expected_date"]
        )

        evidence = [
            self._evidence(
                "shipments.csv",
                shipment["shipment_id"],
                (
                    f"{quantity:g} units of {product_id} "
                    f"are in transit to {warehouse_id}, "
                    f"currently expected on {expected_date}."
                ),
            ),
            self._evidence(
                "orders.csv",
                order["order_id"],
                (
                    f"Customer requires delivery by "
                    f"{required_date}."
                ),
            ),
        ]

        expected_before_required = (
            expected_date <= required_date
        )

        # ----------------------------------------------------------
        # Important business rule:
        # If the shipment already arrives on/before the required
        # date, expediting provides no identified delivery benefit.
        # ----------------------------------------------------------

        if expected_before_required:
            return {
                "action": "EXPEDITE",
                "feasible": False,
                "policy_rule": "R03",
                "shipment_id": shipment["shipment_id"],
                "shipment_quantity": quantity,
                "expected_date": expected_date,
                "required_date": required_date,
                "expected_before_required": True,
                "reason": (
                    f"Shipment {shipment['shipment_id']} is "
                    f"already expected on {expected_date}, "
                    f"before or on the customer's required date "
                    f"of {required_date}. Expediting is therefore "
                    f"not currently necessary."
                ),
                "trade_off": (
                    "Expediting would introduce potential "
                    "transportation cost without an identified "
                    "delivery-date benefit."
                ),
                "evidence": evidence,
            }

        # Shipment arrives after customer's required date.
        return {
            "action": "EXPEDITE",
            "feasible": True,
            "shipment_id": shipment["shipment_id"],
            "shipment_quantity": quantity,
            "expected_date": expected_date,
            "required_date": required_date,
            "expected_before_required": False,
            "policy_rule": "R03",
            "reason": (
                f"Shipment {shipment['shipment_id']} is "
                f"currently expected on {expected_date}, "
                f"after the customer's required date of "
                f"{required_date}. Expediting should therefore "
                f"be considered."
            ),
            "trade_off": (
                "Expediting may increase transportation cost. "
                "No exact cost is estimated because no documented "
                "cost rule is currently available."
            ),
            "evidence": evidence,
        }


    def evaluate_part_ship(
        self,
        order: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Determine whether part of an order can be fulfilled now.
        """

        quantity = float(
            order["quantity"]
        )

        fulfillable = float(
            order.get("fulfillable_quantity", 0)
        )

        shortage = float(
            order.get("shortage_quantity", 0)
        )

        fulfillable = max(
            fulfillable,
            0.0,
        )

        if quantity <= 0:
            return {
                "action": "PART_SHIP",
                "feasible": False,
                "coverage_quantity": 0,
                "coverage_percentage": 0.0,
                "policy_rule": "R04",
                "reason": (
                    "The order quantity is invalid or zero."
                ),
                "trade_off": None,
                "evidence": [],
            }

        if fulfillable <= 0:
            return {
                "action": "PART_SHIP",
                "feasible": False,
                "coverage_quantity": 0,
                "coverage_percentage": 0.0,
                "policy_rule": "R04",
                "reason": (
                    "No quantity is currently available "
                    "to fulfill the order."
                ),
                "trade_off": None,
                "evidence": [],
            }

        if shortage <= 0:
            return {
                "action": "PART_SHIP",
                "feasible": False,
                "coverage_quantity": quantity,
                "coverage_percentage": 100.0,
                "policy_rule": "R04",
                "reason": (
                    "The order can already be fulfilled "
                    "in full."
                ),
                "trade_off": None,
                "evidence": [],
            }

        coverage = round(
            (fulfillable / quantity) * 100,
            2,
        )

        evidence = [
            self._evidence(
                "orders.csv",
                order["order_id"],
                (
                    f"Order quantity is {quantity:g}; "
                    f"{fulfillable:g} units are currently "
                    f"fulfillable."
                ),
            ),
        ]

        remaining = quantity - fulfillable

        return {
            "action": "PART_SHIP",
            "feasible": True,
            "coverage_quantity": fulfillable,
            "coverage_percentage": coverage,
            "remaining_quantity": remaining,
            "policy_rule": "R04",
            "reason": (
                f"{fulfillable:g} of {quantity:g} units "
                f"can be shipped immediately, covering "
                f"{coverage}% of the order."
            ),
            "trade_off": (
                f"The customer receives {fulfillable:g} units "
                f"now, but the remaining {remaining:g} units "
                f"require later fulfillment."
            ),
            "evidence": evidence,
        }

    # ==============================================================
    # CUSTOMER NOTIFICATION
    # ==============================================================

    def evaluate_notification(
        self,
        order: dict[str, Any],
        impact_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Determine whether customer notification should be considered.

        No customer message is sent automatically.
        """

        shortage = float(
            order.get("shortage_quantity", 0)
        )

        if shortage <= 0:
            return {
                "action": "NOTIFY_CUSTOMER",
                "feasible": False,
                "policy_rule": "R05",
                "reason": (
                    "No delivery shortage has been identified."
                ),
                "trade_off": None,
                "evidence": [],
            }

        evidence = [
            self._evidence(
                "orders.csv",
                order["order_id"],
                (
                    f"Order has a shortage of {shortage:g} "
                    f"units against a required date of "
                    f"{order['required_date']}."
                ),
            ),
        ]

        return {
            "action": "NOTIFY_CUSTOMER",
            "feasible": True,
            "policy_rule": "R05",
            "reason": (
                "Customer communication should be considered "
                "because the order cannot currently be fulfilled "
                "in full."
            ),
            "trade_off": (
                "Early notification improves transparency but "
                "may require communicating an uncertain revised "
                "delivery date."
            ),
            "evidence": evidence,
        }

    # ==============================================================
    # EVALUATE ALL OPTIONS
    # ==============================================================

    def evaluate_order(
        self,
        order: dict[str, Any],
        impact_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Evaluate all four response options.
        """

        options = [
            self.evaluate_reallocation(
                order
            ),
            self.evaluate_expedite(
                order,
                impact_result,
            ),
            self.evaluate_part_ship(
                order
            ),
            self.evaluate_notification(
                order,
                impact_result,
            ),
        ]

        feasible_options = [
            option
            for option in options
            if option.get("feasible")
        ]

        return {
            "order_id": order["order_id"],
            "customer_id": order["customer_id"],
            "customer_name": order.get("customer_name"),
            "product_id": order["product_id"],
            "warehouse_id": order.get("warehouse_id"),
            "quantity": float(order["quantity"]),
            "fulfillable_quantity": float(
                order.get(
                    "fulfillable_quantity",
                    0,
                )
            ),
            "shortage_quantity": float(
                order.get(
                    "shortage_quantity",
                    0,
                )
            ),
            "priority": order.get("priority"),
            "priority_score": order.get(
                "priority_score"
            ),
            "options": options,
            "feasible_option_count": len(
                feasible_options
            ),
        }

    # ==============================================================
    # OPTION SCORING
    # ==============================================================

    @staticmethod
    def _option_score(
        option: dict[str, Any],
    ) -> float:
        """
        Calculate a deterministic decision-support score.

        This is NOT an ML prediction.

        Factors:
            Full resolution       = 50 points
            Coverage              = up to 30 points
            Operational certainty = 20 points

        Notification is intentionally treated as a fallback
        communication action rather than an operational recovery.
        """

        if not option.get("feasible"):
            return -1.0

        action = option["action"]

        if action == "NOTIFY_CUSTOMER":
            return 10.0

        coverage = float(
            option.get(
                "coverage_percentage",
                0,
            )
        )

        score = coverage * 0.30

        if option.get(
            "fully_resolves_shortage",
            False,
        ):
            score += 50.0

        elif coverage >= 100:
            score += 50.0

        elif action == "EXPEDITE":
            # An inbound shipment may resolve the shortage,
            # but exact recovery cannot be guaranteed here.
            score += 20.0

        elif action == "PART_SHIP":
            score += 10.0

        elif action == "REALLOCATE":
            score += 15.0

        # Operational certainty bonus.
        if action == "REALLOCATE":
            score += 20.0

        elif action == "PART_SHIP":
            score += 20.0

        elif action == "EXPEDITE":
            score += 10.0

        return round(
            score,
            2,
        )

    # ==============================================================
    # SELECT RECOMMENDATION
    # ==============================================================

    def _recommend_option(
        self,
        options: list[dict[str, Any]],
    ) -> dict[str, Any] | None:
        """
        Select the strongest deterministic response.

        Policy preference:
            1. Full shortage resolution.
            2. Highest fulfillment coverage.
            3. More operationally certain options.
            4. Lower action rank as tie-breaker.
        """

        feasible = [
            option
            for option in options
            if option.get("feasible")
        ]

        if not feasible:
            return None

        scored = []

        for option in feasible:
            score = self._option_score(
                option
            )

            scored.append(
                (
                    option,
                    score,
                )
            )

        scored.sort(
            key=lambda item: (
                -item[1],
                -float(
                    item[0].get(
                        "coverage_percentage",
                        0,
                    )
                ),
                self.ACTION_RANK.get(
                    item[0]["action"],
                    99,
                ),
            )
        )

        best_option, best_score = scored[0]

        recommended = dict(
            best_option
        )

        recommended["decision_score"] = best_score

        return recommended

    # ==============================================================
    # RECOMMEND FOR ONE ORDER
    # ==============================================================

    def recommend_for_order(
        self,
        order: dict[str, Any],
        impact_result: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Produce a complete recommendation for one affected order.
        """

        evaluation = self.evaluate_order(
            order,
            impact_result,
        )

        recommendation = self._recommend_option(
            evaluation["options"]
        )

        if recommendation is None:
            recommendation_reason = (
                "No feasible operational response was identified. "
                "Human review is required."
            )

        else:
            recommendation_reason = (
                f"{recommendation['action']} selected because "
                f"it provides the strongest deterministic response "
                f"under the response playbook."
            )
        evidence = self.evidence_engine.order_evidence(
            order
        )
        return {
            **evaluation,
            "evidence": evidence,

            "recommended_action": (
                recommendation["action"]
                if recommendation
                else None
            ),

            "recommendation": recommendation,

            "recommendation_reason": (
                recommendation_reason
            ),

            # R06 — Human approval.
            "requires_human_approval": True,

            # R07 — Evidence required.
            "evidence_required": True,
        }

    # ==============================================================
    # RECOMMEND FOR MULTIPLE ORDERS
    # ==============================================================

    def recommend(
        self,
        prioritized_orders: list[dict[str, Any]],
        impact_result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Generate recommendations for prioritized affected orders.
        """

        if not prioritized_orders:
            return []

        recommendations = []

        for order in prioritized_orders:
            recommendations.append(
                self.recommend_for_order(
                    order,
                    impact_result,
                )
            )

        return recommendations
