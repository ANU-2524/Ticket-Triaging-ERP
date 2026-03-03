# Ticket-Triaging-ERP

## AI-Powered ERP Ticket Triage System

This project analyzes ERP support tickets and returns structured triage data (category, priority, module, routing, and first response) using Groq with LLaMA 3.3 70B.

---

## Features

| Feature | Description |
|---|---|
| **Auto-Classification** | Categorizes tickets into Finance, Inventory, Procurement, HR, or General |
| **ERP Module Detection** | Identifies Oracle Fusion, SAP, Microsoft Dynamics, or Generic ERP |
| **Issue Type Recognition** | Issue, Change Request, Support Request, or Information Request |
| **Priority Scoring** | Assigns High, Medium, or Low with reasoning |
| **Confidence Score** | Model self-assessed certainty for the classification |
| **Team Routing** | Suggests the responsible support team |
| **SLA Assignment** | Derives SLA target from priority level |
| **First Response Generation** | Creates a ready-to-send first response |
| **Session History** | Lists and exports analyzed tickets as CSV |

---

## Setup and Run

### 1. Open the project folder

```bash
cd Ticket-Triaging-ERP
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your Groq API key

Go to [console.groq.com](https://console.groq.com) → API Keys → Create Key

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

### 5. Use the app

1. Paste your Groq API key in the **sidebar**
2. Type or paste any ERP support ticket in the input box
3. Click **"Analyze & Triage Ticket"**
4. See full triage results instantly

---

## Project Structure

```
Ticket-Triaging-ERP/
├── app.py               ← Streamlit UI (main entry point)
├── src/
│   ├── __init__.py
│   ├── triage_engine.py ← Groq API calls + JSON parsing
│   ├── prompts.py       ← System & user prompt templates (iterate here)
│   └── models.py        ← Data models / typed structures
├── requirements.txt
└── README.md
```

---

## How It Works

```
User Ticket (natural language)
        ↓
System Prompt (ERP domain knowledge + priority rules)
        ↓
LLaMA 3.3 70B (Groq API)
        ↓
Structured JSON Response
        ↓
Validated + Enriched (team routing, SLA)
        ↓
Rendered in Streamlit UI
```

### Prompt Strategy
- **Separation of concerns**: Prompts are defined in `src/prompts.py`, isolated from UI logic
- **Structured output**: The model is instructed to return valid JSON only
- **Domain knowledge injection**: System prompt encodes ERP taxonomy, ITIL issue types, and priority heuristics
- **Robust parsing**: Regex fallback handles cases where the model wraps output in markdown fences
- **Confidence scoring**: Model provides a confidence score shown in the UI

### Priority Heuristics
| Priority | Triggers |
|---|---|
| **High** | System down, payment runs blocked, month-end close at risk, audit/compliance deadline, C-level mentioned, $1M+ financial impact |
| **Medium** | Functionality degraded, 5-20 users affected, scheduled deadline in 1-2 weeks, data inconsistency |
| **Low** | Info/how-to requests, single user, no deadline, documentation, cosmetic issues |

---

## API Key Security

- The API key is entered at runtime via Streamlit's password input — it is **never stored to disk**
- For production: use environment variables (for example, `GROQ_API_KEY`) via `python-dotenv`

---

## Sample Tickets (Built-In)

5 sample tickets are included covering:
- Finance – Critical (GL account error blocking payment run)
- Inventory – Medium (stock discrepancy before audit)
- Procurement – High (POs stuck, blocking supply chain)
- HR – Low (documentation request for payroll config)
- SAP – Change Request (new cost centers for acquisition)

---

## Tech Stack

| Component | Technology |
|---|---|
| **UI Framework** | Streamlit |
| **AI/LLM** | Groq + LLaMA 3.3 70B |
| **Language** | Python 3.9+ |
| **Styling** | Custom CSS injected via Streamlit |

---


