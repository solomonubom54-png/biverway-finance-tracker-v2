import streamlit as st
import pandas as pd
from datetime import datetime
from core.supabase_db import (
    client,
    add_income, load_income, delete_income, clear_income_month,
    add_expense, load_expense, delete_expense, clear_expense_month,
    save_allocation
)

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="Biverway Finance OS", layout="wide")

# ====================== GLOBAL STYLES ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&family=Sora:ital,wght@1,300&display=swap');

/* ── TOKENS ── */
:root {
    --bg-base:    #080a0e;
    --bg-card:    #0d1017;
    --bg-elevated:#131720;
    --bg-input:   #0f1318;
    --gold:       #c9a84c;
    --gold-dim:   #9a7a34;
    --gold-glow:  rgba(201,168,76,0.08);
    --gold-line:  rgba(201,168,76,0.2);
    --cream:      #e8e0d0;
    --cream-dim:  rgba(232,224,208,0.55);
    --cream-mute: rgba(232,224,208,0.25);
    --white:      #f0ece4;
    --green:      #4caf7d;
    --green-bg:   rgba(76,175,125,0.08);
    --red:        #c0544a;
    --red-bg:     rgba(192,84,74,0.08);
    --amber-warn: #d4922a;
    --warn-bg:    rgba(212,146,42,0.08);
    --border:     rgba(255,255,255,0.05);
    --border-md:  rgba(255,255,255,0.08);
    --radius-sm:  8px;
    --radius:     12px;
    --radius-lg:  16px;
    --font-disp:  'Sora', sans-serif;
    --font-mono:  'IBM Plex Mono', monospace;
}

/* ── BASE ── */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
    background: var(--bg-base) !important;
    color: var(--cream) !important;
    font-family: var(--font-disp) !important;
}
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    background: var(--bg-base) !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    max-width: 820px !important;
    margin: 0 auto !important;
}
.block-container { padding: 0 1.4rem 4rem !important; }

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 3px; }

/* ── MASTHEAD ── */
.bw-masthead {
    padding: 36px 0 28px;
    border-bottom: 1px solid var(--gold-line);
    margin-bottom: 32px;
}
.bw-masthead-label {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--gold) !important;
    margin-bottom: 8px !important;
}
.bw-masthead h1 {
    font-family: var(--font-disp) !important;
    font-size: 1.9rem !important;
    font-weight: 600 !important;
    letter-spacing: -0.02em !important;
    color: var(--white) !important;
    margin: 0 0 4px 0 !important;
    line-height: 1.1 !important;
}
.bw-masthead-sub {
    font-size: 0.8rem !important;
    color: var(--cream-mute) !important;
    font-weight: 300 !important;
    letter-spacing: 0.02em !important;
}

/* ── SECTION LABEL ── */
.bw-section-label {
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.2em !important;
    text-transform: uppercase !important;
    color: var(--gold) !important;
    padding: 0 0 10px 0 !important;
    margin: 32px 0 16px 0 !important;
    border-bottom: 1px solid var(--gold-line) !important;
    display: block !important;
}

/* ── CARDS ── */
.bw-card {
    background: var(--bg-card);
    border: 1px solid var(--border-md);
    border-radius: var(--radius);
    padding: 24px;
    margin-bottom: 12px;
}
.bw-card-elevated {
    background: var(--bg-elevated);
    border: 1px solid var(--border-md);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 8px;
}

/* ── MONTH BADGE ── */
.bw-month {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--gold-glow);
    border: 1px solid var(--gold-line);
    color: var(--gold);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 100px;
    margin-bottom: 24px;
}

/* ── METRIC GRID ── */
.bw-kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border-md);
    border-radius: var(--radius);
    overflow: hidden;
    margin: 0 0 24px 0;
}
.bw-kpi {
    background: var(--bg-card);
    padding: 20px 18px 16px;
}
.bw-kpi .kpi-label {
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--cream-mute);
    margin-bottom: 10px;
    display: block;
}
.bw-kpi .kpi-value {
    font-family: var(--font-mono);
    font-size: 1.15rem;
    font-weight: 500;
    color: var(--white);
    line-height: 1;
    display: block;
}
.bw-kpi .kpi-value.positive { color: var(--green); }
.bw-kpi .kpi-value.negative { color: var(--red); }

