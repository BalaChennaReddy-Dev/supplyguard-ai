# SupplyGuard AI — Response Playbook

## Purpose

This playbook defines the operational rules used by SupplyGuard AI when evaluating responses to supply-chain disruptions.

The system recommends actions but does not execute them automatically.

Final decisions require human approval.

---

## R01 — Full Reallocation Preferred

If another warehouse has enough available inventory to completely cover an affected order's shortage, reallocation should be considered the preferred response.

Reason:

* Resolves the shortage using existing inventory.
* Avoids waiting for disrupted replenishment.
* Provides a deterministic fulfillment path.

Trade-off:

* Reduces available inventory at the source warehouse.
* May create risk for orders depending on that inventory.

---

## R02 — Partial Reallocation

If another warehouse has available inventory but not enough to cover the entire shortage, partial reallocation may be considered.

The system must explicitly show:

* Available quantity.
* Quantity transferred.
* Remaining shortage.
* Source warehouse.

Partial reallocation must not be represented as full resolution.

---

## R03 — Expedite Inbound Shipment

Expediting may be considered when an affected product has an in-transit shipment.

The system should compare:

* Customer required date.
* Current expected shipment date.
* Projected date after disruption.
* Quantity available in the shipment.

Expediting introduces additional transportation cost.

The system must not invent an exact expedite cost unless a documented cost rule exists.

---

## R04 — Part-Ship

Part-shipping may be considered when some quantity is currently fulfillable.

The system must show:

* Total order quantity.
* Quantity available now.
* Quantity remaining.
* Percentage of order covered.

Part-shipping does not resolve the remaining shortage.

---

## R05 — Customer Notification

Customer notification should be considered when an order cannot currently be fulfilled in full.

Notification is a communication recommendation only.

The system must not automatically send a message.

---

## R06 — Human Approval

Every operational recommendation requires human approval.

SupplyGuard AI must never:

* Move inventory automatically.
* Expedite a shipment automatically.
* Change an order automatically.
* Send customer communications automatically.

The system provides decision support only.

---

## R07 — Evidence Required

Every recommendation must contain traceable evidence.

Evidence should identify:

* Source dataset.
* Record identifier.
* Relevant operational fact.

Examples:

* `inventory.csv → WH002/PROD001`
* `shipments.csv → SHIP001`
* `orders.csv → ORD013`

---

## R08 — No Impact

If a disruption notice cannot be mapped to relevant operational data, the system must not invent an impact.

The result should be:

`NO IMPACT`

with an explanation that no matching operational dependency was found.

---

## R09 — Ambiguous Disruption

If critical information is missing or ambiguous, the system should identify the missing information and avoid making unsupported operational recommendations.

Examples:

* Unknown supplier.
* Unknown product.
* Unknown shipment.
* Unknown warehouse.

---

## R10 — Trade-Off Transparency

Every feasible operational option should display its primary trade-off.

Examples:

### Reallocation

Benefit:

* Uses existing inventory.

Trade-off:

* Reduces stock at another warehouse.

### Expedite

Benefit:

* May accelerate inbound replenishment.

Trade-off:

* Additional transportation cost.

### Part-Ship

Benefit:

* Customer receives available quantity sooner.

Trade-off:

* Remaining quantity is delayed.

### Customer Notification

Benefit:

* Improves customer transparency.

Trade-off:

* Customer may receive an uncertain revised delivery date.

---

## R11 — Recommendation Priority

When comparing options, SupplyGuard AI should prefer:

1. Full shortage resolution with available inventory.
2. The option with the highest fulfillment coverage.
3. Inbound recovery options such as expediting.
4. Partial shipment.
5. Customer notification when no operational recovery option is sufficient.

The final recommendation must remain subject to human approval.

---

## R12 — No Invented Facts

The system must not invent:

* Inventory quantities.
* Shipment dates.
* Transportation costs.
* Customer commitments.
* Supplier capabilities.
* Delivery dates.

If required information is unavailable, the system must state that it is unavailable.
