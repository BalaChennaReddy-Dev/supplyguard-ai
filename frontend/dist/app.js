const noticeInput = document.getElementById("notice");
const analyzeButton = document.getElementById("analyzeBtn");
const statusElement = document.getElementById("status");
const resultsElement = document.getElementById("results");

analyzeButton.addEventListener("click", analyzeDisruption);


async function analyzeDisruption() {
    const notice = noticeInput.value.trim();

    if (!notice) {
        statusElement.textContent = "Please enter a disruption notice.";
        statusElement.className = "error";
        return;
    }

    analyzeButton.disabled = true;
    statusElement.className = "";
    statusElement.textContent =
        "Analyzing disruption with SupplyGuard AI...";
    resultsElement.classList.add("hidden");

    try {
        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                notice: notice,
                analysis_date: new Date()
                    .toISOString()
                    .slice(0, 10)
            })
        });

        const contentType =
            response.headers.get("content-type") || "";

        const data = contentType.includes("application/json")
            ? await response.json()
            : {
                detail: await response.text()
            };

        if (!response.ok) {
            throw new Error(
                data.detail || "Analysis failed."
            );
        }

        renderResults(data);

        statusElement.textContent =
            "Analysis completed successfully.";
        statusElement.className = "success";

    } catch (error) {
        console.error(error);

        statusElement.textContent =
            error.message || "Analysis failed.";

        statusElement.className = "error";

    } finally {
        analyzeButton.disabled = false;
    }
}


function renderResults(data) {
    const impact = data.impact || {};
    const recommendations = Array.isArray(data.recommendations)
        ? data.recommendations
        : [];

    renderImpact(impact);

    renderDisruptionDetails(
        data.extraction || {},
        data.resolved || {}
    );

    renderImpactDetails(impact);

    renderRecommendation(recommendations);

    renderResponseOptions(recommendations);

    renderOrders(
        impact.prioritized_orders || []
    );

    renderImpactGraph(
        impact.impact_graph || {}
    );

    renderEvidence(
        recommendations
    );

    resultsElement.classList.remove("hidden");
}


function renderImpact(impact) {
    const metrics = [
        {
            label: "Impact Status",
            value: formatLabel(
                impact.impact_status || "Unknown"
            )
        },
        {
            label: "Impact Found",
            value: impact.impact_found
                ? "Yes"
                : "No"
        },
        {
            label: "Affected Shipments",
            value: (
                impact.affected_shipments || []
            ).length
        },
        {
            label: "At-Risk Orders",
            value: (
                impact.at_risk_orders || []
            ).length
        },
        {
            label: "Affected Customers",
            value: (
                impact.affected_customers || []
            ).length
        },
        {
            label: "Priority Orders",
            value: (
                impact.prioritized_orders || []
            ).length
        }
    ];

    document.getElementById(
        "impactMetrics"
    ).innerHTML = metrics
        .map(metric => `
            <div class="metric">
                <div class="metric-label">
                    ${escapeHtml(metric.label)}
                </div>

                <div class="metric-value">
                    ${escapeHtml(
                        String(metric.value)
                    )}
                </div>
            </div>
        `)
        .join("");
}


function renderDisruptionDetails(
    extraction,
    resolved
) {
    const supplier = resolved.supplier;
    const products = resolved.products || [];

    const details = [
        {
            label: "Event Type",
            value: formatLabel(
                extraction.event_type ||
                "Unknown"
            )
        },
        {
            label: "Supplier",
            value:
                supplier?.supplier_name ||
                extraction.supplier_name ||
                "Not identified"
        },
        {
            label: "Location",
            value:
                supplier?.location ||
                extraction.location ||
                "Not identified"
        },
        {
            label: "Start Date",
            value:
                extraction.start_date ||
                "Not identified"
        },
        {
            label: "Duration",
            value: extraction.duration_days
                ? `${extraction.duration_days} days`
                : "Not identified"
        },
        {
            label: "Confidence",
            value:
                extraction.confidence !== undefined
                    ? `${Math.round(
                        extraction.confidence * 100
                    )}%`
                    : "N/A"
        }
    ];

    const productNames = products.length
        ? products
            .map(product =>
                product.product_name
            )
            .join(", ")
        : (
            extraction.affected_products || []
        ).join(", ");

    details.push({
        label: "Affected Products",
        value:
            productNames ||
            "Not identified"
    });

    document.getElementById(
        "disruptionDetails"
    ).innerHTML = details
        .map(item => `
            <div class="detail-card">
                <div class="metric-label">
                    ${escapeHtml(item.label)}
                </div>

                <div class="detail-value">
                    ${escapeHtml(
                        String(item.value)
                    )}
                </div>
            </div>
        `)
        .join("");
}