/* ── STATUS BADGE ── */
.bw-status {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 8px 14px;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    margin-top: 4px;
}
.bw-status.green  { background: var(--green-bg); color: var(--green); border: 1px solid rgba(76,175,125,0.2); }
.bw-status.yellow { background: var(--warn-bg);  color: var(--amber-warn); border: 1px solid rgba(212,146,42,0.2); }
.bw-status.red    { background: var(--red-bg);   color: var(--red); border: 1px solid rgba(192,84,74,0.2); }
.bw-status::before { content: ''; width: 5px; height: 5px; border-radius: 50%; background: currentColor; display: inline-block; }

/* ── INSIGHT ROW ── */
.bw-insight-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
}
.bw-insight-row:last-child { border-bottom: none; }
.bw-insight-row .ir-label {
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--cream-mute);
}
.bw-insight-row .ir-value {
    font-family: var(--font-mono);
    font-size: 0.88rem;
    font-weight: 500;
    color: var(--white);
}
.bw-insight-row .ir-sub {
    font-size: 0.65rem;
    color: var(--cream-mute);
    margin-left: 6px;
}

/* ── ALLOCATION TABLE ── */
.bw-alloc-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
}
.bw-alloc-table tr {
    border-bottom: 1px solid var(--border);
}
.bw-alloc-table tr:last-child { border-bottom: none; }
.bw-alloc-table td {
    padding: 11px 0;
    font-size: 0.85rem;
}
.bw-alloc-table td:first-child {
    color: var(--cream-dim);
    font-size: 0.78rem;
}
.bw-alloc-table td:nth-child(2) {
    text-align: center;
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--gold);
    letter-spacing: 0.05em;
}
.bw-alloc-table td:last-child {
    text-align: right;
    font-family: var(--font-mono);
    font-size: 0.88rem;
    color: var(--white);
    font-weight: 500;
}

/* ── PROGRESS BAR ── */
.bw-bar-wrap {
    width: 100%;
    height: 2px;
    background: var(--border-md);
    border-radius: 2px;
    margin-top: 6px;
    overflow: hidden;
}
.bw-bar-fill {
    height: 100%;
    background: var(--gold);
    border-radius: 2px;
    transition: width 0.6s ease;
}

/* ── DIVIDER ── */
.bw-divider {
    border: none;
    border-top: 1px solid var(--border);
    margin: 24px 0;
}

/* ── FOOTER ── */
.bw-footer {
    text-align: center;
    font-family: var(--font-mono);
    font-size: 0.6rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--cream-mute);
    margin-top: 48px;
    padding-top: 24px;
    border-top: 1px solid var(--border);
}

/* ── USER BAR ── */
.bw-userbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 24px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 8px;
}
.bw-userbar .ub-email {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--cream-mute);
    letter-spacing: 0.06em;
}
.bw-userbar .ub-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--green);
    display: inline-block;
    margin-right: 8px;
}

/* ════════════════════════════════════════
   STREAMLIT WIDGET OVERRIDES
   ════════════════════════════════════════ */

/* Labels */
[data-testid="stWidgetLabel"] p,
[data-baseweb="form-control-label"] {
    font-family: var(--font-mono) !important;
    font-size: 0.62rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--cream-mute) !important;
    margin-bottom: 6px !important;
}

/* Text inputs */
[data-baseweb="input"],
[data-baseweb="input"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
}
[data-baseweb="input"] input {
    background: transparent !important;
    color: var(--white) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.9rem !important;
    padding: 10px 14px !important;
}
[data-baseweb="input"]:focus-within {
    border-color: var(--gold-dim) !important;
    box-shadow: 0 0 0 3px var(--gold-glow) !important;
}

/* Textarea */
[data-baseweb="textarea"] textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--white) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.85rem !important;
    padding: 10px 14px !important;
}
[data-baseweb="textarea"]:focus-within {
    border-color: var(--gold-dim) !important;
}

