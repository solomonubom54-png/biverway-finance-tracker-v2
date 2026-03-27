import streamlit as st
import pandas as pd
from datetime import datetime
from core.supabase_db import (
    client,
    add_income, load_income, delete_income, clear_income_month,
    add_expense, load_expense, delete_expense, clear_expense_month,
    is_month_locked, lock_month
)

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="Biverway Financial OS", layout="wide")

# ====================== GLOBAL STYLES ======================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --bg-base:    #080a0e;
    --bg-card:    #0d1017;
    --bg-elevated:#131720;
    --bg-input:   #0f1318;
    --gold:       #c9a84c;
    --gold-dim:   #9a7a34;
    --gold-glow:  rgba(201,168,76,0.07);
    --gold-line:  rgba(201,168,76,0.18);
    --cream:      #e8e0d0;
    --cream-dim:  rgba(232,224,208,0.6);
    --cream-mute: rgba(232,224,208,0.28);
    --white:      #f0ece4;
    --green:      #4caf7d;
    --green-bg:   rgba(76,175,125,0.08);
    --red:        #c0544a;
    --red-bg:     rgba(192,84,74,0.08);
    --amber-warn: #d4922a;
    --warn-bg:    rgba(212,146,42,0.08);
    --border:     rgba(255,255,255,0.05);
    --border-md:  rgba(255,255,255,0.09);
    --radius-sm:  8px;
    --radius:     12px;
    --font-disp:  'Sora', sans-serif;
    --font-mono:  'IBM Plex Mono', monospace;
}

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

::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 3px; }

.bw-masthead {
    padding: 32px 0 22px;
    border-bottom: 1px solid var(--gold-line);
    margin-bottom: 28px;
}
.bw-masthead-label {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--gold);
    margin-bottom: 10px;
    display: block;
}
.bw-masthead h1 {
    font-family: var(--font-disp);
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    color: var(--white);
    margin: 0 0 6px 0;
    line-height: 1.1;
    text-transform: uppercase;
}
.bw-masthead-sub {
    font-size: 0.72rem;
    color: var(--cream-mute);
    font-weight: 300;
    letter-spacing: 0.04em;
}

.bw-section-label {
    font-family: var(--font-mono);
    font-size: 0.58rem;
    letter-spacing: 0.24em;
    text-transform: uppercase;
    color: var(--gold);
    padding-bottom: 10px;
    margin: 28px 0 14px 0;
    border-bottom: 1px solid var(--gold-line);
    display: block;
}

.bw-month {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--gold-glow);
    border: 1px solid var(--gold-line);
    color: var(--gold);
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 5px 13px;
    border-radius: 100px;
    margin-bottom: 20px;
}

.bw-kpi-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border-md);
    border-radius: var(--radius);
    overflow: hidden;
    margin: 0 0 20px 0;
}
.bw-kpi {
    background: var(--bg-card);
    padding: 16px 12px 14px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 82px;
}
.bw-kpi.highlight {
    background: linear-gradient(160deg, #0d1017 55%, rgba(201,168,76,0.05) 100%);
}
.bw-kpi .kpi-label {
    font-family: var(--font-mono);
    font-size: 0.48rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--cream-mute);
    margin-bottom: 8px;
    display: block;
    line-height: 1.6;
}
.bw-kpi .kpi-value {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    font-weight: 500;
    color: var(--white);
    line-height: 1;
    display: block;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.bw-kpi.highlight .kpi-value { font-size: 0.88rem; font-weight: 600; }
.bw-kpi .kpi-value.positive { color: var(--green); }
.bw-kpi .kpi-value.negative { color: var(--red); }

.bw-status {
    display: inline-flex;
    align-items: flex-start;
    gap: 9px;
    padding: 10px 14px;
    border-radius: var(--radius-sm);
    font-family: var(--font-mono);
    font-size: 0.68rem;
    letter-spacing: 0.03em;
    margin-top: 4px;
    line-height: 1.5;
}
.bw-status.green  { background: var(--green-bg); color: var(--green); border: 1px solid rgba(76,175,125,0.18); }
.bw-status.yellow { background: var(--warn-bg);  color: var(--amber-warn); border: 1px solid rgba(212,146,42,0.18); }
.bw-status.red    { background: var(--red-bg);   color: var(--red); border: 1px solid rgba(192,84,74,0.18); }
.bw-status-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; display: inline-block; flex-shrink: 0; margin-top: 5px; }

