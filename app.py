import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet, delete_row, clear_sheet_by_month

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="Biverway | Finance OS", layout="wide")

# ====================== GLOBAL STYLES ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

/* ── ROOT TOKENS ── */
:root {
    --bg:        #0b0c10;
    --bg2:       #13151c;
    --bg3:       #1a1d27;
    --amber:     #f5a623;
    --amber-dim: #c4841a;
    --ice:       #dce9f0;
    --ice-bg:    rgba(220,233,240,0.07);
    --green:     #2ecc71;
    --red:       #e74c3c;
    --yellow:    #f0c040;
    --muted:     rgba(255,255,255,0.35);
    --border:    rgba(255,255,255,0.07);
    --radius:    14px;
    --font-head: 'Barlow Condensed', sans-serif;
    --font-mono: 'DM Mono', monospace;
    --font-body: 'DM Sans', sans-serif;
}

/* ── BASE ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg) !important;
    color: #e8eaf0 !important;
    font-family: var(--font-body) !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stSidebarContent"] {
    background: var(--bg) !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    max-width: 860px !important;
    margin: 0 auto !important;
}
.block-container { padding: 0 1.2rem 3rem !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--amber-dim); border-radius: 4px; }

/* ── AMBER HERO BANNER ── */
.bw-hero {
    background: var(--amber);
    border-radius: var(--radius);
    padding: 22px 28px 18px;
    margin: 24px 0 28px;
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.bw-hero h1 {
    font-family: var(--font-head) !important;
    font-size: 2.2rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.04em !important;
    color: #0b0c10 !important;
    margin: 0 !important;
    line-height: 1 !important;
    text-transform: uppercase;
}
.bw-hero p {
    font-family: var(--font-body) !important;
    font-size: 0.78rem !important;
    color: rgba(0,0,0,0.55) !important;
    margin: 0 !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 500;
}

/* ── SECTION HEADER (ice-blue pill) ── */
.bw-section {
    background: var(--ice-bg);
    border: 1px solid rgba(220,233,240,0.13);
    border-radius: var(--radius);
    padding: 13px 20px;
    margin: 24px 0 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.bw-section span {
    font-family: var(--font-head) !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.08em !important;
    color: var(--ice) !important;
    text-transform: uppercase;
}
.bw-section .bw-icon { font-size: 1.1rem; }

/* ── MONTH BADGE ── */
.bw-month-badge {
    display: inline-block;
    background: rgba(245,166,35,0.12);
    border: 1px solid rgba(245,166,35,0.3);
    color: var(--amber);
    font-family: var(--font-mono);
    font-size: 0.8rem;
    letter-spacing: 0.1em;
    padding: 5px 14px;
    border-radius: 100px;
    margin-bottom: 18px;
}

/* ── CARD ── */
.bw-card {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 22px 22px 18px;
    margin-bottom: 14px;
}

/* ── RESULTS TABLE ── */
.bw-results-table {
    width: 100%;
    border-collapse: collapse;
    font-family: var(--font-body);
    font-size: 0.9rem;
    margin-top: 6px;
}
.bw-results-table tr {
    border-bottom: 1px solid var(--border);
}
.bw-results-table tr:last-child { border-bottom: none; }
.bw-results-table td {
    padding: 12px 16px;
    color: #c8ccd8;
}
.bw-results-table td:first-child {
    color: var(--muted);
    font-size: 0.78rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    width: 50%;
}
.bw-results-table td:last-child {
    font-family: var(--font-mono);
    font-size: 1rem;
    color: #e8eaf0;
    font-weight: 500;
    text-align: right;
}
.bw-results-table tr:nth-child(odd) td { background: rgba(255,255,255,0.02); }

/* ── METRIC GRID ── */
.bw-metric-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
    margin: 14px 0;
}
.bw-metric {
    background: var(--bg3);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px 12px;
}
.bw-metric .label {
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    font-family: var(--font-mono);
    margin-bottom: 6px;
}
.bw-metric .value {
    font-family: var(--font-mono);
    font-size: 1.05rem;
    font-weight: 500;
    color: #e8eaf0;
    line-height: 1;
}

/* ── STATUS PILL ── */
.bw-pill {
    display: inline-block;
    padding: 5px 13px;
    border-radius: 100px;
    font-size: 0.75rem;
    font-family: var(--font-mono);
    letter-spacing: 0.06em;
    font-weight: 500;
    margin-top: 10px;
}
.bw-pill.green  { background: rgba(46,204,113,0.12); color: var(--green); border: 1px solid rgba(46,204,113,0.25); }
.bw-pill.yellow { background: rgba(240,192,64,0.12); color: var(--yellow); border: 1px solid rgba(240,192,64,0.25); }
.bw-pill.red    { background: rgba(231,76,60,0.12); color: var(--red); border: 1px solid rgba(231,76,60,0.25); }

/* ── FOOTER ── */
.bw-footer {
    text-align: center;
    font-size: 0.72rem;
    color: var(--muted);
    font-family: var(--font-mono);
    letter-spacing: 0.1em;
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid var(--border);
}

/* ── STREAMLIT WIDGET OVERRIDES ── */

/* Labels */
[data-testid="stWidgetLabel"] p,
label, .stSelectbox label, .stNumberInput label,
[data-baseweb="form-control-label"] {
    font-family: var(--font-mono) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}

/* Inputs */
input, textarea,
[data-baseweb="input"] input,
[data-baseweb="textarea"] textarea {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: var(--font-mono) !important;
    font-size: 1rem !important;
}
input:focus, textarea:focus {
    border-color: rgba(245,166,35,0.5) !important;
    box-shadow: 0 0 0 2px rgba(245,166,35,0.08) !important;
}

/* Select */
[data-baseweb="select"] > div {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #e8eaf0 !important;
    font-family: var(--font-mono) !important;
}
[data-baseweb="popover"] [role="listbox"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
}
[role="option"] {
    background: transparent !important;
    color: #e8eaf0 !important;
    font-family: var(--font-mono) !important;
    font-size: 0.88rem !important;
}
[role="option"]:hover, [aria-selected="true"] {
    background: rgba(245,166,35,0.1) !important;
    color: var(--amber) !important;
}

/* Primary button → amber */
[data-testid="baseButton-primary"],
button[kind="primary"] {
    background: var(--amber) !important;
    color: #0b0c10 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: var(--font-head) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    padding: 10px 28px !important;
    transition: background 0.2s, transform 0.1s !important;
}
[data-testid="baseButton-primary"]:hover { background: var(--amber-dim) !important; transform: translateY(-1px); }

/* Secondary / form submit */
[data-testid="baseButton-secondary"],
button[kind="secondary"] {
    background: var(--bg3) !important;
    color: #e8eaf0 !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    font-family: var(--font-head) !important;
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    transition: border-color 0.2s, color 0.2s !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: var(--amber) !important;
    color: var(--amber) !important;
}

/* Form submit button specifically */
[data-testid="stFormSubmitButton"] button {
    background: var(--amber) !important;
    color: #0b0c10 !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: var(--font-head) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    width: 100% !important;
    padding: 12px !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: var(--amber-dim) !important;
    transform: translateY(-1px);
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg2) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
}
[data-testid="stExpanderToggleIcon"] { color: var(--amber) !important; }
[data-testid="stExpander"] summary {
    font-family: var(--font-head) !important;
    font-size: 0.95rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: var(--ice) !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    background: var(--bg2) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg3) !important;
    color: var(--muted) !important;
    font-size: 0.68rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] td {
    color: #c8ccd8 !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
}