function renderImpactDetails(impact) {
    const shipments =
        impact.affected_shipments || [];

    const inventory =
        impact.inventory_summary || [];

    const orders =
        impact.at_risk_orders || [];

    const customers =
        impact.affected_customers || [];

    const cards = [
        {
            label: "Affected Shipments",
            value: shipments.length,
            description: shipments.length
                ? shipments
                    .map(item =>
                        `${item.shipment_id}: ${item.quantity} units`
                    )
                    .join(" · ")
                : "No affected shipments"
        },
        {
            label: "Inventory Dependencies",
            value: inventory.length,
            description: inventory.length
                ? inventory
                    .map(item =>
                        `${item.warehouse_id} / ${item.product_id}: ${item.available_quantity} available`
                    )
                    .join(" · ")
                : "No inventory dependencies"
        },
        {
            label: "Customer Orders at Risk",
            value: orders.length,
            description: orders.length
                ? orders
                    .map(item =>
                        `${item.order_id}: ${item.shortage_quantity} unit shortage`
                    )
                    .join(" · ")
                : "No at-risk orders"
        },
        {
            label: "Affected Customers",
            value: customers.length,
            description: customers.length
                ? customers
                    .map(item =>
                        item.customer_name
                    )
                    .join(" · ")
                : "No affected customers"
        }
    ];

    document.getElementById(
        "impactDetails"
    ).innerHTML = cards
        .map(card => `
            <div class="metric">
                <div class="metric-label">
                    ${escapeHtml(card.label)}
                </div>

                <div class="metric-value">
                    ${escapeHtml(
                        String(card.value)
                    )}
                </div>

                <p class="card-description">
                    ${escapeHtml(
                        card.description
                    )}
                </p>
            </div>
        `)
        .join("");
}


function renderRecommendation(
    recommendations
) {
    const container =
        document.getElementById(
            "recommendation"
        );

    if (!recommendations.length) {
        container.innerHTML = `
            <div class="recommendation no-action">
                <div class="recommendation-header">
                    <span class="action-badge">
                        NO ACTION
                    </span>
                </div>

                <h3>
                    No operational action recommended
                </h3>

                <p>
                    No affected customer order currently
                    requires an operational response.
                </p>
            </div>
        `;

        return;
    }

    const recommendation =
        recommendations[0];

    const action =
        recommendation.recommended_action ||
        "NO_ACTION";

    container.innerHTML = `
        <div class="recommendation">

            <div class="recommendation-header">

                <span class="action-badge">
                    ${escapeHtml(action)}
                </span>

                ${
                    recommendation.requires_human_approval
                        ? `
                            <span class="approval-badge">
                                Human approval required
                            </span>
                        `
                        : `
                            <span class="approval-badge">
                                Review recommended
                            </span>
                        `
                }

            </div>

            <h3>
                Recommended Action:
                ${escapeHtml(action)}
            </h3>

            <p>
                ${escapeHtml(
                    recommendation.recommendation_reason ||
                    "No recommendation reason provided."
                )}
            </p>

            <div class="recommendation-summary">

                <div>
                    <span>Order</span>
                    <strong>
                        ${escapeHtml(
                            recommendation.order_id ||
                            "N/A"
                        )}
                    </strong>
                </div>

                <div>
                    <span>Shortage</span>
                    <strong>
                        ${escapeHtml(
                            String(
                                recommendation.shortage_quantity ??
                                0
                            )
                        )} units
                    </strong>
                </div>

                <div>
                    <span>Priority</span>
                    <strong>
                        ${escapeHtml(
                            recommendation.priority ||
                            "N/A"
                        )}
                    </strong>
                </div>

                <div>
                    <span>Evidence</span>
                    <strong>
                        ${
                            recommendation.evidence_required
                                ? "Required"
                                : "Not required"
                        }
                    </strong>
                </div>

            </div>

        </div>
    `;
}