.bw-insight-row { display: flex; justify-content: space-between; align-items: baseline; padding: 11px 0; border-bottom: 1px solid var(--border); }
.bw-insight-row:last-child { border-bottom: none; }
.bw-insight-row .ir-label { font-size: 0.78rem; color: var(--cream-dim); font-weight: 400; }
.bw-insight-row .ir-value { font-family: var(--font-mono); font-size: 0.88rem; font-weight: 500; color: var(--white); }
.bw-insight-row .ir-sub { font-size: 0.62rem; color: var(--cream-mute); margin-left: 7px; }

.bw-bar-wrap { width: 100%; height: 1px; background: var(--border-md); border-radius: 1px; margin-top: 6px; overflow: hidden; }
.bw-bar-fill { height: 100%; background: linear-gradient(90deg, var(--gold-dim), var(--gold)); border-radius: 1px; }

.bw-record-table { border: 1px solid var(--border-md); border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 14px; }
.bw-record-row { display: flex; justify-content: space-between; align-items: center; padding: 13px 16px; border-bottom: 1px solid var(--border); background: var(--bg-card); }
.bw-record-row:last-child { border-bottom: none; }
.bw-record-row .rr-left { display: flex; flex-direction: column; gap: 3px; }
.bw-record-row .rr-source { font-size: 0.82rem; font-weight: 500; color: var(--white); }
.bw-record-row .rr-meta { font-size: 0.63rem; color: var(--cream-mute); font-family: var(--font-mono); letter-spacing: 0.04em; }
.bw-record-row .rr-amount { font-family: var(--font-mono); font-size: 0.92rem; font-weight: 500; color: var(--white); }

.bw-alloc-wrap { border: 1px solid var(--border-md); border-radius: var(--radius-sm); overflow: hidden; margin: 14px 0 16px; }
.bw-alloc-row { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border); background: var(--bg-card); }
.bw-alloc-row:last-child { border-bottom: none; }
.bw-alloc-row .ar-cat { flex: 1; font-size: 0.8rem; color: var(--cream-dim); }
.bw-alloc-row .ar-pct { font-family: var(--font-mono); font-size: 0.63rem; color: var(--gold); letter-spacing: 0.05em; width: 38px; text-align: center; }
.bw-alloc-row .ar-amt { font-family: var(--font-mono); font-size: 0.85rem; font-weight: 500; color: var(--white); text-align: right; min-width: 96px; }

.bw-lock-banner { background: rgba(201,168,76,0.05); border: 1px solid var(--gold-line); border-radius: var(--radius-sm); padding: 11px 16px; margin-bottom: 16px; font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.05em; color: var(--gold); display: flex; align-items: center; gap: 10px; }

.bw-userbar { padding: 10px 0 18px; border-bottom: 1px solid var(--border); margin-bottom: 4px; }
.bw-ub-email { font-family: var(--font-mono); font-size: 0.63rem; color: var(--cream-mute); letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px; }
.bw-ub-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); display: inline-block; flex-shrink: 0; }

.bw-footer { text-align: center; font-family: var(--font-mono); font-size: 0.55rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream-mute); margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border); }

/* STREAMLIT OVERRIDES */
[data-testid="stWidgetLabel"] p,
[data-baseweb="form-control-label"] {
    font-family: var(--font-disp) !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.02em !important;
    text-transform: none !important;
    color: var(--cream-dim) !important;
    font-weight: 400 !important;
    margin-bottom: 5px !important;
}
[data-baseweb="input"] > div { background: var(--bg-input) !important; border: 1px solid var(--border-md) !important; border-radius: var(--radius-sm) !important; }
[data-baseweb="input"] input { background: transparent !important; color: var(--white) !important; font-family: var(--font-mono) !important; font-size: 0.88rem !important; padding: 10px 14px !important; }
[data-baseweb="input"]:focus-within > div { border-color: var(--gold-dim) !important; box-shadow: 0 0 0 3px var(--gold-glow) !important; }
[data-baseweb="textarea"] textarea { background: var(--bg-input) !important; border: 1px solid var(--border-md) !important; border-radius: var(--radius-sm) !important; color: var(--cream-dim) !important; font-family: var(--font-disp) !important; font-size: 0.82rem !important; padding: 10px 14px !important; }
[data-testid="stNumberInput"] > div { background: var(--bg-input) !important; border: 1px solid var(--border-md) !important; border-radius: var(--radius-sm) !important; }
[data-testid="stNumberInput"] input { background: transparent !important; color: var(--white) !important; font-family: var(--font-mono) !important; font-size: 0.95rem !important; }
[data-testid="stNumberInput"] button { background: var(--bg-elevated) !important; border: none !important; color: var(--cream-mute) !important; }
[data-testid="stNumberInput"] button:hover { color: var(--gold) !important; background: var(--gold-glow) !important; }
[data-baseweb="select"] > div { background: var(--bg-input) !important; border: 1px solid var(--border-md) !important; border-radius: var(--radius-sm) !important; }
[data-baseweb="select"] > div > div > div, [data-baseweb="select"] > div span { color: var(--white) !important; font-family: var(--font-disp) !important; font-size: 0.85rem !important; }