/* Alert / info / success / warning / error boxes */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
}
[data-testid="stNotificationContentInfo"]    { background: rgba(220,233,240,0.06) !important; border-left-color: var(--ice) !important; }
[data-testid="stNotificationContentSuccess"] { background: rgba(46,204,113,0.06) !important; border-left-color: var(--green) !important; }
[data-testid="stNotificationContentWarning"] { background: rgba(240,192,64,0.06) !important; border-left-color: var(--yellow) !important; }
[data-testid="stNotificationContentError"]   { background: rgba(231,76,60,0.06) !important; border-left-color: var(--red) !important; }

/* Date input */
[data-testid="stDateInput"] input {
    font-family: var(--font-mono) !important;
}

/* Divider */
hr { border-color: var(--border) !important; margin: 24px 0 !important; }

/* Hide streamlit branding */
#MainMenu, footer, [data-testid="stStatusWidget"] { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "income_form_key" not in st.session_state:
    st.session_state.income_form_key = 0
if "expense_form_key" not in st.session_state:
    st.session_state.expense_form_key = 0

# ====================== HERO BANNER ======================
st.markdown("""
<div class="bw-hero">
    <h1>Biverway Finance OS</h1>
    <p>Performance-Driven Financial Control</p>
</div>
""", unsafe_allow_html=True)