function renderResponseOptions(
    recommendations
) {
    const container =
        document.getElementById(
            "responseOptions"
        );

    if (!recommendations.length) {
        container.innerHTML = `
            <p class="empty-state">
                No response options are required because
                no customer order is currently at risk.
            </p>
        `;

        return;
    }

    const recommendation =
        recommendations[0];

    const options =
        recommendation.options || [];

    if (!options.length) {
        container.innerHTML = `
            <p class="empty-state">
                No response options available.
            </p>
        `;

        return;
    }

    container.innerHTML = options
        .map(option => `
            <div class="
                option-card
                ${
                    option.feasible
                        ? "feasible"
                        : "not-feasible"
                }
            ">

                <div class="option-header">

                    <div>
                        <span class="option-action">
                            ${escapeHtml(
                                option.action ||
                                "OPTION"
                            )}
                        </span>

                        <span class="policy-rule">
                            ${escapeHtml(
                                option.policy_rule ||
                                "Policy"
                            )}
                        </span>
                    </div>

                    <span class="feasibility">
                        ${
                            option.feasible
                                ? "FEASIBLE"
                                : "NOT FEASIBLE"
                        }
                    </span>

                </div>

                <p>
                    ${escapeHtml(
                        option.reason || ""
                    )}
                </p>

                ${
                    option.coverage_quantity !==
                        undefined
                        ? `
                            <div class="option-metrics">

                                <span>
                                    Coverage:
                                    <strong>
                                        ${escapeHtml(
                                            String(
                                                option.coverage_quantity
                                            )
                                        )}
                                        units
                                    </strong>
                                </span>

                                <span>
                                    ${escapeHtml(
                                        String(
                                            option.coverage_percentage ||
                                            0
                                        )
                                    )}% of shortage
                                </span>

                            </div>
                        `
                        : ""
                }

                <div class="trade-off">
                    <strong>
                        Trade-off:
                    </strong>

                    ${escapeHtml(
                        option.trade_off ||
                        "No trade-off specified."
                    )}
                </div>

            </div>
        `)
        .join("");
}


function renderOrders(orders) {
    const container =
        document.getElementById(
            "orders"
        );

    if (!orders.length) {
        container.innerHTML = `
            <p class="empty-state">
                No at-risk orders identified.
            </p>
        `;

        return;
    }

    container.innerHTML = orders
        .map(order => `
            <div class="order-card">

                <div class="order-main">

                    <div>

                        <div class="order-id">
                            ${escapeHtml(
                                order.order_id
                            )}
                        </div>

                        <div class="order-customer">
                            ${escapeHtml(
                                order.customer_name ||
                                "Unknown customer"
                            )}

                            ·

                            ${escapeHtml(
                                order.product_id ||
                                "Unknown product"
                            )}
                        </div>

                    </div>

                    <div class="
                        priority-badge
                        ${getPriorityClass(
                            order.priority
                        )}
                    ">
                        ${escapeHtml(
                            order.priority ||
                            "UNKNOWN"
                        )}
                    </div>

                </div>

                <div class="order-metrics">

                    <div>
                        <span>
                            Order Quantity
                        </span>

                        <strong>
                            ${escapeHtml(
                                String(
                                    order.quantity ?? 0
                                )
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>
                            Fulfillable
                        </span>

                        <strong>
                            ${escapeHtml(
                                String(
                                    order.fulfillable_quantity ??
                                    0
                                )
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>
                            Shortage
                        </span>

                        <strong class="shortage">
                            ${escapeHtml(
                                String(
                                    order.shortage_quantity ??
                                    0
                                )
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>
                            Priority Score
                        </span>

                        <strong>
                            ${escapeHtml(
                                String(
                                    order.priority_score ??
                                    0
                                )
                            )}
                        </strong>
                    </div>

                    <div>
                        <span>
                            Required Date
                        </span>

                        <strong>
                            ${escapeHtml(
                                order.required_date ||
                                "N/A"
                            )}
                        </strong>
                    </div>

                </div>

                <div class="order-reasons">

                    ${
                        (order.reasons || [])
                            .map(reason => `
                                <span class="reason-tag">
                                    ${escapeHtml(
                                        reason
                                    )}
                                </span>
                            `)
                            .join("")
                    }

                </div>

            </div>
        `)
        .join("");
}


