# Ticket-Triaging-ERP# 🎫 AI-Powered ERP Ticket Triage System

An intelligent triage system that automatically classifies, prioritizes, and generates first responses for ERP support tickets using **Claude AI** (Anthropic).

---

## 🚀 Features

| Feature | Description |
|---|---|
| **Auto-Classification** | Categorizes tickets into Finance, Inventory, Procurement, HR, General |
| **ERP Module Detection** | Identifies Oracle Fusion, SAP, Microsoft Dynamics, or Generic ERP |
| **Issue Type Recognition** | Issue / Change Request / Support Request / Information Request |
| **Priority Scoring** | High / Medium / Low with business reasoning |
| **Confidence Score** | How certain the AI is about its classification |
| **Team Routing** | Suggests the right team to handle the ticket |
| **SLA Assignment** | Derives SLA target from priority level |
| **First Response Generation** | Professional, empathetic auto-reply ready to send |
| **Session History** | Browses and exports all analyzed tickets as CSV |

---

## 🛠 Setup & Run

### 1. Clone / Download the project

```bash
cd ticket_triage
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Get your Anthropic API key

Go to [console.anthropic.com](https://console.anthropic.com) → API Keys → Create Key

### 4. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

### 5. Use the app

1. Paste your Anthropic API key in the **sidebar**
2. Type or paste any ERP support ticket in the input box
3. Click **"⚡ Analyze & Triage Ticket"**
4. See full triage results instantly

---

## 📁 Project Structure

```
ticket_triage/
├── app.py               ← Streamlit UI (main entry point)
├── src/
│   ├── __init__.py
│   ├── triage_engine.py ← Core LLM logic, Anthropic API, JSON parsing
│   ├── prompts.py       ← System & user prompt templates (iterate here)
│   └── models.py        ← Data models / typed structures
├── requirements.txt
└── README.md
```

---

## 🧠 How It Works

```
User Ticket (natural language)
        ↓
System Prompt (ERP domain knowledge + priority rules)
        ↓
Claude Sonnet (Anthropic API)
        ↓
Structured JSON Response
        ↓
Validated + Enriched (team routing, SLA)
        ↓
Rendered in Streamlit UI
```

### Prompt Engineering Strategy
- **Separation of concerns**: Prompts are in `src/prompts.py`, isolated from UI logic
- **Structured output**: Claude is instructed to return only valid JSON — no markdown, no preamble
- **Domain knowledge injection**: System prompt encodes ERP taxonomy, ITIL issue types, priority heuristics
- **Robust parsing**: Regex fallback handles edge cases where model wraps response in markdown fences
- **Confidence scoring**: Model self-rates certainty, displayed as a progress bar

### Priority Heuristics
| Priority | Triggers |
|---|---|
| **High** | System down, payment runs blocked, month-end close at risk, audit/compliance deadline, C-level mentioned, $1M+ financial impact |
| **Medium** | Functionality degraded, 5-20 users affected, scheduled deadline in 1-2 weeks, data inconsistency |
| **Low** | Info/how-to requests, single user, no deadline, documentation, cosmetic issues |

---

## 🔒 API Key Security

- The API key is entered at runtime via Streamlit's password input — it is **never stored to disk**
- For production: use environment variables (`ANTHROPIC_API_KEY`) via `python-dotenv`

---

## 📊 Sample Tickets (built-in)

5 sample tickets are included covering:
- Finance – Critical (GL account error blocking payment run)
- Inventory – Medium (stock discrepancy before audit)
- Procurement – High (POs stuck, blocking supply chain)
- HR – Low (documentation request for payroll config)
- SAP – Change Request (new cost centers for acquisition)

---

## 🏗 Tech Stack

| Component | Technology |
|---|---|
| **UI Framework** | Streamlit |
| **AI/LLM** | Anthropic Claude (claude-sonnet) |
| **Language** | Python 3.9+ |
| **Data** | Pandas (export to CSV) |
| **Styling** | Custom CSS injected via Streamlit |

---

*Built for AI/ML & GenAI internship assessment — demonstrating LLM-powered business process automation.*
