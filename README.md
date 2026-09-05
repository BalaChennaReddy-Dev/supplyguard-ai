# SupplyGuard AI

## AI-Powered Supply Chain Disruption Response Assistant

SupplyGuard AI is an intelligent disruption-response assistant designed to help supply-chain teams understand disruption notices, identify operational impact, prioritize affected orders, and recommend response options.

The system combines Google Gemini AI with deterministic local supply-chain analysis to transform an unstructured disruption notice into a traceable operational response.

> **AI interprets. Local systems calculate. AI explains. Humans approve.**

---

## Problem Statement

Supply-chain disruptions are often communicated through unstructured messages such as:

- Supplier production shutdowns
- Carrier delays
- Warehouse incidents
- Production interruptions
- Transportation disruptions

A disruption notice alone does not immediately tell an operations team:

- Which products are affected?
- Which shipments are at risk?
- Which warehouses are impacted?
- Which customer orders may be delayed?
- Which customers should be prioritized?
- What response options are available?
- Why is a particular response recommended?

SupplyGuard AI addresses this problem by connecting the disruption notice with operational supply-chain data and producing an explainable response plan.

---

## Solution

SupplyGuard AI follows a hybrid AI + deterministic architecture:

```text
Unstructured Disruption Notice
            |
            v
       Gemini AI
            |
            v
Structured Disruption Information
            |
            v
Local Entity Matching
            |
            v
Deterministic Impact Analysis
            |
            v
Order Priority Engine
            |
            v
Response Recommendation
            |
            v
Evidence + Impact Graph
            |
            v
       Human Approval
```

The core design principle is:

> **AI interprets. Local deterministic systems calculate. AI explains. Humans approve.**

This separation ensures that the language model is not responsible for inventing operational business impacts.

---

## Key Features

### 1. AI-Powered Disruption Understanding

SupplyGuard AI uses Gemini to understand unstructured disruption notices and extract structured information such as:

- Disruption type
- Supplier
- Location
- Shipment
- Warehouse
- Start date
- Duration
- Affected products
- Confidence
- Missing information

This allows natural-language disruption messages to be connected with structured operational data.

### 2. Local Entity Resolution

Extracted entities are matched against the application's own supply-chain datasets.

The system can resolve:

- Suppliers
- Products
- Shipments
- Warehouses
- Customers
- Orders

This prevents the AI from making unsupported assumptions about the company's operational environment.

### 3. Deterministic Supply Chain Impact Analysis

After entity resolution, the system calculates the operational impact using local data.

It evaluates relationships across:

- Suppliers
- Products
- Shipments
- Warehouses
- Inventory
- Orders
- Customers

The system identifies confirmed downstream impact instead of relying on an AI-generated guess.

### 4. Explainable Order Prioritization

Affected orders are ranked using deterministic priority signals such as:

- Customer importance
- Customer criticality
- Required delivery date
- Quantity shortage
- Available inventory

This helps operations teams identify which orders require attention first.

### 5. Response Recommendations

SupplyGuard AI recommends appropriate response options based on the calculated impact.

Possible responses include:

- Reallocate inventory
- Part-ship available inventory
- Expedite
- Notify the customer
- Escalate for human decision

The system provides recommendations rather than automatically executing supply-chain actions.

### 6. Evidence and Traceability

Important impact claims are connected to the underlying operational data.

Users can understand:

- Why an order is affected
- Which product caused the dependency
- Which shipment is involved
- Which warehouse is involved
- What inventory was considered
- Why an order received its priority
- Why a response was recommended

This makes the system more explainable and auditable.

### 7. Impact Graph

The application's Impact Graph visualizes how a disruption propagates through the supply chain.

```text
Supplier -> SKU/Product -> Shipment -> Warehouse -> Inventory -> Order -> Customer
```

This gives operations teams a visual representation of the complete disruption path.

### 8. No-Impact Detection

If a disruption cannot be mapped to the operational data, SupplyGuard AI does not invent an impact.

Instead, it returns a safe result such as:

```text
Impact Found: No
Status: No Impact
At-Risk Orders: 0
```

This is important for preventing unsupported AI-generated business claims.

### 9. Human-in-the-Loop Decision Making

Supply-chain actions can have financial, operational, and customer consequences.

Therefore, SupplyGuard AI recommends actions but does not autonomously execute:

- Inventory transfers
- Shipment changes
- Customer notifications
- Expedite requests
- Order modifications