function renderImpactGraph(graph) {
    const container =
        document.getElementById(
            "impactGraph"
        );

    const nodes =
        graph.nodes || [];

    const edges =
        graph.edges || [];

    if (!nodes.length) {
        container.innerHTML = `
            <p class="empty-state">
                No impact graph available.
            </p>
        `;

        return;
    }

    const typeCounts = {};

    nodes.forEach(node => {
        const type =
            String(
                node.type || "unknown"
            ).toLowerCase();

        typeCounts[type] =
            (typeCounts[type] || 0) + 1;
    });

    const nodeLookup = {};

    nodes.forEach(node => {
        nodeLookup[node.id] = node;
    });

    const typeLabels =
        Object.entries(typeCounts)
            .map(([type, count]) => `
                <div class="graph-stat">
                    <span>
                        ${escapeHtml(
                            formatLabel(type)
                        )}
                    </span>

                    <strong>
                        ${escapeHtml(
                            String(count)
                        )}
                    </strong>
                </div>
            `)
            .join("");

    const flowTypes = [
        "supplier",
        "product",
        "shipment",
        "warehouse",
        "inventory",
        "order",
        "customer"
    ];

    const flowNodes =
        flowTypes
            .map(type => {

                const matchingNodes =
                    nodes.filter(node =>
                        String(
                            node.type || ""
                        ).toLowerCase() === type
                    );

                if (!matchingNodes.length) {
                    return `
                        <div class="
                            flow-column
                            empty-flow
                        ">

                            <div class="flow-type">
                                ${escapeHtml(
                                    formatLabel(type)
                                )}
                            </div>

                            <div class="
                                flow-node
                                muted
                            ">
                                No affected
                                ${escapeHtml(
                                    formatLabel(
                                        type
                                    ).toLowerCase()
                                )}
                            </div>

                        </div>
                    `;
                }

                return `
                    <div class="flow-column">

                        <div class="flow-type">
                            ${escapeHtml(
                                formatLabel(type)
                            )}
                        </div>

                        <div class="flow-node-list">

                            ${matchingNodes
                                .map(node => {

                                    const label =
                                        node.label ||
                                        node.name ||
                                        node.id ||
                                        "Unknown";

                                    return `
                                        <div class="
                                            flow-node
                                            affected
                                        ">

                                            <strong>
                                                ${escapeHtml(
                                                    label
                                                )}
                                            </strong>

                                            ${
                                                node.id &&
                                                node.id !== label
                                                    ? `
                                                        <span>
                                                            ${escapeHtml(
                                                                node.id
                                                            )}
                                                        </span>
                                                    `
                                                    : ""
                                            }

                                        </div>
                                    `;
                                })
                                .join("")}

                        </div>

                    </div>
                `;
            })
            .join("");

    const edgeRows =
        edges
            .map(edge => {

                const sourceNode =
                    nodeLookup[
                        edge.source
                    ] || {};

                const targetNode =
                    nodeLookup[
                        edge.target
                    ] || {};

                const sourceLabel =
                    sourceNode.label ||
                    sourceNode.name ||
                    edge.source ||
                    "Unknown";

                const targetLabel =
                    targetNode.label ||
                    targetNode.name ||
                    edge.target ||
                    "Unknown";

                return `
                    <div class="graph-edge">

                        <span class="graph-node">
                            ${escapeHtml(
                                sourceLabel
                            )}
                        </span>

                        <span class="graph-arrow">
                            ?
                        </span>

                        <span class="graph-node">
                            ${escapeHtml(
                                targetLabel
                            )}
                        </span>

                        <span class="graph-relationship">
                            ${escapeHtml(
                                edge.relationship ||
                                "RELATED"
                            )}
                        </span>

                    </div>
                `;
            })
            .join("");

    container.innerHTML = `

        <div class="graph-summary">

            <div class="graph-stat">

                <span>
                    Total Nodes
                </span>

                <strong>
                    ${escapeHtml(
                        String(
                            graph.node_count ||
                            nodes.length
                        )
                    )}
                </strong>

            </div>

            <div class="graph-stat">

                <span>
                    Total Relationships
                </span>

                <strong>
                    ${escapeHtml(
                        String(
                            graph.edge_count ||
                            edges.length
                        )
                    )}
                </strong>

            </div>

            ${typeLabels}

        </div>


        <div class="graph-path">

            <div class="graph-path-title">
                Disruption propagation
            </div>

            <div class="impact-flow">
                ${flowNodes}
            </div>

        </div>


        <div class="graph-path">

            <div class="graph-path-title">
                Traceable relationships
            </div>

            <div class="graph-edges">
                ${edgeRows}
            </div>

        </div>
    `;
}