# ====================== MONTH SELECTOR ======================
st.markdown('<div class="bw-section"><span class="bw-icon">📅</span><span>Working Month</span></div>', unsafe_allow_html=True)
working_month = st.date_input("", value=datetime.today(), label_visibility="collapsed")
current_month = working_month.strftime("%b %Y")
st.markdown(f'<div class="bw-month-badge">● &nbsp;{current_month}</div>', unsafe_allow_html=True)

# ====================== HEADERS ======================
income_headers  = ["month_year", "income_source", "income_type", "amount", "notes"]
expense_headers = ["month_year", "category", "amount", "description"]

# ====================== LOAD DATA ======================
income_records  = load_sheet("Income",  income_headers)
expense_records = load_sheet("Expense", expense_headers)

income_df  = pd.DataFrame(income_records)
expense_df = pd.DataFrame(expense_records)

for df, col in [(income_df, "month_year"), (expense_df, "month_year")]:
    if col not in df.columns:
        df[col] = ""

income_df_month  = income_df[income_df["month_year"]  == current_month].copy()
expense_df_month = expense_df[expense_df["month_year"] == current_month].copy()

if not income_df_month.empty:
    income_df_month["amount"] = pd.to_numeric(income_df_month["amount"], errors="coerce").fillna(0)
if not expense_df_month.empty:
    expense_df_month["amount"] = pd.to_numeric(expense_df_month["amount"], errors="coerce").fillna(0)

# ====================== INCOME TRACKER ======================
st.markdown('<div class="bw-section"><span class="bw-icon">💰</span><span>Income Tracker</span></div>', unsafe_allow_html=True)

income_type_map = {
    "Skill": "Active",
    "Salary": "Active",
    "Business": "Passive",
    "Dividend/Interest": "Passive",
    "Rental": "Passive"
}

with st.form(f"income_form_{st.session_state.income_form_key}"):
    col_a, col_b = st.columns(2)
    with col_a:
        income_source = st.selectbox("Income Source", list(income_type_map.keys()))
    with col_b:
        amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0, format="%0.0f")
    notes = st.text_area("Notes (optional)", height=80)
    submit_income = st.form_submit_button("＋  Add Income")

if submit_income:
    append_row("Income", [current_month, income_source, income_type_map[income_source], amount, notes])
    st.success("Income entry recorded.")
    st.session_state.income_form_key += 1
    st.rerun()

if not income_df_month.empty:
    st.markdown(f'<p style="font-family:var(--font-mono);font-size:0.72rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin:18px 0 8px;">Records — {current_month}</p>', unsafe_allow_html=True)
    display_income = income_df_month[["income_source", "income_type", "amount", "notes"]].reset_index(drop=True)
    display_income.columns = ["Source", "Type", "Amount (₦)", "Notes"]
    st.dataframe(display_income, use_container_width=True)

    col_del, col_clr = st.columns([3, 1])
    with col_clr:
        if st.button("🗑 Clear Month", key="clr_inc"):
            clear_sheet_by_month("Income", current_month)
            st.rerun()
    with col_del:
        del_income_label = st.selectbox(
            "Delete a row",
            options=[f"{i}: {row['income_source']} — ₦{row['amount']:,.0f}" for i, (_, row) in enumerate(income_df_month.iterrows())],
            key="del_inc_select"
        )
        if st.button("Delete Selected", key="del_inc_btn"):
            sel_idx = int(del_income_label.split(":")[0])
            actual_idx = income_df_month.index[sel_idx]
            delete_row("Income", actual_idx + 2)
            st.rerun()
else:
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.8rem;color:var(--muted);margin:12px 0;">No income entries for this month.</p>', unsafe_allow_html=True)

# ====================== EXPENSE TRACKER ======================
st.markdown('<div class="bw-section"><span class="bw-icon">💸</span><span>Expense Tracker</span></div>', unsafe_allow_html=True)

expense_categories = [
    "Rent", "Food", "Utilities", "Transport",
    "Healthcare", "Education", "Subscription", "Family Support"
]