/* Number input */
[data-testid="stNumberInput"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stNumberInput"] input {
    background: transparent !important;
    color: var(--white) !important;
    font-family: var(--font-mono) !important;
    font-size: 1rem !important;
}
[data-testid="stNumberInput"] button {
    background: var(--bg-elevated) !important;
    border: none !important;
    color: var(--cream-dim) !important;
}
[data-testid="stNumberInput"] button:hover {
    background: var(--gold-glow) !important;
    color: var(--gold) !important;
}

/* Select box */
[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
}
[data-baseweb="select"] > div > div > div,
[data-baseweb="select"] > div span {
    color: var(--white) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.85rem !important;
}
[data-baseweb="select"] svg { color: var(--cream-mute) !important; }

/* Dropdown list */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"] {
    background: #1a1f2a !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
}
[role="option"] {
    background: transparent !important;
    color: var(--cream-dim) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.82rem !important;
    padding: 10px 16px !important;
    border-bottom: 1px solid var(--border) !important;
}
[role="option"]:last-child { border-bottom: none !important; }
[role="option"]:hover {
    background: var(--gold-glow) !important;
    color: var(--gold) !important;
}
[aria-selected="true"] {
    background: var(--gold-glow) !important;
    color: var(--gold) !important;
}

/* Date input */
[data-testid="stDateInput"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
}
[data-testid="stDateInput"] input {
    background: transparent !important;
    color: var(--white) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.88rem !important;
}

/* Form submit button */
[data-testid="stFormSubmitButton"] button {
    background: var(--gold) !important;
    color: #080a0e !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
    padding: 11px 28px !important;
    width: 100% !important;
    transition: background 0.2s, transform 0.1s !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #d4b460 !important;
    transform: translateY(-1px) !important;
}
[data-testid="stFormSubmitButton"] button:active {
    transform: translateY(0) !important;
}

/* Secondary buttons */
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: var(--cream-dim) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.05em !important;
    padding: 8px 16px !important;
    transition: border-color 0.2s, color 0.2s !important;
}
[data-testid="baseButton-secondary"]:hover {
    border-color: var(--gold-dim) !important;
    color: var(--gold) !important;
    background: var(--gold-glow) !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 8px !important;
}
[data-testid="stExpander"] summary {
    font-family: var(--font-mono) !important;
    font-size: 0.68rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--cream-dim) !important;
    padding: 14px 18px !important;
}
[data-testid="stExpander"] summary:hover { color: var(--gold) !important; }
[data-testid="stExpanderToggleIcon"] { color: var(--gold-dim) !important; }
[data-testid="stExpander"] > div > div {
    padding: 4px 18px 18px !important;
}

/* Dataframe */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius-sm) !important;
    overflow: hidden !important;
}
[data-testid="stDataFrame"] table {
    background: var(--bg-card) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.78rem !important;
}
[data-testid="stDataFrame"] th {
    background: var(--bg-elevated) !important;
    color: var(--cream-mute) !important;
    font-size: 0.58rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border-md) !important;
    padding: 10px 12px !important;
    font-weight: 400 !important;
}
[data-testid="stDataFrame"] td {
    color: var(--cream-dim) !important;
    border-bottom: 1px solid var(--border) !important;
    padding: 9px 12px !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: rgba(201,168,76,0.03) !important;
}

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid var(--border-md) !important;
    gap: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: var(--font-mono) !important;
    font-size: 0.65rem !important;
    font-weight: 400 !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: var(--cream-mute) !important;
    padding: 10px 20px !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom-color: var(--gold) !important;
    background: transparent !important;
}

/* Alert boxes */
[data-testid="stAlert"] {
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.75rem !important;
    border-left-width: 2px !important;
}
[data-testid="stNotificationContentInfo"] {
    background: rgba(232,224,208,0.04) !important;
    border-left-color: var(--cream-mute) !important;
}
[data-testid="stNotificationContentSuccess"] {
    background: var(--green-bg) !important;
    border-left-color: var(--green) !important;
}
[data-testid="stNotificationContentWarning"] {
    background: var(--warn-bg) !important;
    border-left-color: var(--amber-warn) !important;
}
[data-testid="stNotificationContentError"] {
    background: var(--red-bg) !important;
    border-left-color: var(--red) !important;
}

