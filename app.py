"""
AI-Powered ERP Ticket Triaging System  —  Streamlit + Groq (free tier)
"""
import streamlit as st
import pandas as pd
from datetime import datetime
from src.triage_engine import TriageEngine

st.set_page_config(page_title="ERP Ticket Triage AI", page_icon="T", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600&family=Manrope:wght@400;600;700&display=swap');
:root{
  --bg:#f6f5f2;
  --panel:#ffffff;
  --panel-2:#f3f1ed;
  --ink:#1f2937;
  --muted:#6b7280;
  --brand:#0f766e;
  --brand-2:#0891b2;
  --border:#e7e2da;
  --shadow:0 10px 30px rgba(17,24,39,0.08);
}
html,body,[class*="css"]{font-family:'Manrope',sans-serif;}
.stApp{background:radial-gradient(1200px 600px at 10% -10%,#e9f5f3 0%,transparent 60%),radial-gradient(1200px 600px at 90% -20%,#eaf3fb 0%,transparent 60%),var(--bg)!important;}
.hero{background:linear-gradient(135deg,#ffffff,#f7fbfb);border:1px solid var(--border);border-radius:16px;padding:26px 34px;margin-bottom:24px;position:relative;overflow:hidden;box-shadow:var(--shadow);}
.hero::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,transparent,var(--brand),var(--brand-2),transparent);}
.htitle{font-size:26px;font-weight:700;color:var(--ink);margin:0;}
.hsub{font-size:13px;color:var(--muted);margin:6px 0 0 0;}
.hbadge{background:#e6fffb;border:1px solid #b2f5ea;border-radius:20px;padding:4px 14px;font-size:11px;color:var(--brand);font-weight:700;letter-spacing:1px;text-transform:uppercase;}
.rs{background:var(--panel);border:1px solid var(--border);border-radius:12px;padding:18px 22px;margin-bottom:14px;box-shadow:var(--shadow);animation:fsi .3s ease-out;}
@keyframes fsi{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:translateY(0)}}
.rst{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:2px;font-weight:600;margin-bottom:10px;font-family:'IBM Plex Mono',monospace;}
.bh{background:#fee2e2;color:#b91c1c;border:1px solid #fecaca;padding:4px 12px;border-radius:6px;font-size:12px;font-weight:700;}
.bm{background:#ffedd5;color:#c2410c;border:1px solid #fed7aa;padding:4px 12px;border-radius:6px;font-size:12px;font-weight:700;}
.bl{background:#dcfce7;color:#15803d;border:1px solid #bbf7d0;padding:4px 12px;border-radius:6px;font-size:12px;font-weight:700;}
.bi{background:#ecfeff;color:#0e7490;border:1px solid #a5f3fc;padding:4px 12px;border-radius:6px;font-size:12px;font-weight:600;}
.rb{background:var(--panel-2);border:1px solid var(--border);border-left:3px solid var(--brand);border-radius:8px;padding:16px 18px;font-size:14px;color:var(--ink);line-height:1.75;font-style:italic;}
.dp{display:inline-block;background:var(--panel-2);border:1px solid var(--border);border-radius:8px;padding:5px 12px;font-size:12px;color:var(--ink);margin:3px 3px 3px 0;}
section[data-testid="stSidebar"]{background:var(--panel)!important;border-right:1px solid var(--border);}
.stTabs [data-baseweb="tab-list"]{gap:8px;background:transparent;border-bottom:1px solid var(--border);}
.stTabs [data-baseweb="tab"]{background:transparent;border:none;color:var(--muted);font-size:12px;letter-spacing:1px;text-transform:uppercase;font-weight:600;padding:10px 20px;}
.stTabs [aria-selected="true"]{color:var(--brand)!important;border-bottom:2px solid var(--brand)!important;}
.stButton>button{background:linear-gradient(135deg,#ccfbf1,#e0f2fe)!important;border:1px solid #bae6fd!important;color:var(--brand)!important;font-weight:700!important;letter-spacing:1px!important;text-transform:uppercase!important;font-size:12px!important;border-radius:10px!important;width:100%!important;}
textarea{background:#ffffff!important;border-color:var(--border)!important;color:var(--ink)!important;}
h1,h2,h3,h4{color:var(--ink)!important;}
p,li{color:var(--ink)!important;}
hr{border-color:var(--border)!important;}
</style>
""", unsafe_allow_html=True)

# ── Session state init (MUST happen before any widget) ──────────────────────
if "history"      not in st.session_state: st.session_state.history      = []
if "api_key"      not in st.session_state: st.session_state.api_key      = ""
if "last_result"  not in st.session_state: st.session_state.last_result  = None
if "ticket_text"  not in st.session_state: st.session_state.ticket_text  = ""

# ── Result renderer ──────────────────────────────────────────────────────────
def show_result(r: dict):
    priority   = r.get("priority",   "Medium")
    category   = r.get("category",   "General")
    erp_module = r.get("erp_module", "Generic ERP")
    issue_type = r.get("issue_type", "Issue")
    summary    = r.get("summary",    "")
    details    = r.get("key_details", [])
    resp       = r.get("first_response", "")
    reason     = r.get("priority_reasoning", "")
    conf       = float(r.get("confidence", 0.85))
    team       = r.get("suggested_team", "Support")

    pbadge = {"High":"bh","Medium":"bm","Low":"bl"}.get(priority,"bi")
    sla    = {"High":"4 hours","Medium":"24 hours","Low":"72 hours"}.get(priority,"24 hours")
    cpct   = int(conf * 100)
    ccol   = "#00d4ff" if cpct >= 80 else "#ffa94d" if cpct >= 60 else "#ff6b6b"

    st.markdown(f"""
    <div class="rs">
      <div class="rst">Classification</div>
      <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;">
        <span class="{pbadge}">{priority} Priority</span>
        <span class="bi">Category: {category}</span>
        <span class="bi">Issue Type: {issue_type}</span>
        <span class="bi">ERP Module: {erp_module}</span>
      </div>
    </div>
    <div class="rs">
      <div class="rst">Summary</div>
      <p style="color:#e6edf3;font-size:14px;line-height:1.65;margin:0;">{summary}</p>
    </div>
    <div class="rs">
      <div class="rst">Priority Reasoning</div>
      <p style="color:#c9d1d9;font-size:13px;line-height:1.6;margin:0 0 14px 0;">{reason}</p>
      <div class="rst">AI Confidence</div>
      <div style="display:flex;align-items:center;gap:12px;">
        <div style="flex:1;background:#21262d;border-radius:4px;height:6px;overflow:hidden;">
          <div style="width:{cpct}%;height:100%;background:{ccol};border-radius:4px;"></div>
        </div>
        <span style="color:{ccol};font-family:'IBM Plex Mono',monospace;font-size:13px;font-weight:600;min-width:36px;">{cpct}%</span>
      </div>
    </div>""", unsafe_allow_html=True)

    if details:
        pills = "".join(f'<span class="dp">• {d}</span>' for d in details)
        st.markdown(f'<div class="rs"><div class="rst">Key Details Extracted</div><div style="margin-top:4px;">{pills}</div></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="rs">
      <div style="display:flex;gap:48px;flex-wrap:wrap;">
        <div><div class="rst">Assigned Team</div><span style="color:#f0f6fc;font-size:14px;font-weight:600;">{team}</span></div>
        <div><div class="rst">SLA Target</div><span style="color:#f0f6fc;font-size:14px;font-weight:600;">{sla}</span></div>
      </div>
    </div>
    <div class="rs">
      <div class="rst">Auto-Generated First Response</div>
      <div class="rb">{resp}</div>
    </div>""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
SAMPLES = {
  "Finance - Critical":    "Our accounts payable team cannot process vendor invoices since yesterday. The system throws GL account not found on every posting attempt. This is blocking our entire payment run for 200 plus vendors. Month-end close is in 2 days and we are at risk of late payment penalties.",
  "Inventory - Medium":    "Stock levels in the warehouse management module do not match our physical count. After yesterday's cycle count we found discrepancies in 150 plus SKUs. We need this reconciled before our external audit next week.",
  "Procurement - High":    "Purchase orders created in the system are not syncing with the finance module for budget validation. Around 45 POs worth 2 million dollars are stuck in pending approval for 3 days. This is halting our supply chain operations completely.",
  "HR - Low":              "Can you provide documentation on how to configure payroll processing for contract employees? We have a new batch of contractors joining next month and want to set things up correctly.",
  "SAP - Change Request": "We need to add three new cost centers for our recently acquired subsidiary and map them to the existing GL structure in SAP. Please guide us through the configuration steps or assign a consultant.",
}

with st.sidebar:
    st.markdown("### API Configuration")
    st.markdown('<p style="font-size:12px;color:#8b949e;">Free key at <a href="https://console.groq.com" style="color:#00d4ff;">console.groq.com</a></p>', unsafe_allow_html=True)

    new_key = st.text_input("Groq API Key", type="password", value=st.session_state.api_key, placeholder="gsk_...", key="api_key_input")
    if new_key != st.session_state.api_key:
        st.session_state.api_key = new_key

    st.markdown("---")
    st.markdown("### Sample Tickets")
    st.caption("Click any to load it")
    for label, text in SAMPLES.items():
        if st.button(label, key=f"s_{label}"):
            st.session_state.ticket_text = text
            st.rerun()

    st.markdown("---")
    st.markdown("### Session Stats")
    total = len(st.session_state.history)
    highp = sum(1 for h in st.session_state.history if h["result"].get("priority") == "High")
    ca, cb = st.columns(2)
    ca.metric("Tickets", total)
    cb.metric("High Priority", highp)
    if total:
        cats = {}
        for h in st.session_state.history:
            c = h["result"].get("category", "Other")
            cats[c] = cats.get(c, 0) + 1
        st.markdown("**Categories:**")
        for cat, cnt in cats.items():
            st.markdown(f'<span class="bi">{cat}</span>&nbsp;`{cnt}`', unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px;">
    <div>
      <h1 class="htitle">ERP Ticket Triage AI</h1>
      <p class="hsub">AI-powered classification · prioritization · routing · auto-response</p>
    </div>
    <span class="hbadge">Groq + LLaMA 3.3 70B</span>
  </div>
</div>""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["Analyze Ticket", "History", "How It Works"])

# ══ Tab 1 ════════════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown("#### Submit a Support Ticket")
        st.caption("Paste any unstructured ticket — plain natural language works perfectly")

        # KEY FIX: use st.session_state value as default, no key= collision
        ticket = st.text_area(
            "Ticket Description",
            value=st.session_state.ticket_text,
            height=230,
            placeholder=(
                "Describe the ERP issue in plain language...\n\n"
                "Example: Our finance team can't close the monthly books because the GL "
                "reconciliation report keeps timing out since the last system update 3 days ago. "
                "The CFO is waiting urgently."
            ),
            label_visibility="collapsed",
        )

        words = len(ticket.split()) if ticket.strip() else 0
        st.markdown(f'<p style="font-size:11px;color:#4a5568;text-align:right;margin-top:-8px;">{words} words · {len(ticket)} chars</p>', unsafe_allow_html=True)

        can_go  = bool(st.session_state.api_key) and bool(ticket.strip())
        clicked = st.button("Analyze & Triage Ticket", disabled=not can_go)

        if not st.session_state.api_key:
          st.info("Enter your **Groq API key** in the sidebar (it's free — get it at console.groq.com)")

        with st.expander("Tips for best results"):
            st.markdown("""
- **State business impact** — who is affected, how many users
- **Mention deadlines** — audit, month-end close, payment runs
- **Include error messages** — paste exact error text if available
- **Describe duration** — since when the problem started
- **Plain language is fine** — no formatting needed at all
            """)

    with right:
        st.markdown("#### Triage Result")
        st.caption("AI analysis appears here after submission")

        if clicked and ticket.strip():
            st.session_state.ticket_text = ticket          # save before rerun
            with st.spinner("Analyzing with LLaMA 3.3 70B via Groq..."):
                engine = TriageEngine(api_key=st.session_state.api_key)
                result, err = engine.analyze(ticket)

            if err:
                st.error(f"{err}")
            else:
                st.session_state.history.insert(0, {
                    "ticket":    ticket,
                    "result":    result,
                    "timestamp": datetime.now().strftime("%H:%M:%S · %d %b %Y"),
                })
                st.session_state.last_result = result
                st.rerun()

        if st.session_state.last_result:
            show_result(st.session_state.last_result)
        else:
            st.markdown("""
            <div style="text-align:center;padding:60px 20px;border:1px dashed #21262d;border-radius:10px;margin-top:8px;">
              <div style="font-size:14px;">AI</div>
              <p style="color:#4a5568;font-size:14px;margin-top:12px;">Submit a ticket to see AI triage results</p>
            </div>""", unsafe_allow_html=True)

# ══ Tab 2 ════════════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.history:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;">
          <div style="font-size:14px;">No history</div>
          <p style="font-size:16px;margin-top:14px;color:#8b949e;">No tickets analyzed yet</p>
        </div>""", unsafe_allow_html=True)
    else:
        rows = [{"Timestamp":h["timestamp"],"Category":h["result"].get("category"),"ERP Module":h["result"].get("erp_module"),
                 "Issue Type":h["result"].get("issue_type"),"Priority":h["result"].get("priority"),
                 "Confidence":f'{int(float(h["result"].get("confidence",0.85))*100)}%',"Summary":h["result"].get("summary","")}
                for h in st.session_state.history]
        csv = pd.DataFrame(rows).to_csv(index=False)
        ca, cb, cc = st.columns([3, 1, 1])
        ca.caption(f"{len(st.session_state.history)} ticket(s) triaged this session")
        with cb:
          st.download_button("Export CSV", csv, "triage_history.csv", "text/csv")
        with cc:
          if st.button("Clear All"):
                st.session_state.history     = []
                st.session_state.last_result = None
                st.rerun()
        st.markdown("---")
        for entry in st.session_state.history:
            r    = entry["result"]
            with st.expander(f'[{r.get("category")}]  {r.get("summary","")[:65]}...  —  {entry["timestamp"]}'):
                show_result(r)
                st.markdown("**Original Ticket:**")
                st.markdown(f'<div style="background:#0d1117;border:1px solid #21262d;border-radius:6px;padding:14px;font-size:13px;color:#c9d1d9;line-height:1.65;">{entry["ticket"]}</div>', unsafe_allow_html=True)

# ══ Tab 3 ════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="rs">
      <div class="rst">What This System Does</div>
      <p style="font-size:14px;line-height:1.85;color:#c9d1d9;">
        An <strong style="color:#00d4ff;">AI-powered ERP ticket triage system</strong> using 
        <strong>LLaMA 3.3 70B</strong> via <strong>Groq</strong> (free tier, very fast inference).
        Analyzes unstructured tickets and returns structured triage data — category, priority, module, 
        team routing, and a ready-to-send first response — all in under 2 seconds.
      </p>
    </div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="rs">
          <div class="rst">Processing Pipeline</div>
          <ol style="color:#c9d1d9;font-size:13px;line-height:2.1;padding-left:20px;margin:0;">
            <li>Raw ticket submitted (unstructured NL)</li>
            <li>Domain-aware system prompt injected</li>
            <li>LLaMA 3.3 70B via Groq API called</li>
            <li>Category + ERP module identified</li>
            <li>Issue type classified (ITIL framework)</li>
            <li>Priority scored with business reasoning</li>
            <li>Confidence score assigned by model</li>
            <li>Team routing derived from category</li>
            <li>First-level response auto-generated</li>
            <li>JSON validated and rendered in UI</li>
          </ol>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="rs">
          <div class="rst">Output Fields</div>
          <ul style="color:#c9d1d9;font-size:13px;line-height:2.1;padding-left:20px;margin:0;">
            <li><strong>Category</strong> — Finance / Inventory / Procurement / HR</li>
            <li><strong>ERP Module</strong> — Oracle Fusion / SAP / MS Dynamics</li>
            <li><strong>Issue Type</strong> — Issue / Change / Support / Info Request</li>
            <li><strong>Priority</strong> — High / Medium / Low + reasoning</li>
            <li><strong>Confidence</strong> — Model certainty (0–100%)</li>
            <li><strong>Key Details</strong> — Auto-extracted facts from ticket</li>
            <li><strong>Team Routing</strong> — Suggested assignment</li>
            <li><strong>SLA</strong> — Derived from priority level</li>
            <li><strong>First Response</strong> — Auto-generated professional reply</li>
          </ul>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class="rs">
      <div class="rst">Prompt Engineering</div>
      <p style="color:#c9d1d9;font-size:13px;line-height:1.85;">
        <strong>System + user prompt</strong> architecture. System prompt encodes ERP domain knowledge, ITIL taxonomy,
        priority heuristics (financial impact, deadlines, user scale, audit risk), and team routing rules.
        Model returns <strong>only valid JSON</strong> — enabling reliable programmatic parsing.
        Regex fallback handles edge cases. Prompts live in <code style="color:#00d4ff;">src/prompts.py</code> 
        — easy to iterate without touching UI logic.
      </p>
    </div>
    <div class="rs">
      <div class="rst">Project Structure</div>
      <pre style="color:#c9d1d9;font-family:'IBM Plex Mono',monospace;font-size:12px;line-height:1.9;margin:0;background:transparent;border:none;">
ticket_triage/
├── app.py               ← Streamlit UI (entry point)
├── src/
│   ├── __init__.py
│   ├── triage_engine.py ← Groq API calls + JSON parsing
│   ├── prompts.py       ← System & user prompt templates
│   └── models.py        ← Data models
├── requirements.txt
└── README.md
      </pre>
    </div>""", unsafe_allow_html=True)