with st.form(f"expense_form_{st.session_state.expense_form_key}"):
    col_c, col_d = st.columns(2)
    with col_c:
        category = st.selectbox("Category", expense_categories)
    with col_d:
        expense_amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0, format="%0.0f")
    description = st.text_area("Description (optional)", height=80)
    submit_expense = st.form_submit_button("＋  Add Expense")

if submit_expense:
    append_row("Expense", [current_month, category, expense_amount, description])
    st.success("Expense entry recorded.")
    st.session_state.expense_form_key += 1
    st.rerun()

if not expense_df_month.empty:
    total_expense = expense_df_month["amount"].sum()
    if total_expense > 0:
        expense_df_month["% of Total"] = (
            expense_df_month["amount"] / total_expense * 100
        ).round(0).astype(int).astype(str) + "%"
    else:
        expense_df_month["% of Total"] = "0%"

    st.markdown(f'<p style="font-family:var(--font-mono);font-size:0.72rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin:18px 0 8px;">Records — {current_month}</p>', unsafe_allow_html=True)
    display_expense = expense_df_month[["category", "amount", "% of Total", "description"]].reset_index(drop=True)
    display_expense.columns = ["Category", "Amount (₦)", "% of Total", "Description"]
    st.dataframe(display_expense, use_container_width=True)

    col_del2, col_clr2 = st.columns([3, 1])
    with col_clr2:
        if st.button("🗑 Clear Month", key="clr_exp"):
            clear_sheet_by_month("Expense", current_month)
            st.rerun()
    with col_del2:
        del_expense_label = st.selectbox(
            "Delete a row",
            options=[f"{i}: {row['category']} — ₦{row['amount']:,.0f}" for i, (_, row) in enumerate(expense_df_month.iterrows())],
            key="del_exp_select"
        )
        if st.button("Delete Selected", key="del_exp_btn"):
            sel_idx = int(del_expense_label.split(":")[0])
            actual_idx = expense_df_month.index[sel_idx]
            delete_row("Expense", actual_idx + 2)
            st.rerun()
else:
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.8rem;color:var(--muted);margin:12px 0;">No expense entries for this month.</p>', unsafe_allow_html=True)

# ====================== FINANCIAL PERFORMANCE ======================
st.markdown('<div class="bw-section"><span class="bw-icon">📊</span><span>Financial Performance</span></div>', unsafe_allow_html=True)

total_income  = income_df_month["amount"].sum()  if not income_df_month.empty  else 0
total_expense = expense_df_month["amount"].sum() if not expense_df_month.empty else 0
net_surplus   = total_income - total_expense
savings_rate  = (net_surplus / total_income * 100) if total_income else 0