/* Dropdown — white bg, black text */
[data-baseweb="popover"], [data-baseweb="menu"], ul[role="listbox"], [role="listbox"] { background: #ffffff !important; border: 1px solid #e0ddd8 !important; border-radius: var(--radius-sm) !important; box-shadow: 0 12px 40px rgba(0,0,0,0.35) !important; }
[role="option"] { background: #ffffff !important; color: #1a1a1a !important; font-family: var(--font-disp) !important; font-size: 0.85rem !important; padding: 11px 16px !important; border-bottom: 1px solid #f0ede8 !important; cursor: pointer !important; }
[role="option"]:last-child { border-bottom: none !important; }
[role="option"]:hover { background: #fdf8f0 !important; color: #9a7a34 !important; }
[aria-selected="true"] { background: #fdf3de !important; color: #9a7a34 !important; font-weight: 600 !important; }

[data-testid="stDateInput"] > div { background: var(--bg-input) !important; border: 1px solid var(--border-md) !important; border-radius: var(--radius-sm) !important; }
[data-testid="stDateInput"] input { background: transparent !important; color: var(--white) !important; font-family: var(--font-mono) !important; font-size: 0.85rem !important; }

/* PRIMARY button — gold */
[data-testid="stFormSubmitButton"] button { background: var(--gold) !important; color: #080a0e !important; border: none !important; border-radius: var(--radius-sm) !important; font-family: var(--font-disp) !important; font-size: 0.78rem !important; font-weight: 600 !important; letter-spacing: 0.04em !important; padding: 11px 28px !important; width: 100% !important; transition: background 0.2s, transform 0.1s !important; box-shadow: 0 2px 12px rgba(201,168,76,0.18) !important; }
[data-testid="stFormSubmitButton"] button:hover { background: #d4b460 !important; transform: translateY(-1px) !important; }

/* SECONDARY button — white bg, dark text */
[data-testid="baseButton-secondary"] { background: #ffffff !important; color: #1a1a1a !important; border: 1px solid #d0ccc5 !important; border-radius: var(--radius-sm) !important; font-family: var(--font-disp) !important; font-size: 0.74rem !important; font-weight: 500 !important; letter-spacing: 0.02em !important; padding: 8px 18px !important; transition: all 0.15s !important; }
[data-testid="baseButton-secondary"]:hover { background: #fdf8f0 !important; border-color: var(--gold-dim) !important; color: #9a7a34 !important; }

/* Expanders */
[data-testid="stExpander"] { background: var(--bg-card) !important; border: 1px solid var(--border-md) !important; border-radius: var(--radius) !important; margin-bottom: 8px !important; overflow: hidden !important; }
[data-testid="stExpander"] > details > summary { background: var(--bg-elevated) !important; font-family: var(--font-disp) !important; font-size: 0.78rem !important; font-weight: 500 !important; color: var(--cream-dim) !important; padding: 13px 18px !important; border-bottom: 1px solid var(--border) !important; list-style: none !important; }
[data-testid="stExpander"] > details[open] > summary { color: var(--gold) !important; border-bottom-color: var(--gold-line) !important; }
[data-testid="stExpander"] > details > summary:hover { color: var(--gold) !important; }
[data-testid="stExpanderToggleIcon"] { color: var(--gold-dim) !important; }
[data-testid="stExpander"] > details > div { padding: 16px 18px 18px !important; background: var(--bg-card) !important; }

[data-testid="stDataFrame"] { border: 1px solid var(--border-md) !important; border-radius: var(--radius-sm) !important; overflow: hidden !important; }
[data-testid="stDataFrame"] table { background: var(--bg-card) !important; font-family: var(--font-mono) !important; font-size: 0.76rem !important; }
[data-testid="stDataFrame"] th { background: var(--bg-elevated) !important; color: var(--cream-mute) !important; font-size: 0.54rem !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; border-bottom: 1px solid var(--border-md) !important; padding: 9px 12px !important; font-weight: 400 !important; }
[data-testid="stDataFrame"] td { color: var(--cream-dim) !important; border-bottom: 1px solid var(--border) !important; padding: 9px 12px !important; }

[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid var(--border-md) !important; background: transparent !important; }
[data-testid="stTabs"] [role="tab"] { font-family: var(--font-disp) !important; font-size: 0.75rem !important; font-weight: 400 !important; color: var(--cream-mute) !important; padding: 10px 20px !important; border-radius: 0 !important; border-bottom: 2px solid transparent !important; background: transparent !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: var(--gold) !important; border-bottom-color: var(--gold) !important; }

[data-testid="stAlert"] { border-radius: var(--radius-sm) !important; font-family: var(--font-disp) !important; font-size: 0.76rem !important; border-left-width: 2px !important; }
[data-testid="stNotificationContentInfo"]    { background: rgba(232,224,208,0.03) !important; border-left-color: var(--cream-mute) !important; }
[data-testid="stNotificationContentSuccess"] { background: var(--green-bg) !important; border-left-color: var(--green) !important; }
[data-testid="stNotificationContentWarning"] { background: var(--warn-bg) !important; border-left-color: var(--amber-warn) !important; }
[data-testid="stNotificationContentError"]   { background: var(--red-bg) !important; border-left-color: var(--red) !important; }

[data-testid="stHorizontalBlock"] { gap: 10px !important; }
#MainMenu, footer, [data-testid="stStatusWidget"] { visibility: hidden !important; }
hr { border-color: var(--border) !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "supabase_session"  not in st.session_state: st.session_state.supabase_session  = None
if "income_form_key"   not in st.session_state: st.session_state.income_form_key   = 0
if "expense_form_key"  not in st.session_state: st.session_state.expense_form_key  = 0
if "show_reset"        not in st.session_state: st.session_state.show_reset        = False

def full_month(dt):  return dt.strftime("%B %Y")
def short_month(dt): return dt.strftime("%b %Y")

# ====================== MASTHEAD ======================
st.markdown("""
<div class="bw-masthead">
    <span class="bw-masthead-label">Biverway &nbsp;·&nbsp; Private Finance</span>
    <h1>Biverway Financial OS</h1>
    <div class="bw-masthead-sub">Your personal wealth command center</div>
</div>
""", unsafe_allow_html=True)

# ====================== AUTH WALL ======================
if st.session_state.supabase_session is None:

    if st.session_state.show_reset:
        st.markdown('<span class="bw-section-label">Password Reset</span>', unsafe_allow_html=True)
        with st.form("reset_form"):
            reset_email  = st.text_input("Email address")
            submit_reset = st.form_submit_button("Send Reset Link")
        if submit_reset:
            try:
                client.auth.reset_password_email(
                    reset_email,
                    options={"redirect_to": "https://biverway-finance-tracker-v2-3weeiriwgi5sqcczk3uuxd.streamlit.app"}
                )
                st.success("Reset link sent — check your inbox.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        if st.button("← Back to Sign In"):
            st.session_state.show_reset = False
            st.rerun()
        st.stop()

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
        st.markdown('<p style="font-family:var(--font-disp);font-size:0.68rem;color:var(--cream-mute);margin-top:12px;line-height:1.7;">After registering, confirm your email before signing in.</p>', unsafe_allow_html=True)

    st.stop()

# ====================== USER BAR ======================
user_email = st.session_state.supabase_session.user.email
col_u, col_lo = st.columns([6, 1])
with col_u:
    st.markdown(f'<div class="bw-userbar"><span class="bw-ub-email"><span class="bw-ub-dot"></span>{user_email}</span></div>', unsafe_allow_html=True)
with col_lo:
    if st.button("Sign Out"):
        client.auth.sign_out()
        st.session_state.supabase_session = None
        st.rerun()

# ====================== MONTH SELECTOR ======================
st.markdown('<span class="bw-section-label">Working Period</span>', unsafe_allow_html=True)
working_month      = st.date_input("", value=datetime.today(), label_visibility="collapsed")
current_month      = short_month(working_month)
current_month_full = full_month(working_month)
st.markdown(f'<div class="bw-month"><span>▸</span>{current_month_full}</div>', unsafe_allow_html=True)

# ====================== LOCK CHECK ======================
month_locked = is_month_locked(current_month)
if month_locked:
    st.markdown(f'<div class="bw-lock-banner">🔒 &nbsp; {current_month_full} is locked — all records are permanently frozen</div>', unsafe_allow_html=True)

# ====================== LOAD DATA ======================
income_records  = load_income(current_month)
expense_records = load_expense(current_month)

income_df  = pd.DataFrame(income_records).reset_index(drop=True)  if income_records  else pd.DataFrame()
expense_df = pd.DataFrame(expense_records).reset_index(drop=True) if expense_records else pd.DataFrame()

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

if not month_locked:
    with st.expander("＋  Record Income Entry"):
        with st.form(f"income_form_{st.session_state.income_form_key}"):
            col_a, col_b = st.columns(2)
            with col_a:
                income_source = st.selectbox("Source", list(income_type_map.keys()))
            with col_b:
                amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0, format="%0.0f")
            notes = st.text_area("Notes", height=70, placeholder="Optional context...")
            submit_income = st.form_submit_button("Record Income")
        if submit_income:
            add_income(current_month, income_source, income_type_map[income_source], amount, notes)
            st.success("Income recorded.")
            st.session_state.income_form_key += 1
            st.rerun()

if not income_df.empty:
    rows_html = ""
    for i, row in income_df.iterrows():
        rows_html += f"""
        <div class="bw-record-row">
            <div class="rr-left">
                <span class="rr-source">{row['source']}</span>
                <span class="rr-meta">{row['income_type']} &nbsp;·&nbsp; {row.get('notes','') or '—'}</span>
            </div>
            <span class="rr-amount">₦{row['amount']:,.0f}</span>
        </div>"""
    st.markdown(f'<div class="bw-record-table">{rows_html}</div>', unsafe_allow_html=True)

    if not month_locked:
        col_del, col_clr = st.columns([3, 1])
        with col_clr:
            if st.button("Clear Month", key="clr_inc"):
                clear_income_month(current_month)
                st.rerun()
        with col_del:
            # Store IDs as plain list — avoids pandas iloc/column lookup issues
            inc_ids    = list(income_df["id"])
            inc_labels = [f"{i} · {row['source']} · ₦{row['amount']:,.0f}"
                          for i, row in income_df.iterrows()]
            del_inc = st.selectbox("Select entry to remove", options=inc_labels, key="del_inc_select")
            if st.button("Remove Income", key="del_inc_btn"):
                sel_idx = int(del_inc.split(" · ")[0])
                delete_income(inc_ids[sel_idx])
                st.rerun()
else:
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.68rem;color:var(--cream-mute);padding:6px 0;">No income entries for this period.</p>', unsafe_allow_html=True)

# ====================== EXPENSES ======================
st.markdown('<span class="bw-section-label">Expenses</span>', unsafe_allow_html=True)

expense_categories = [
    "Rent", "Food", "Utilities", "Transport",
    "Healthcare", "Education", "Subscription", "Family Support"
]

if not month_locked:
    with st.expander("＋  Record Expense Entry"):
        with st.form(f"expense_form_{st.session_state.expense_form_key}"):
            col_c, col_d = st.columns(2)
            with col_c:
                category = st.selectbox("Category", expense_categories)
            with col_d:
                expense_amount = st.number_input("Amount (₦)", min_value=0.0, step=1000.0, format="%0.0f")
            description = st.text_area("Description", height=70, placeholder="Optional context...")
            submit_expense = st.form_submit_button("Record Expense")
        if submit_expense:
            add_expense(current_month, category, expense_amount, description)
            st.success("Expense recorded.")
            st.session_state.expense_form_key += 1
            st.rerun()

if not expense_df.empty:
    total_expense = expense_df["amount"].sum()
    rows_html2 = ""
    for i, row in expense_df.iterrows():
        share = f"{row['amount']/total_expense*100:.0f}%" if total_expense > 0 else "—"
        rows_html2 += f"""
        <div class="bw-record-row">
            <div class="rr-left">
                <span class="rr-source">{row['category']}</span>
                <span class="rr-meta">{share} of total &nbsp;·&nbsp; {row.get('description','') or '—'}</span>
            </div>
            <span class="rr-amount">₦{row['amount']:,.0f}</span>
        </div>"""
    st.markdown(f'<div class="bw-record-table">{rows_html2}</div>', unsafe_allow_html=True)

    if not month_locked:
        col_del2, col_clr2 = st.columns([3, 1])
        with col_clr2:
            if st.button("Clear Month", key="clr_exp"):
                clear_expense_month(current_month)
                st.rerun()
        with col_del2:
            # Store IDs as plain list — avoids pandas iloc/column lookup issues
            exp_ids    = list(expense_df["id"])
            exp_labels = [f"{i} · {row['category']} · ₦{row['amount']:,.0f}"
                          for i, row in expense_df.iterrows()]
            del_exp = st.selectbox("Select entry to remove", options=exp_labels, key="del_exp_select")
            if st.button("Remove Expense", key="del_exp_btn"):
                sel_idx = int(del_exp.split(" · ")[0])
                delete_expense(exp_ids[sel_idx])
                st.rerun()
else:
    st.markdown('<p style="font-family:var(--font-mono);font-size:0.68rem;color:var(--cream-mute);padding:6px 0;">No expense entries for this period.</p>', unsafe_allow_html=True)

# ====================== PERFORMANCE ======================
total_income  = income_df["amount"].sum()  if not income_df.empty  else 0
total_expense = expense_df["amount"].sum() if not expense_df.empty else 0
net_surplus   = total_income - total_expense
savings_rate  = (net_surplus / total_income * 100) if total_income else 0

st.markdown('<span class="bw-section-label">Financial Performance</span>', unsafe_allow_html=True)

surplus_cls = "positive" if net_surplus >= 0 else "negative"
st.markdown(f"""
<div class="bw-kpi-grid">
    <div class="bw-kpi">
        <span class="kpi-label">Total<br>Income</span>
        <span class="kpi-value">₦{total_income:,.0f}</span>
    </div>
    <div class="bw-kpi">
        <span class="kpi-label">Total<br>Expenses</span>
        <span class="kpi-value">₦{total_expense:,.0f}</span>
    </div>
    <div class="bw-kpi highlight">
        <span class="kpi-label">Net<br>Surplus</span>
        <span class="kpi-value {surplus_cls}">₦{net_surplus:,.0f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

with st.expander("Performance Analysis"):
    if total_income == 0:
        st.info("Record income to see performance analysis.")
    else:
        if savings_rate >= 30:
            s_cls, s_txt = "green",  f"Savings rate {savings_rate:.1f}% — strong surplus discipline"
        elif 15 <= savings_rate < 30:
            s_cls, s_txt = "yellow", f"Savings rate {savings_rate:.1f}% — stable, room to optimize"
        elif 1 <= savings_rate < 15:
            s_cls, s_txt = "yellow", f"Savings rate {savings_rate:.1f}% — margin is thin"
        else:
            s_cls, s_txt = "red",    f"Deficit — expenses exceed income by ₦{abs(net_surplus):,.0f}"

        st.markdown(f'<div class="bw-status {s_cls}"><span class="bw-status-dot"></span>{s_txt}</div>', unsafe_allow_html=True)

        bar_pct = min(max(savings_rate, 0), 100)
        st.markdown(f"""
        <div style="margin:18px 0 22px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:7px;">
                <span style="font-family:var(--font-disp);font-size:0.72rem;color:var(--cream-mute);">Savings Rate</span>
                <span style="font-family:var(--font-mono);font-size:0.68rem;color:var(--gold);">{savings_rate:.1f}%</span>
            </div>
            <div class="bw-bar-wrap"><div class="bw-bar-fill" style="width:{bar_pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        if not income_df.empty:
            active_income  = income_df[income_df["income_type"] == "Active"]["amount"].sum()
            passive_income = income_df[income_df["income_type"] == "Passive"]["amount"].sum()
            active_pct     = (active_income  / total_income * 100) if total_income else 0
            passive_pct    = (passive_income / total_income * 100) if total_income else 0

            st.markdown('<p style="font-family:var(--font-disp);font-size:0.72rem;color:var(--cream-mute);margin:18px 0 8px;">Income Structure</p>', unsafe_allow_html=True)
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
            <div style="margin:14px 0 18px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:7px;">
                    <span style="font-family:var(--font-disp);font-size:0.72rem;color:var(--cream-mute);">Passive Income Share</span>
                    <span style="font-family:var(--font-mono);font-size:0.68rem;color:var(--gold);">{passive_pct:.0f}%</span>
                </div>
                <div class="bw-bar-wrap"><div class="bw-bar-fill" style="width:{passive_pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)

            if active_pct >= 70:
                st.markdown('<div class="bw-status yellow"><span class="bw-status-dot"></span>Income heavily effort-dependent — grow passive streams to build resilience</div>', unsafe_allow_html=True)
            elif passive_pct >= 50:
                st.markdown('<div class="bw-status green"><span class="bw-status-dot"></span>Passive income majority — strong foundation for wealth accumulation</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="bw-status yellow"><span class="bw-status-dot"></span>Moderately diversified — continue growing passive streams</div>', unsafe_allow_html=True)

        if not expense_df.empty:
            sorted_exp = expense_df.sort_values("amount", ascending=False).head(3)
            st.markdown('<p style="font-family:var(--font-disp);font-size:0.72rem;color:var(--cream-mute);margin:20px 0 8px;">Top Cost Drivers</p>', unsafe_allow_html=True)
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

allocation_modes = {
    "Balanced (Default)":  {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 10, "Charity": 5},
    "Wealth Acceleration": {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 5,  "Charity": 5},
    "Generosity Focus":    {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5,  "Emergency": 5,  "Lifestyle": 10, "Charity": 25},
    "Security First":      {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5,  "Charity": 5},
}

with st.expander("Allocation Planner"):
    if total_income == 0:
        st.info("Record income to unlock allocation planning.")
    elif net_surplus <= 0:
        st.warning("No surplus available. Reduce expenses to generate allocatable surplus.")
    else:
        mode = st.selectbox("Strategy", list(allocation_modes.keys()))
        allocation_list = [
            {"Category": cat, "Pct": pct, "Amount": round(net_surplus * pct / 100, 0)}
            for cat, pct in allocation_modes[mode].items()
        ]

        st.markdown('<p style="font-family:var(--font-disp);font-size:0.7rem;color:var(--cream-mute);margin:14px 0 10px;">Allocation Breakdown &nbsp;·&nbsp; Live calculation from current surplus</p>', unsafe_allow_html=True)

        alloc_rows = ""
        for r in allocation_list:
            alloc_rows += f"""
            <div class="bw-alloc-row">
                <span class="ar-cat">{r['Category']}</span>
                <span class="ar-pct">{r['Pct']}%</span>
                <span class="ar-amt">₦{r['Amount']:,.0f}</span>
            </div>"""
        st.markdown(f'<div class="bw-alloc-wrap">{alloc_rows}</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:var(--font-disp);font-size:0.67rem;color:var(--cream-mute);line-height:1.6;">Allocation updates automatically as income and expenses change. Lock the month below to permanently record this period.</p>', unsafe_allow_html=True)

# ====================== LOCK MONTH ======================
st.markdown('<span class="bw-section-label">Period Control</span>', unsafe_allow_html=True)

if month_locked:
    st.markdown(f'<div class="bw-lock-banner">🔒 &nbsp; {current_month_full} is permanently locked. All records are frozen and cannot be altered.</div>', unsafe_allow_html=True)
else:
    with st.expander(f"Lock {current_month_full}"):
        st.markdown(f"""
        <p style="font-family:var(--font-disp);font-size:0.8rem;color:var(--cream-dim);line-height:1.75;margin-bottom:18px;">
        Locking <strong style="color:var(--white);">{current_month_full}</strong> will permanently freeze all income, expense,
        and allocation records for this period. Once locked,
        <strong style="color:var(--gold);">no entries can be added, edited, or deleted.</strong>
        This action cannot be undone.
        </p>
        """, unsafe_allow_html=True)
        col_lock, col_space = st.columns([1, 2])
        with col_lock:
            if st.button(f"🔒 Lock {current_month_full}", key="lock_btn"):
                if lock_month(current_month):
                    st.success(f"{current_month_full} has been permanently locked.")
                    st.rerun()

# ====================== FOOTER ======================
st.markdown(f"""
<div class="bw-footer">
    Biverway Financial OS &nbsp;·&nbsp; Built on the Biverway Wealth System &nbsp;·&nbsp; {datetim
