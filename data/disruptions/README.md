# Disruption Test Scenarios

These disruption notices are synthetic test inputs for SupplyGuard AI.

## 1. supplier_shutdown.txt

Tests a supplier-level production shutdown.

Expected behavior:
- Identify the supplier.
- Identify potentially affected products.
- Find related shipments.
- Trace affected inventory.
- Identify affected customer orders.
- Calculate potential delivery impact.
- Generate mitigation options.

## 2. carrier_delay.txt

Tests a shipment-specific transportation delay.

Expected behavior:
- Identify the shipment.
- Trace the shipment to its product and warehouse.
- Identify customer orders dependent on the affected supply.
- Estimate delivery impact.

## 3. warehouse_incident.txt

Tests a warehouse-level disruption.

Expected behavior:
- Identify the warehouse.
- Determine potentially affected inventory.
- Identify customer orders using that inventory.
- Recommend possible stock reallocation.

## 4. ambiguous_disruption.txt

Tests uncertainty handling.

Expected behavior:
- Do not guess the supplier.
- Do not invent affected products.
- Identify missing information.
- Request clarification.

## 5. no_impact_disruption.txt

Tests the no-impact path.

Expected behavior:
- Map the notice to available operational data.
- Check active shipments and customer commitments.
- Return no current business impact when no actionable dependency exists.