with st.expander("VIEW PERFORMANCE DETAILS"):

    # Metric grid
    st.markdown(f"""
    <div class="bw-metric-grid">
        <div class="bw-metric">
            <div class="label">Total Income</div>
            <div class="value">₦{total_income:,.0f}</div>
        </div>
        <div class="bw-metric">
            <div class="label">Total Expenses</div>
            <div class="value">₦{total_expense:,.0f}</div>
        </div>
        <div class="bw-metric">
            <div class="label">Net Surplus</div>
            <div class="value" style="color:{'#2ecc71' if net_surplus >= 0 else '#e74c3c'}">₦{net_surplus:,.0f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Savings insight
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.72rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin:20px 0 6px;">Savings Insight</p>', unsafe_allow_html=True)

    if total_income == 0:
        st.error("No income recorded — financial performance cannot be evaluated.")
    else:
        if savings_rate >= 30:
            pill_cls, pill_txt = "green",  f"▲ {savings_rate:.1f}% savings rate — strong position"
        elif 15 <= savings_rate < 30:
            pill_cls, pill_txt = "yellow", f"◆ {savings_rate:.1f}% savings rate — stable, optimize further"
        elif 1 <= savings_rate < 15:
            pill_cls, pill_txt = "yellow", f"▼ {savings_rate:.1f}% savings rate — margin too thin"
        else:
            pill_cls, pill_txt = "red",    f"✕ {savings_rate:.1f}% — deficit, expenses exceed income"
        st.markdown(f'<span class="bw-pill {pill_cls}">{pill_txt}</span>', unsafe_allow_html=True)

    # Income insight
    if not income_df_month.empty:
        active_income  = income_df_month[income_df_month["income_type"] == "Active"]["amount"].sum()
        passive_income = income_df_month[income_df_month["income_type"] == "Passive"]["amount"].sum()
        active_pct  = (active_income  / total_income * 100) if total_income else 0
        passive_pct = (passive_income / total_income * 100) if total_income else 0

        st.markdown('<p style="font-family:var(--font-mono);font-size:0.72rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin:20px 0 8px;">Income Structure</p>', unsafe_allow_html=True)
        st.markdown(f"""
        <table class="bw-results-table">
            <tr><td>Active Income</td><td>₦{active_income:,.0f} &nbsp;<span style="color:var(--muted);font-size:0.78rem">({active_pct:.0f}%)</span></td></tr>
            <tr><td>Passive Income</td><td>₦{passive_income:,.0f} &nbsp;<span style="color:var(--muted);font-size:0.78rem">({passive_pct:.0f}%)</span></td></tr>
        </table>
        """, unsafe_allow_html=True)

        if active_pct >= 70:
            st.markdown('<span class="bw-pill yellow">Income heavily effort-dependent — grow passive streams</span>', unsafe_allow_html=True)
        elif passive_pct >= 50:
            st.markdown('<span class="bw-pill green">Healthy passive structure — income base is resilient</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="bw-pill yellow">Income structure moderately balanced</span>', unsafe_allow_html=True)

    # Expense insight
    if not expense_df_month.empty:
        sorted_exp = expense_df_month.sort_values("amount", ascending=False)
        top = sorted_exp.head(2)
        st.markdown('<p style="font-family:var(--font-mono);font-size:0.72rem;letter-spacing:0.1em;color:var(--muted);text-transform:uppercase;margin:20px 0 8px;">Top Cost Drivers</p>', unsafe_allow_html=True)
        rows_html = "".join(
            f'<tr><td>{row["category"]}</td><td>₦{row["amount"]:,.0f} &nbsp;<span style="color:var(--muted);font-size:0.78rem">({row["% of Total"]})</span></td></tr>'
            for _, row in top.iterrows()
        )
        st.markdown(f'<table class="bw-results-table">{rows_html}</table>', unsafe_allow_html=True)

# ====================== ALLOCATION LOG ======================
st.markdown('<div class="bw-section"><span class="bw-icon">📂</span><span>Allocation Log</span></div>', unsafe_allow_html=True)

with st.expander("VIEW / MANAGE ALLOCATION"):
    if total_income == 0:
        st.info("No income recorded — allocation cannot be calculated.")
    elif net_surplus <= 0:
        st.warning("No surplus available — allocation requires a positive net surplus.")
    else:
        allocation_modes = {
            "Default":                  {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 10, "Charity": 5},
            "Wealth Focus":             {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 5,  "Charity": 5},
            "Giving Focus":             {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 10, "Charity": 25},
            "Savings / Security Focus": {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5,  "Charity": 5},
        }

        mode = st.selectbox("Allocation Mode", list(allocation_modes.keys()))
        allocation_list = [
            {"Category": cat, "Percentage (%)": pct, "Allocated Amount (₦)": round(net_surplus * pct / 100, 0)}
            for cat, pct in allocation_modes[mode].items()
        ]

        # Render as styled table
        rows_alloc = "".join(
            f'<tr><td>{r["Category"]}</td><td>₦{r["Allocated Amount (₦)"]:,.0f} &nbsp;<span style="color:var(--muted);font-size:0.78rem">({r["Percentage (%)"]}%)</span></td></tr>'
            for r in allocation_list
        )
        st.markdown(f'<table class="bw-results-table" style="margin-bottom:16px">{rows_alloc}</table>', unsafe_allow_html=True)

        if st.button("💾  Save Allocation for Month"):
            clear_sheet_by_month("Allocation_Log", current_month)
            for row in allocation_list:
                append_row("Allocation_Log", [current_month, row["Category"], row["Percentage (%)"], row["Allocated Amount (₦)"]])
            st.success("Allocation saved to Google Sheet.")

# ====================== FOOTER ======================
st.markdown(f"""
<div class="bw-footer">
    DESIGNED ACCORDING TO BIVERWAY TRADING SYSTEM &nbsp;·&nbsp; FINANCE OS V3.0
</div>
""", unsafe_allow_html=True)