A human operator remains responsible for approving the final action.

---

## Technology Stack

### Backend

- Python 3.11+
- FastAPI
- Uvicorn
- Pandas
- NumPy

### Artificial Intelligence

- Google Gemini
- Gemini structured extraction
- Gemini embeddings
- `gemini-embedding-001`
- `gemini-3.6-flash`

### Retrieval

- FAISS
- Local semantic retrieval
- Supply-chain operational data
- Response playbooks

### Frontend

- HTML5
- CSS3
- JavaScript

### Configuration

- python-dotenv

---

## System Architecture

```text
                         +----------------------+
                         |  Disruption Notice   |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |      Gemini AI       |
                         | Notice Interpretation|
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Structured Event     |
                         | Extraction           |
                         +----------+-----------+
                                    |
                                    v
                    +-------------------------------+
                    | Local Entity Resolution       |
                    +---------------+---------------+
                                    |
                                    v
                    +-------------------------------+
                    | Deterministic Impact Engine   |
                    +---------------+---------------+
                                    |
                     +--------------+--------------+
                     |                             |
                     v                             v
             +---------------+             +---------------+
             | Priority      |             | Impact Graph  |
             | Engine        |             | + Evidence    |
             +-------+-------+             +---------------+
                     |
                     v
             +---------------+
             | Recommendation|
             | Engine        |
             +-------+-------+
                     |
                     v
             +---------------+
             | Human Approval|
             +---------------+
```

---

## Impact Propagation Model

The core business relationship is:

```text
Supplier
    |
    +---- Product
            |
            +---- Shipment
                    |
                    +---- Warehouse
                            |
                            +---- Inventory
                                    |
                                    +---- Order
                                            |
                                            +---- Customer
```

This allows the application to answer:

> **"Who and what is actually affected by this disruption?"**

Instead of simply reporting that a supplier has stopped production, SupplyGuard AI traces the disruption through the operational network.

---

## Example: Supplier Production Shutdown

### Input Disruption

```text
Alpha Components Ltd in Chennai has reported an equipment failure
at its production facility. The facility will be shut down for
10 days starting September 5, 2026. Industrial Control Boards
and Power Supply Modules are affected.
```

### AI Interpretation

The AI extracts information similar to:

```text
Event Type: Production Shutdown
Supplier: Alpha Components Ltd
Location: Chennai
Start Date: 2026-09-05
Duration: 10 days

Affected Products:
- Industrial Control Board
- Power Supply Module
```

### Operational Impact

The structured disruption is mapped to the local supply-chain data.

Example affected order:

```text
Order: ORD013
Customer: Vertex Robotics
Product: Industrial Control Board
Order Quantity: 50
Available Quantity: 10
Shortage: 40
Priority: HIGH
```

### Recommended Response

```text
Recommendation: REALLOCATE
```

Possible supporting options include:

- Reallocate inventory from another warehouse
- Part-ship the available quantity
- Notify the affected customer
- Obtain human approval before execution

---

## Example Impact Graph

For the supplier shutdown scenario, the disruption can be traced through a relationship similar to:

```text
Alpha Components Ltd
        |
        v
Industrial Control Board
        |
        v
Shipment
        |
        v
Chennai Warehouse
        |
        v
Inventory
        |
        v
ORD013
        |
        v
Vertex Robotics
```

Every stage represents an operational relationship that can be inspected by the system.

---

## Test Scenarios

SupplyGuard AI includes scenarios covering confirmed impact, delayed transportation, warehouse incidents, ambiguous notices, and no-impact disruptions.

### Scenario 1 — Supplier Shutdown

Tests:

- Supplier resolution
- Product resolution
- Shipment impact
- Inventory impact
- Order impact
- Priority calculation
- Response recommendation
- Evidence generation
- Impact graph generation

### Scenario 2 — Carrier Delay

Tests:

- Shipment identification
- Carrier delay interpretation
- Delayed shipment propagation
- Downstream order analysis
- Response recommendation

### Scenario 3 — Warehouse Incident

Tests:

- Warehouse resolution
- Inventory impact
- Downstream order analysis
- Avoidance of unsupported quantities
- Human approval boundary

### Scenario 4 — Ambiguous Disruption

Tests:

- Missing supplier information
- Missing product information
- Ambiguous disruption mapping
- Missing information handling
- Escalation instead of unsupported conclusions