/* Columns gap */
[data-testid="stHorizontalBlock"] {
    gap: 12px !important;
}

/* Hide branding */
#MainMenu, footer, [data-testid="stStatusWidget"] { visibility: hidden !important; }
hr { border-color: var(--border) !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "supabase_session" not in st.session_state:
    st.session_state.supabase_session = None
if "income_form_key" not in st.session_state:
    st.session_state.income_form_key = 0
if "expense_form_key" not in st.session_state:
    st.session_state.expense_form_key = 0
if "show_reset" not in st.session_state:
    st.session_state.show_reset = False

# ====================== MASTHEAD ======================
st.markdown("""
<div class="bw-masthead">
    <div class="bw-masthead-label">Biverway &nbsp;·&nbsp; Private Finance</div>
    <h1>Finance OS</h1>
    <div class="bw-masthead-sub">Your personal wealth command center</div>
</div>
""", unsafe_allow_html=True)

# ====================== AUTH WALL ======================
if st.session_state.supabase_session is None:

    # ── FORGOT PASSWORD ──
    if st.session_state.show_reset:
        st.markdown('<span class="bw-section-label">Password Reset</span>', unsafe_allow_html=True)
        with st.form("reset_form"):
            reset_email = st.text_input("Email address")
            submit_reset = st.form_submit_button("Send Reset Link")
        if submit_reset:
            try:
                client.auth.reset_password_email(
                    reset_email,
                    options={"redirect_to": "https://biverway-finance-tracker-v2-3weeiriwgi5sqcczk3uuxd.streamlit.app"}
                )
                st.success("Reset link sent. Check your inbox.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        if st.button("← Back to Login"):
            st.session_state.show_reset = False
            st.rerun()
        st.stop()

    # ── LOGIN / SIGNUP ──
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        with st.form("login_form"):
            email    = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit   = st.form_submit_button("Sign In")
        if submit:
            try:
                res = client.auth.sign_in_with_password({"email": email, "password": password})
                if res.session:
                    st.session_state.supabase_session = res.session
                    st.rerun()
            except Exception as e:
                err = str(e).lower()
                if "invalid" in err or "credentials" in err:
                    st.error("Incorrect email or password.")
                elif "email not confirmed" in err:
                    st.warning("Please confirm your email before signing in.")
                else:
                    st.error(f"Sign in failed: {e}")

        if st.button("Forgot password?"):
            st.session_state.show_reset = True
            st.rerun()

    with tab2:
        with st.form("signup_form"):
            new_email    = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            submit_new   = st.form_submit_button("Create Account")
        if submit_new:
            try:
                if len(new_password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    res = client.auth.sign_up({"email": new_email, "password": new_password})
                    if res.user and res.user.identities is not None and len(res.user.identities) == 0:
                        st.error("This email is already registered. Please sign in instead.")
                    else:
                        st.success("Account created. Check your email to confirm before signing in.")
            except Exception as e:
                err = str(e).lower()
                if "already registered" in err or "already exists" in err:
                    st.error("This email is already registered. Please sign in instead.")
                elif "rate limit" in err:
                    st.warning("Too many attempts. Please wait a few minutes.")
                else:
                    st.error(f"Registration failed: {e}")
        st.markdown('<p style="font-family:var(--font-mono);font-size:0.65rem;color:var(--cream-mute);margin-top:14px;line-height:1.6;">After registering, check your inbox and confirm your email before signing in.</p>', unsafe_allow_html=True)

    st.stop()

# ====================== USER BAR ======================
user_email = st.session_state.supabase_session.user.email
col_u, col_lo = st.columns([6, 1])
with col_u:
    st.markdown(f'<div class="bw-userbar"><span class="ub-email"><span class="ub-dot"></span>{user_email}</span></div>', unsafe_allow_html=True)
with col_lo:
    if st.button("Sign Out"):
        client.auth.sign_out()
        st.session_state.supabase_session = None
        st.rerun()

# ====================== MONTH SELECTOR ======================
st.markdown('<span class="bw-section-label">Working Period</span>', unsafe_allow_html=True)
working_month = st.date_input("", value=datetime.today(), label_visibility="collapsed")
current_month = working_month.strftime("%b %Y")
st.markdown(f'<div class="bw-month"><span>▸</span>{current_month}</div>', unsafe_allow_html=True)

# ====================== LOAD DATA ======================
income_records  = load_income(current_month)
expense_records = load_expense(current_month)

income_df  = pd.DataFrame(income_records)  if income_records  else pd.DataFrame()
expense_df = pd.DataFrame(expense_records) if expense_records else pd.DataFrame()

if not income_df.empty:
    income_df["amount"] = pd.to_numeric(income_df["amount"], errors="coerce").fillna(0)
if not expense_df.empty:
    expense_df["amount"] = pd.to_numeric(expense_df["amount"], errors="coerce").fillna(0)

# ====================== INCOME ======================
st.markdown('<span class="bw-section-label">Income</span>', unsafe_allow_html=True)

income_type_map = {
    "Skill": "Active",
    "Salary": "Active",
    "Business": "Passive",
    "Dividend / Interest": "Passive",
    "Rental": "Passive"
}

with st.expander("＋  Record Income Entry"):
    with st.form(f"income_form_{st.session_state.income_form_key}"):
        col_a, col_b = st.columns(2)
        with col_a:
            income_source = st.selectbox("Source", list(income_type_map.keys()))
        with col_b:
            amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0, format="%0.0f")
        notes = st.text_area("Notes", height=72, placeholder="Optional context...")
        submit_income = st.form_submit_button("Record Entry")

    if submit_income:
        add_income(current_month, income_source, income_type_map[income_source], amount, notes)
        st.success("Income recorded.")
        st.session_state.income_form_key += 1
        st.rerun()

if not income_df.empty:
    display_income = income_df[["source", "income_type", "amount", "notes"]].copy()
    display_income.columns = ["Source", "Type", "Amount (₦)", "Notes"]
    display_income = display_income.reset_index(drop=True)
    st.dataframe(display_income, use_container_width=True)

    col_del, col_clr = st.columns([3, 1])
    with col_clr:
        if st.button("Clear Month", key="clr_inc"):
            clear_income_month(current_month)
            st.rerun()
    with col_del:
        options = [f"{i} · {row['source']} · ₦{row['amount']:,.0f}" for i, row in income_df.iterrows()]
        del_inc = st.selectbox("Select entry to remove", options=options, key="del_inc_select")
        if st.button("Remove Entry", key="del_inc_btn"):
            sel_idx = int(del_inc.split(" · ")[0])
            delete_income(income_df.iloc[sel_idx]["id"])
            st.rerun()
else:
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.72rem;color:var(--cream-mute);padding:8px 0;">No income entries for this period.</p>', unsafe_allow_html=True)

# ====================== EXPENSES ======================
st.markdown('<span class="bw-section-label">Expenses</span>', unsafe_allow_html=True)

expense_categories = [
    "Rent", "Food", "Utilities", "Transport",
    "Healthcare", "Education", "Subscription", "Family Support"
]

with st.expander("＋  Record Expense Entry"):
    with st.form(f"expense_form_{st.session_state.expense_form_key}"):
        col_c, col_d = st.columns(2)
        with col_c:
            category = st.selectbox("Category", expense_categories)
        with col_d:
            expense_amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0, format="%0.0f")
        description = st.text_area("Description", height=72, placeholder="Optional context...")
        submit_expense = st.form_submit_button("Record Entry")

    if submit_expense:
        add_expense(current_month, category, expense_amount, description)
        st.success("Expense recorded.")
        st.session_state.expense_form_key += 1
        st.rerun()

if not expense_df.empty:
    total_expense = expense_df["amount"].sum()
    if total_expense > 0:
        expense_df["Share"] = (expense_df["amount"] / total_expense * 100).round(1).astype(str) + "%"
    else:
        expense_df["Share"] = "—"

    display_expense = expense_df[["category", "amount", "Share", "description"]].copy()
    display_expense.columns = ["Category", "Amount (₦)", "Share", "Description"]
    display_expense = display_expense.reset_index(drop=True)
    st.dataframe(display_expense, use_container_width=True)

    col_del2, col_clr2 = st.columns([3, 1])
    with col_clr2:
        if st.button("Clear Month", key="clr_exp"):
            clear_expense_month(current_month)
            st.rerun()
    with col_del2:
        options2 = [f"{i} · {row['category']} · ₦{row['amount']:,.0f}" for i, row in expense_df.iterrows()]
        del_exp = st.selectbox("Select entry to remove", options=options2, key="del_exp_select")
        if st.button("Remove Entry", key="del_exp_btn"):
            sel_idx = int(del_exp.split(" · ")[0])
            delete_expense(expense_df.iloc[sel_idx]["id"])
            st.rerun()
else:
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.72rem;color:var(--cream-mute);padding:8px 0;">No expense entries for this period.</p>', unsafe_allow_html=True)

# ====================== PERFORMANCE ======================
total_income  = income_df["amount"].sum()  if not income_df.empty  else 0
total_expense = expense_df["amount"].sum() if not expense_df.empty else 0
net_surplus   = total_income - total_expense
savings_rate  = (net_surplus / total_income * 100) if total_income else 0

st.markdown('<span class="bw-section-label">Financial Performance</span>', unsafe_allow_html=True)

# KPI grid always visible
surplus_cls = "positive" if net_surplus >= 0 else "negative"
st.markdown(f"""
<div class="bw-kpi-grid">
    <div class="bw-kpi">
        <span class="kpi-label">Total Income</span>
        <span class="kpi-value">₦{total_income:,.0f}</span>
    </div>
    <div class="bw-kpi">
        <span class="kpi-label">Total Expenses</span>
        <span class="kpi-value">₦{total_expense:,.0f}</span>
    </div>
    <div class="bw-kpi">
        <span class="kpi-label">Net Surplus</span>
        <span class="kpi-value {surplus_cls}">₦{net_surplus:,.0f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("Performance Analysis"):
    if total_income == 0:
        st.info("No income recorded for this period.")
    else:
        # Savings rate
        if savings_rate >= 30:
            status_cls = "green"
            status_txt = f"Savings rate {savings_rate:.1f}% — strong surplus discipline"
        elif 15 <= savings_rate < 30:
            status_cls = "yellow"
            status_txt = f"Savings rate {savings_rate:.1f}% — stable, room to optimize"
        elif 1 <= savings_rate < 15:
            status_cls = "yellow"
            status_txt = f"Savings rate {savings_rate:.1f}% — margin is thin"
        else:
            status_cls = "red"
            status_txt = f"Deficit — expenses exceed income by ₦{abs(net_surplus):,.0f}"

        st.markdown(f'<div class="bw-status {status_cls}">{status_txt}</div>', unsafe_allow_html=True)

        # Savings bar
        bar_pct = min(max(savings_rate, 0), 100)
        st.markdown(f"""
        <div style="margin:16px 0 24px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                <span style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.1em;color:var(--cream-mute);text-transform:uppercase;">Savings Rate</span>
                <span style="font-family:var(--font-mono);font-size:0.6rem;color:var(--gold);">{savings_rate:.1f}%</span>
            </div>
            <div class="bw-bar-wrap"><div class="bw-bar-fill" style="width:{bar_pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        # Income structure
        if not income_df.empty:
            active_income  = income_df[income_df["income_type"] == "Active"]["amount"].sum()
            passive_income = income_df[income_df["income_type"] == "Passive"]["amount"].sum()
            active_pct  = (active_income  / total_income * 100) if total_income else 0
            passive_pct = (passive_income / total_income * 100) if total_income else 0

            st.markdown('<span style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--cream-mute);display:block;margin-bottom:10px;">Income Structure</span>', unsafe_allow_html=True)
            st.markdown(f"""
            <div>
                <div class="bw-insight-row">
                    <span class="ir-label">Active Income</span>
                    <span class="ir-value">₦{active_income:,.0f}<span class="ir-sub">{active_pct:.0f}%</span></span>
                </div>
                <div class="bw-insight-row">
                    <span class="ir-label">Passive Income</span>
                    <span class="ir-value">₦{passive_income:,.0f}<span class="ir-sub">{passive_pct:.0f}%</span></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Passive income bar
            st.markdown(f"""
            <div style="margin:12px 0 20px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.1em;color:var(--cream-mute);text-transform:uppercase;">Passive Income Share</span>
                    <span style="font-family:var(--font-mono);font-size:0.6rem;color:var(--gold);">{passive_pct:.0f}%</span>
                </div>
                <div class="bw-bar-wrap"><div class="bw-bar-fill" style="width:{passive_pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

            if active_pct >= 70:
                st.markdown('<div class="bw-status yellow">Income heavily effort-dependent — build passive streams to strengthen resilience</div>', unsafe_allow_html=True)
            elif passive_pct >= 50:
                st.markdown('<div class="bw-status green">Passive income majority — strong foundation for wealth accumulation</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="bw-status yellow">Income moderately diversified — continue growing passive streams</div>', unsafe_allow_html=True)

        # Top expenses
        if not expense_df.empty:
            st.markdown('<span style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--cream-mute);display:block;margin:20px 0 10px;">Cost Concentration</span>', unsafe_allow_html=True)
            sorted_exp = expense_df.sort_values("amount", ascending=False).head(3)
            rows = ""
            for _, row in sorted_exp.iterrows():
                share = f"{row['amount']/total_expense*100:.0f}%" if total_expense > 0 else "—"
                rows += f"""
                <div class="bw-insight-row">
                    <span class="ir-label">{row['category']}</span>
                    <span class="ir-value">₦{row['amount']:,.0f}<span class="ir-sub">{share}</span></span>
                </div>"""
            st.markdown(f'<div>{rows}</div>', unsafe_allow_html=True)

# ====================== ALLOCATION ======================
st.markdown('<span class="bw-section-label">Surplus Allocation</span>', unsafe_allow_html=True)

with st.expander("Allocation Planner"):
    if total_income == 0:
        st.info("Record income to unlock allocation planning.")
    elif net_surplus <= 0:
        st.warning("No surplus available. Allocation requires positive net surplus.")
    else:
        allocation_modes = {
            "Balanced (Default)":       {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 10, "Charity": 5},
            "Wealth Acceleration":      {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 5,  "Charity": 5},
            "Generosity Focus":         {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 10, "Charity": 25},
            "Security First":           {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5,  "Charity": 5},
        }

        mode = st.selectbox("Allocation Strategy", list(allocation_modes.keys()))
        allocation_list = [
            {"Category": cat, "Percentage (%)": pct, "Allocated Amount (₦)": round(net_surplus * pct / 100, 0)}
            for cat, pct in allocation_modes[mode].items()
        ]

        st.markdown('<span style="font-family:var(--font-mono);font-size:0.6rem;letter-spacing:0.15em;text-transform:uppercase;color:var(--cream-mute);display:block;margin:16px 0 10px;">Allocation Breakdown</span>', unsafe_allow_html=True)

        rows_alloc = ""
        for r in allocation_list:
            bar_w = r["Percentage (%)"]
            rows_alloc += f"""
            <tr>
                <td>{r['Category']}</td>
                <td>{r['Percentage (%)']}%</td>
                <td>₦{r['Allocated Amount (₦)']:,.0f}</td>
            </tr>"""

        st.markdown(f"""
        <table class="bw-alloc-table">
            <tr style="border-bottom:1px solid var(--gold-line);">
                <td style="color:var(--cream-mute);font-family:var(--font-mono);font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;padding-bottom:8px;">Category</td>
                <td style="text-align:center;color:var(--cream-mute);font-family:var(--font-mono);font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;padding-bottom:8px;">Allocation</td>
                <td style="text-align:right;color:var(--cream-mute);font-family:var(--font-mono);font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;padding-bottom:8px;">Amount</td>
            </tr>
            {rows_alloc}
        </table>
        """, unsafe_allow_html=True)

        if st.button("Save Allocation to Record"):
            save_allocation(current_month, allocation_list)
            st.success("Allocation saved.")

# ====================== FOOTER ======================
st.markdown(f"""
<div class="bw-footer">
    Biverway Finance OS &nbsp;·&nbsp; Built on the Biverway Wealth System &nbsp;·&nbsp; {datetime.today().year}
</div>
""", unsafe_allow_html=True)