function renderEvidence(
    recommendations
) {
    const container =
        document.getElementById(
            "evidence"
        );

    const evidenceMap =
        new Map();

    recommendations.forEach(
        recommendation => {

            (
                recommendation.evidence ||
                []
            ).forEach(item => {

                const key =
                    `${item.source}|${item.record_id}|${item.fact}`;

                if (!evidenceMap.has(key)) {
                    evidenceMap.set(
                        key,
                        item
                    );
                }
            });


            (
                recommendation.options ||
                []
            ).forEach(option => {

                (
                    option.evidence ||
                    []
                ).forEach(item => {

                    const fact =
                        item.fact ||
                        item.detail ||
                        "";

                    const key =
                        `${item.source}|${item.record_id}|${fact}`;

                    if (!evidenceMap.has(key)) {
                        evidenceMap.set(
                            key,
                            {
                                source:
                                    item.source,
                                record_id:
                                    item.record_id,
                                fact:
                                    fact
                            }
                        );
                    }
                });
            });
        }
    );

    const evidence =
        Array.from(
            evidenceMap.values()
        );

    if (!evidence.length) {
        container.innerHTML = `
            <p class="empty-state">
                No evidence records returned.
            </p>
        `;

        return;
    }

    container.innerHTML =
        evidence
            .map(item => `
                <div class="evidence-item">

                    <div class="evidence-source">
                        ${escapeHtml(
                            item.source ||
                            "Unknown source"
                        )}
                    </div>

                    <div class="evidence-record">
                        ${escapeHtml(
                            item.record_id ||
                            ""
                        )}
                    </div>

                    <p>
                        ${escapeHtml(
                            item.fact ||
                            ""
                        )}
                    </p>

                </div>
            `)
            .join("");
}


function getPriorityClass(
    priority
) {
    if (priority === "CRITICAL") {
        return "priority-critical";
    }

    if (priority === "HIGH") {
        return "priority-high";
    }

    if (priority === "MEDIUM") {
        return "priority-medium";
    }

    return "priority-low";
}


function formatLabel(value) {
    return String(value)
        .replaceAll("_", " ")
        .replace(
            /\b\w/g,
            char => char.toUpperCase()
        );
}


function escapeHtml(value) {
    return String(value)
        .replaceAll(
            "&",
            "&amp;"
        )
        .replaceAll(
            "<",
            "&lt;"
        )
        .replaceAll(
            ">",
            "&gt;"
        )
        .replaceAll(
            '"',
            "&quot;"
        )
        .replaceAll(
            "'",
            "&#039;"
        );
}