### Scenario 5 — No Impact

Tests:

- Disruption mapping failure
- No-impact classification
- Prevention of fabricated business impact
- Zero at-risk orders

Example:

```text
Impact Found: No
Status: No Impact
At-Risk Orders: 0
```

---

## AI and Data Grounding

SupplyGuard AI does not rely on the language model alone to determine supply-chain impact.

The system separates AI responsibilities from deterministic business logic.

### AI Responsibilities

- Understand natural-language disruption notices
- Extract structured disruption information
- Resolve natural-language entities
- Retrieve relevant response guidance
- Explain recommendations

### Deterministic System Responsibilities

- Match entities against operational data
- Calculate inventory availability
- Calculate shortages
- Identify affected orders
- Calculate order priority
- Build impact relationships
- Generate traceable evidence

This architecture reduces hallucination risk and makes operational decisions easier to validate.

---

## Retrieval-Augmented Response Guidance

SupplyGuard AI uses local semantic retrieval to identify relevant response guidance from the application's own knowledge and playbook data.

Gemini embeddings are used to represent relevant text, while FAISS provides local similarity search.

The retrieved guidance supports response recommendations rather than allowing the model to independently invent operational procedures.

---

## Safety and Edge Cases

The system is designed to avoid unsupported conclusions.

It handles cases such as:

- Unknown suppliers
- Unknown products
- Missing shipment information
- Ambiguous disruption notices
- Warehouse disruptions without confirmed inventory impact
- Disruptions that map to no operational data
- Insufficient evidence for a recommendation

When evidence is insufficient, the system can identify missing information or return a no-impact or escalation result rather than fabricating an answer.

---

## Human Approval Boundary

SupplyGuard AI follows a recommendation-only model.

```text
AI
 |
 | Understand
 v
System
 |
 | Calculate
 v
Recommendation
 |
 | Explain + Provide Evidence
 v
Human Operator
 |
 | Approve / Reject
 v
Business Action
```

The application does not directly execute the recommended operational action.

This preserves human control over decisions involving inventory, customers, shipments, and fulfillment.

---

## Project Structure

```text
supplyguard-ai/
|
+-- app.py
+-- requirements.txt
+-- README.md
+-- .gitignore
|
+-- data/
|   +-- suppliers.csv
|   +-- products.csv
|   +-- warehouses.csv
|   +-- inventory.csv
|   +-- shipments.csv
|   +-- customers.csv
|   +-- orders.csv
|   +-- disruptions/
|
+-- src/
|   +-- api/
|   +-- engine/
|   +-- ...
|
+-- frontend/
    +-- dist/
        +-- index.html
        +-- app.js
        +-- styles.css
```

---

## Requirements

Before running the application, make sure the following are available:

- Python 3.11+
- Gemini API key
- Internet connection for Gemini API access

The application is designed to run with a single command after dependencies and configuration are prepared.

---

## Installation

Clone the repository:

```powershell
git clone https://github.com/BalaChennaReddy-Dev/supplyguard-ai.git
cd supplyguard-ai
```

Create a virtual environment:

```powershell
python -m venv venv
```

Activate the virtual environment on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Install the required packages:

```powershell
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Replace `your_gemini_api_key` with your Gemini API key.

The `.env` file contains sensitive credentials and must never be committed to Git.

---

## Run the Application

Start the application using:

```powershell
python app.py
```

The application will start on:

```text
http://localhost:8000
```

Open the URL in your browser.

The complete application, including the frontend and API, is served from the same application. No separate frontend server is required.

---

## API

### Health Check

```text
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "gemini_configured": true
}
```

### Analyze Disruption

```text
POST /api/analyze
```

Example request:

```json
{
  "notice": "Alpha Components Ltd has stopped production for 10 days."
}
```

Optional analysis date:

```json
{
  "notice": "Alpha Components Ltd has stopped production for 10 days.",
  "analysis_date": "2026-09-05"
}
```

The API returns structured information containing disruption interpretation, operational impact, priority information, recommendations, evidence, and impact graph information.

---

## Sample Disruption Notices

### Supplier Shutdown

```text
Alpha Components Ltd in Chennai has reported an equipment failure
at its production facility. The facility will be shut down for
10 days starting September 5, 2026. Industrial Control Boards
and Power Supply Modules are affected.
```

### Carrier Delay

```text
Shipment SHIP005 carrying Motor Controllers to the Bengaluru
Distribution Center has been delayed by approximately 5 days.
```

### Warehouse Incident

```text
A water leakage incident has occurred at the Bengaluru Distribution
Center. The affected section may be unavailable for approximately
3 days starting September 6, 2026.
```

### Ambiguous Disruption

```text
A disruption has occurred at a southern facility for approximately
one week, but the affected supplier and products have not yet been
confirmed.
```

### No-Impact Scenario

```text
Omega Materials Corporation in Mumbai is experiencing a 7-day issue
starting September 5, 2026. The affected product line is currently
under review.
```

---

## Expected Behavior

For a confirmed disruption, SupplyGuard AI should provide:

- Disruption interpretation
- Resolved entities
- Confirmed operational impact
- Affected shipments
- Affected orders
- Order priority
- Recommended response
- Response options
- Evidence
- Impact graph
- Human approval requirement

For a disruption with no confirmed operational mapping, the system should return a no-impact or escalation result instead of inventing affected entities or quantities.

---

## Troubleshooting

### Gemini API Key Not Configured

If the health endpoint reports:

```json
{
  "gemini_configured": false
}
```

check that the `.env` file exists in the project root and contains:

```text
GEMINI_API_KEY=your_gemini_api_key
```

Restart the application after changing the environment file.

---

### Port 8000 Already in Use

If port `8000` is already being used, stop the process using that port and run:

```powershell
python app.py
```

The project is configured to serve the complete application on port `8000`.

---

### Dependency Installation Problems

Make sure the virtual environment is active:

```powershell
.\venv\Scripts\Activate.ps1
```

Then reinstall the dependencies:

```powershell
pip install -r requirements.txt
```

---

### Application Does Not Start

Verify the Python version:

```powershell
python --version
```

Python 3.11 or newer is recommended.

Then verify that the main application file exists:

```powershell
Test-Path .\app.py
```

It should return:

```text
True
```

---

### Frontend Does Not Load

Make sure the frontend build files exist:

```powershell
Test-Path .\frontend\dist\index.html
```

It should return:

```text
True
```

Then restart:

```powershell
python app.py
```

Open:

```text
http://localhost:8000
```

---

### API Returns an Analysis Error

First verify the health endpoint:

```text
http://localhost:8000/health
```

If Gemini is configured correctly, retry the disruption analysis.

For ambiguous notices, provide additional information such as:

- Supplier name
- Product
- Shipment ID
- Warehouse
- Start date
- Expected duration

This allows the system to establish a stronger operational mapping.

---

## Why SupplyGuard AI?

Traditional disruption monitoring can identify that something went wrong.

SupplyGuard AI focuses on the next operational questions:

> **What does this disruption actually affect?**

> **Which orders should we prioritize?**

> **What response options are available?**

> **Why is this response recommended?**

The system connects unstructured disruption information with operational supply-chain data and produces a traceable response recommendation.

---

## Key Differentiator

The core differentiator is the combination of:

```text
Natural Language Understanding
             +
Operational Data
             +
Deterministic Impact Analysis
             +
Explainable Prioritization
             +
Response Recommendations
             +
Evidence
             +
Impact Graph
             +
Human Approval
```

This creates a practical decision-support system rather than a generic AI chatbot.

---

## Design Philosophy

SupplyGuard AI is built around four principles:

### Interpret

Use AI to understand messy, unstructured disruption information.

### Calculate

Use deterministic local systems to calculate operational impact.

### Explain

Use AI and structured evidence to communicate the reasoning clearly.

### Approve

Keep humans responsible for consequential business decisions.

---

## Core Design Principle

```text
AI interprets.
      |
      v
Local systems calculate.
      |
      v
AI explains.
      |
      v
Humans approve.
```

---

## Project Information

**Project:** SupplyGuard AI

**Track:** PS08 — Supply Chain — Disruption Response Assistant

**Repository:**  
https://github.com/BalaChennaReddy-Dev/supplyguard-ai

---

## Hackathon Focus

SupplyGuard AI demonstrates how generative AI can be combined with deterministic business systems to support supply-chain disruption response.

The project focuses on:

- Grounded AI
- Explainability
- Traceability
- Human-in-the-loop decision making
- Operational impact analysis
- Safe handling of uncertainty
- Action recommendations without autonomous execution

---

## License

This project was developed as a hackathon/project prototype for demonstrating AI-assisted supply-chain disruption response.
