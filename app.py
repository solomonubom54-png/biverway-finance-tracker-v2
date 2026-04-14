import streamlit as st
import pandas as pd
from datetime import datetime
from core.supabase_db import (
    client,
    add_income, load_income, delete_income, clear_income_month,
    add_expense, load_expense, delete_expense, clear_expense_month,
    is_month_locked, lock_month
)

st.set_page_config(page_title="Biverway Financial OS", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@300;400;500&display=swap');

:root {
    --bg-base:     #080a0e;
    --bg-card:     #0d1017;
    --bg-elevated: #131720;
    --bg-input:    #0c0f15;
    --gold:        #c9a84c;
    --gold-dim:    #9a7a34;
    --gold-glow:   rgba(201,168,76,0.07);
    --gold-line:   rgba(201,168,76,0.16);
    --cream:       #e8e0d0;
    --cream-dim:   rgba(232,224,208,0.5);
    --cream-mute:  rgba(232,224,208,0.22);
    --white:       #f0ece4;
    --green:       #4caf7d;
    --green-bg:    rgba(76,175,125,0.08);
    --red:         #c0544a;
    --red-bg:      rgba(192,84,74,0.08);
    --amber-warn:  #d4922a;
    --warn-bg:     rgba(212,146,42,0.08);
    --border-soft: rgba(255,255,255,0.055);
    --border-md:   rgba(255,255,255,0.08);
    --radius-sm:   8px;
    --radius:      12px;
    --font-disp:   'Sora', sans-serif;
    --font-mono:   'IBM Plex Mono', monospace;
}

html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
    background: var(--bg-base) !important;
    color: var(--cream) !important;
    font-family: var(--font-disp) !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
    background: var(--bg-base) !important;
    border-bottom: 1px solid var(--border-soft) !important;
}
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    max-width: 820px !important;
    margin: 0 auto !important;
}
.block-container { padding: 0 1.4rem 4rem !important; }
::-webkit-scrollbar { width: 3px; }
::-webkit-scrollbar-thumb { background: var(--gold-dim); border-radius: 3px; }

/* MASTHEAD */
.bw-masthead { padding: 32px 0 22px; border-bottom: 1px solid var(--gold-line); margin-bottom: 28px; }
.bw-masthead-label { font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold); margin-bottom: 10px; display: block; }
.bw-masthead h1 { font-family: var(--font-disp); font-size: 1.75rem; font-weight: 700; letter-spacing: -0.01em; color: var(--white); margin: 0 0 6px 0; line-height: 1.1; text-transform: uppercase; }
.bw-masthead-sub { font-size: 0.72rem; color: var(--cream-mute); font-weight: 300; letter-spacing: 0.04em; }

/* SECTION LABEL */
.bw-section-label { font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.24em; text-transform: uppercase; color: var(--gold); padding-bottom: 10px; margin: 28px 0 14px 0; border-bottom: 1px solid var(--gold-line); display: block; }

/* MONTH BADGE */
.bw-month { display: inline-flex; align-items: center; gap: 8px; background: var(--gold-glow); border: 1px solid var(--gold-line); color: var(--gold); font-family: var(--font-mono); font-size: 0.65rem; letter-spacing: 0.1em; text-transform: uppercase; padding: 5px 13px; border-radius: 100px; margin-bottom: 20px; }

/* KPI GRID */
.bw-kpi-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1px; background: var(--border-soft); border: 1px solid var(--border-md); border-radius: var(--radius); overflow: hidden; margin: 0 0 20px 0; }
.bw-kpi { background: var(--bg-card); padding: 16px 12px 14px; display: flex; flex-direction: column; justify-content: space-between; min-height: 82px; }
.bw-kpi.highlight { background: linear-gradient(160deg, #0d1017 55%, rgba(201,168,76,0.05) 100%); }
.bw-kpi .kpi-label { font-family: var(--font-mono); font-size: 0.48rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--cream-mute); margin-bottom: 8px; display: block; line-height: 1.6; }
.bw-kpi .kpi-value { font-family: var(--font-mono); font-size: 0.82rem; font-weight: 500; color: var(--white); line-height: 1; display: block; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.bw-kpi.highlight .kpi-value { font-size: 0.88rem; font-weight: 600; }
.bw-kpi .kpi-value.positive { color: var(--green); }
.bw-kpi .kpi-value.negative { color: var(--red); }

/* STATUS */
.bw-status { display: inline-flex; align-items: flex-start; gap: 9px; padding: 10px 14px; border-radius: var(--radius-sm); font-family: var(--font-mono); font-size: 0.68rem; margin-top: 4px; line-height: 1.5; }
.bw-status.green  { background: var(--green-bg); color: var(--green); border: 1px solid rgba(76,175,125,0.15); }
.bw-status.yellow { background: var(--warn-bg); color: var(--amber-warn); border: 1px solid rgba(212,146,42,0.15); }
.bw-status.red    { background: var(--red-bg); color: var(--red); border: 1px solid rgba(192,84,74,0.15); }
.bw-status-dot { width: 5px; height: 5px; border-radius: 50%; background: currentColor; display: inline-block; flex-shrink: 0; margin-top: 5px; }

/* INSIGHT ROW */
.bw-insight-row { display: flex; justify-content: space-between; align-items: baseline; padding: 11px 0; border-bottom: 1px solid var(--border-soft); }
.bw-insight-row:last-child { border-bottom: none; }
.bw-insight-row .ir-label { font-size: 0.78rem; color: var(--cream-dim); font-weight: 400; }
.bw-insight-row .ir-value { font-family: var(--font-mono); font-size: 0.88rem; font-weight: 500; color: var(--white); }
.bw-insight-row .ir-sub { font-size: 0.62rem; color: var(--cream-mute); margin-left: 7px; }

/* PROGRESS BAR */
.bw-bar-wrap { width: 100%; height: 1px; background: var(--border-md); border-radius: 1px; margin-top: 6px; overflow: hidden; }
.bw-bar-fill { height: 100%; background: linear-gradient(90deg, var(--gold-dim), var(--gold)); border-radius: 1px; }

/* RECORD ROWS */
.bw-record-table { border: 1px solid var(--border-md); border-radius: var(--radius-sm); overflow: hidden; margin-bottom: 16px; }
.bw-record-row { display: flex; justify-content: space-between; align-items: center; padding: 13px 16px; border-bottom: 1px solid var(--border-soft); background: var(--bg-card); }
.bw-record-row:last-child { border-bottom: none; }
.bw-record-row .rr-left { display: flex; flex-direction: column; gap: 3px; }
.bw-record-row .rr-source { font-size: 0.82rem; font-weight: 500; color: var(--white); }
.bw-record-row .rr-meta { font-size: 0.63rem; color: var(--cream-mute); font-family: var(--font-mono); letter-spacing: 0.04em; }
.bw-record-row .rr-amount { font-family: var(--font-mono); font-size: 0.92rem; font-weight: 500; color: var(--white); }

/* EMPTY STATE */
.bw-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 28px 20px; border: 1px solid var(--border-soft); border-radius: var(--radius-sm); background: var(--bg-card); margin-bottom: 16px; gap: 7px; }
.bw-empty-icon { font-size: 1.1rem; opacity: 0.25; }
.bw-empty-text { font-family: var(--font-mono); font-size: 0.62rem; letter-spacing: 0.08em; color: var(--cream-mute); text-transform: uppercase; }
.bw-empty-sub { font-family: var(--font-disp); font-size: 0.67rem; color: var(--cream-mute); opacity: 0.6; }

/* ALLOC ROWS */
.bw-alloc-wrap { border: 1px solid var(--border-md); border-radius: var(--radius-sm); overflow: hidden; margin: 14px 0 10px; }
.bw-alloc-row { display: flex; align-items: center; padding: 12px 16px; border-bottom: 1px solid var(--border-soft); background: var(--bg-card); }
.bw-alloc-row:last-child { border-bottom: none; }
.bw-alloc-row .ar-cat { flex: 1; font-size: 0.8rem; color: var(--cream-dim); }
.bw-alloc-row .ar-pct { font-family: var(--font-mono); font-size: 0.63rem; color: var(--gold); letter-spacing: 0.05em; width: 38px; text-align: center; }
.bw-alloc-row .ar-amt { font-family: var(--font-mono); font-size: 0.85rem; font-weight: 500; color: var(--white); text-align: right; min-width: 96px; }

/* ALLOC TOTAL BADGE */
.bw-alloc-total { display: flex; align-items: center; justify-content: space-between; padding: 9px 14px; border: 1px solid rgba(76,175,125,0.15); border-radius: var(--radius-sm); background: var(--green-bg); margin-bottom: 10px; }
.bw-alloc-total .at-label { font-family: var(--font-mono); font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase; color: var(--green); }
.bw-alloc-total .at-check { font-family: var(--font-mono); font-size: 0.68rem; font-weight: 600; color: var(--green); }

/* LOCK BANNER */
.bw-lock-banner { background: rgba(201,168,76,0.04); border: 1px solid var(--gold-line); border-radius: var(--radius-sm); padding: 11px 16px; margin-bottom: 16px; font-family: var(--font-mono); font-size: 0.65rem; color: var(--gold); display: flex; align-items: center; gap: 10px; }

/* CONFIRM BOX */
.bw-confirm { background: var(--bg-elevated); border: 1px solid var(--gold-line); border-radius: var(--radius-sm); padding: 14px 16px; margin: 10px 0; }
.bw-confirm p { font-family: var(--font-disp); font-size: 0.78rem; color: var(--cream-dim); margin: 0 0 12px 0; line-height: 1.5; }
.bw-confirm strong { color: var(--white); }

/* EDIT FORM */
.bw-edit-wrap { background: var(--bg-elevated); border: 1px solid var(--gold-line); border-radius: var(--radius-sm); padding: 16px; margin: 8px 0 12px; }
.bw-edit-title { font-family: var(--font-mono); font-size: 0.58rem; letter-spacing: 0.18em; text-transform: uppercase; color: var(--gold); margin-bottom: 14px; display: block; }

/* USER BAR */
.bw-userbar { padding: 10px 0 18px; border-bottom: 1px solid var(--border-soft); margin-bottom: 4px; }
.bw-ub-email { font-family: var(--font-mono); font-size: 0.63rem; color: var(--cream-mute); letter-spacing: 0.05em; display: flex; align-items: center; gap: 8px; }
.bw-ub-dot { width: 6px; height: 6px; border-radius: 50%; background: var(--green); display: inline-block; flex-shrink: 0; }

/* FOOTER */
.bw-footer { text-align: center; font-family: var(--font-mono); font-size: 0.55rem; letter-spacing: 0.2em; text-transform: uppercase; color: var(--cream-mute); margin-top: 48px; padding-top: 20px; border-top: 1px solid var(--border-soft); }

/* ═══════════════════════════════════
   WIDGET OVERRIDES
   ═══════════════════════════════════ */

[data-testid="stWidgetLabel"] p,
[data-baseweb="form-control-label"] {
    font-family: var(--font-disp) !important;
    font-size: 0.67rem !important;
    color: var(--cream-mute) !important;
    font-weight: 400 !important;
    margin-bottom: 6px !important;
}

[data-baseweb="input"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: none !important;
}
[data-baseweb="input"] input {
    background: transparent !important;
    color: var(--white) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.86rem !important;
    padding: 11px 14px !important;
}
[data-baseweb="input"]:focus-within > div {
    border-color: rgba(201,168,76,0.22) !important;
    box-shadow: none !important;
}

[data-baseweb="textarea"] textarea {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--cream-dim) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.81rem !important;
    padding: 11px 14px !important;
    box-shadow: none !important;
}

[data-testid="stNumberInput"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: none !important;
}
[data-testid="stNumberInput"] input {
    background: transparent !important;
    color: var(--white) !important;
    font-family: var(--font-mono) !important;
    font-size: 0.92rem !important;
}
[data-testid="stNumberInput"] button {
    background: transparent !important;
    border: none !important;
    color: rgba(232,224,208,0.15) !important;
}
[data-testid="stNumberInput"] button:hover {
    color: var(--gold) !important;
    background: var(--gold-glow) !important;
}

/* ── SELECT TRIGGER — all dropdowns ── */
[data-baseweb="select"] > div {
    background: var(--bg-input) !important;
    border: 1px solid var(--border-soft) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: none !important;
    min-height: 42px !important;
}
[data-baseweb="select"] > div > div {
    padding: 8px 12px !important;
}
[data-baseweb="select"] > div > div > div,
[data-baseweb="select"] > div span {
    color: var(--white) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.8rem !important;
    font-weight: 400 !important;
    white-space: normal !important;
    line-height: 1.4 !important;
}
[data-baseweb="select"] svg { color: rgba(232,224,208,0.25) !important; width: 14px !important; }

/* ── REMOVE / ACTION SELECTBOX — quieter, smaller ── */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
    min-height: 36px !important;
    padding: 0 !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div {
    padding: 6px 10px !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div > div > div,
[data-testid="stSelectbox"] [data-baseweb="select"] > div span {
    font-size: 0.72rem !important;
    color: rgba(232,224,208,0.45) !important;
}

/* ── DROPDOWN LIST — dark ── */
[data-baseweb="popover"],
[data-baseweb="menu"],
ul[role="listbox"],
[role="listbox"] {
    background: #0a0d13 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 16px 48px rgba(0,0,0,0.75), 0 2px 8px rgba(0,0,0,0.5) !important;
}
[role="option"] {
    background: transparent !important;
    color: rgba(232,224,208,0.7) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.78rem !important;
    font-weight: 400 !important;
    padding: 10px 14px !important;
    border-bottom: 1px solid rgba(255,255,255,0.04) !important;
    cursor: pointer !important;
    white-space: normal !important;
    line-height: 1.4 !important;
    transition: background 0.12s, color 0.12s !important;
}
[role="option"]:last-child { border-bottom: none !important; }
[role="option"]:hover {
    background: rgba(255,255,255,0.04) !important;
    color: var(--white) !important;
}
[aria-selected="true"],
[role="option"][aria-selected="true"] {
    background: rgba(201,168,76,0.07) !important;
    color: var(--gold) !important;
    font-weight: 500 !important;
}

/* ── PRIMARY BUTTON — gold ── */
[data-testid="stFormSubmitButton"] button {
    background: var(--gold) !important;
    color: #080a0e !important;
    border: none !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.76rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    padding: 12px 24px !important;
    width: 100% !important;
    margin-top: 10px !important;
    transition: background 0.18s, transform 0.1s !important;
}
[data-testid="stFormSubmitButton"] button:hover {
    background: #d4b460 !important;
    transform: translateY(-1px) !important;
}

/* ── SECONDARY BUTTONS — quiet, unobtrusive ── */
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    color: rgba(232,224,208,0.4) !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: var(--radius-sm) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.62rem !important;
    font-weight: 400 !important;
    padding: 5px 10px !important;
    transition: all 0.15s !important;
    box-shadow: none !important;
}
[data-testid="baseButton-secondary"]:hover {
    background: rgba(255,255,255,0.03) !important;
    border-color: rgba(201,168,42,0.2) !important;
    color: rgba(232,224,208,0.7) !important;
}

/* ── EXPANDERS ── */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-md) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 8px !important;
    overflow: hidden !important;
}
[data-testid="stExpander"] > details > summary {
    background: var(--bg-elevated) !important;
    font-family: var(--font-disp) !important;
    font-size: 0.76rem !important;
    font-weight: 500 !important;
    color: var(--cream-dim) !important;
    padding: 12px 18px !important;
    border-bottom: 1px solid var(--border-soft) !important;
    list-style: none !important;
}
[data-testid="stExpander"] > details[open] > summary { color: var(--gold) !important; border-bottom-color: var(--gold-line) !important; }
[data-testid="stExpander"] > details > summary:hover { color: var(--gold) !important; }
[data-testid="stExpanderToggleIcon"] { color: rgba(201,168,76,0.45) !important; }
[data-testid="stExpander"] > details > div { padding: 18px 18px 20px !important; background: var(--bg-card) !important; }

/* ── TABS ── */
[data-testid="stTabs"] [role="tablist"] { border-bottom: 1px solid var(--border-md) !important; background: transparent !important; }
[data-testid="stTabs"] [role="tab"] { font-family: var(--font-disp) !important; font-size: 0.73rem !important; font-weight: 400 !important; color: var(--cream-mute) !important; padding: 10px 20px !important; border-radius: 0 !important; border-bottom: 2px solid transparent !important; background: transparent !important; }
[data-testid="stTabs"] [role="tab"][aria-selected="true"] { color: var(--gold) !important; border-bottom-color: var(--gold) !important; }

/* ── ALERTS ── */
[data-testid="stAlert"] { border-radius: var(--radius-sm) !important; font-family: var(--font-disp) !important; font-size: 0.74rem !important; border-left-width: 2px !important; }
[data-testid="stNotificationContentInfo"]    { background: rgba(232,224,208,0.03) !important; border-left-color: var(--cream-mute) !important; }
[data-testid="stNotificationContentSuccess"] { background: var(--green-bg) !important; border-left-color: var(--green) !important; }
[data-testid="stNotificationContentWarning"] { background: var(--warn-bg) !important; border-left-color: var(--amber-warn) !important; }
[data-testid="stNotificationContentError"]   { background: var(--red-bg) !important; border-left-color: var(--red) !important; }

[data-testid="stHorizontalBlock"] { gap: 10px !important; }
#MainMenu, footer, [data-testid="stStatusWidget"] { visibility: hidden !important; }
hr { border-color: var(--border-soft) !important; margin: 20px 0 !important; }
</style>
""", unsafe_allow_html=True)

# ====================== HELPERS ======================
def fmt_amount(amount, compact=False):
    """Format naira amounts. Compact mode for KPI cards (₦5.0M), full for records."""
    if compact:
        if abs(amount) >= 1_000_000:
            return f"&#8358;{amount/1_000_000:.1f}M"
        elif abs(amount) >= 1_000:
            return f"&#8358;{amount/1_000:.0f}K"
        else:
            return f"&#8358;{amount:,.0f}"
    return f"&#8358;{amount:,.0f}"

def full_month(dt):  return dt.strftime("%B %Y")
def short_month(dt): return dt.strftime("%b %Y")

MONTHS = ["January","February","March","April","May","June",
          "July","August","September","October","November","December"]

# ====================== SESSION STATE ======================
if "supabase_session"    not in st.session_state: st.session_state.supabase_session    = None
if "income_form_key"     not in st.session_state: st.session_state.income_form_key     = 0
if "expense_form_key"    not in st.session_state: st.session_state.expense_form_key    = 0
if "show_reset"          not in st.session_state: st.session_state.show_reset          = False
if "confirm_del_income"  not in st.session_state: st.session_state.confirm_del_income  = None
if "confirm_del_expense" not in st.session_state: st.session_state.confirm_del_expense = None
if "edit_income_id"      not in st.session_state: st.session_state.edit_income_id      = None
if "edit_expense_id"     not in st.session_state: st.session_state.edit_expense_id     = None
if "working_month_idx"   not in st.session_state: st.session_state.working_month_idx   = datetime.today().month - 1
if "working_year"        not in st.session_state: st.session_state.working_year        = datetime.today().year

# ====================== MASTHEAD ======================
st.markdown("""
<div class="bw-masthead">
    <span class="bw-masthead-label">Biverway &nbsp;&middot;&nbsp; Private Finance</span>
    <h1>Biverway Financial OS</h1>
    <div class="bw-masthead-sub">Your personal wealth command center</div>
</div>
""", unsafe_allow_html=True)

# ====================== AUTH ======================
if st.session_state.supabase_session is None:

    if st.session_state.show_reset:
        st.markdown('<span class="bw-section-label">Password Reset</span>', unsafe_allow_html=True)
        with st.form("reset_form"):
            reset_email  = st.text_input("Email address")
            submit_reset = st.form_submit_button("Send Reset Link")
        if submit_reset:
            try:
                client.auth.reset_password_email(reset_email, options={"redirect_to": "https://biverway-finance-tracker-v2-3weeiriwgi5sqcczk3uuxd.streamlit.app"})
                st.success("Reset link sent — check your inbox.")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        if st.button("Back to Sign In"):
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
                if "invalid" in err or "credentials" in err: st.error("Incorrect email or password.")
                elif "email not confirmed" in err: st.warning("Please confirm your email before signing in.")
                else: st.error(f"Sign in failed: {e}")
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
                if "already registered" in err or "already exists" in err: st.error("This email is already registered.")
                elif "rate limit" in err: st.warning("Too many attempts. Please wait a few minutes.")
                else: st.error(f"Registration failed: {e}")
        st.markdown('<p style="font-family:var(--font-disp);font-size:0.67rem;color:var(--cream-mute);margin-top:12px;line-height:1.7;">After registering, confirm your email before signing in.</p>', unsafe_allow_html=True)

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

# ====================== WORKING PERIOD — Month/Year Dropdowns ======================
st.markdown('<span class="bw-section-label">Working Period</span>', unsafe_allow_html=True)

col_m, col_y = st.columns([2, 1])
with col_m:
    selected_month_name = st.selectbox(
        "Month",
        options=MONTHS,
        index=st.session_state.working_month_idx,
        key="month_select"
    )
with col_y:
    current_year = datetime.today().year
    year_options = list(range(current_year - 3, current_year + 2))
    selected_year = st.selectbox(
        "Year",
        options=year_options,
        index=year_options.index(st.session_state.working_year) if st.session_state.working_year in year_options else len(year_options) - 2,
        key="year_select"
    )

st.session_state.working_month_idx = MONTHS.index(selected_month_name)
st.session_state.working_year      = selected_year

current_month      = f"{selected_month_name[:3]} {selected_year}"   # e.g. "Mar 2026"
current_month_full = f"{selected_month_name} {selected_year}"       # e.g. "March 2026"

st.markdown(f'<div class="bw-month">&#9658;&nbsp;{current_month_full}</div>', unsafe_allow_html=True)

month_locked = is_month_locked(current_month)
if month_locked:
    st.markdown(f'<div class="bw-lock-banner">&#128274;&nbsp;{current_month_full} is locked &mdash; all records are permanently frozen</div>', unsafe_allow_html=True)

# ====================== LOAD DATA ======================
income_records  = load_income(current_month)
expense_records = load_expense(current_month)
income_df  = pd.DataFrame(income_records)  if income_records  else pd.DataFrame()
expense_df = pd.DataFrame(expense_records) if expense_records else pd.DataFrame()
if not income_df.empty:  income_df["amount"]  = pd.to_numeric(income_df["amount"],  errors="coerce").fillna(0)
if not expense_df.empty: expense_df["amount"] = pd.to_numeric(expense_df["amount"], errors="coerce").fillna(0)

# ====================== INCOME ======================
st.markdown('<span class="bw-section-label">Income</span>', unsafe_allow_html=True)

income_type_map = {
    "Skill":               "Active",
    "Salary":              "Active",
    "Business":            "Passive",
    "Dividend / Interest": "Passive",
    "Rental":              "Passive"
}

if not month_locked:
    with st.expander("Add Income"):
        with st.form(f"income_form_{st.session_state.income_form_key}"):
            col_a, col_b = st.columns(2)
            with col_a: income_source = st.selectbox("Source", list(income_type_map.keys()))
            with col_b: amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
            notes = st.text_area("Notes", height=70, placeholder="Optional context...")
            submit_income = st.form_submit_button("Record Income")
        if submit_income:
            with st.spinner("Recording..."):
                add_income(current_month, income_source, income_type_map[income_source], amount, notes)
            st.success("Income recorded.")
            st.session_state.income_form_key += 1
            st.rerun()

if not income_df.empty:
    rows_html = ""
    for _, row in income_df.iterrows():
        rows_html += (
            f'<div class="bw-record-row">'
            f'<div class="rr-left">'
            f'<span class="rr-source">{row["source"]}</span>'
            f'<span class="rr-meta">{row["income_type"]} &nbsp;&middot;&nbsp; {row.get("notes","") or "&mdash;"}</span>'
            f'</div>'
            f'<span class="rr-amount">&#8358;{float(row["amount"]):,.0f}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="bw-record-table">{rows_html}</div>', unsafe_allow_html=True)

    if not month_locked:
        inc_map = {}
        for idx, rec in enumerate(income_records):
            amt   = float(rec.get("amount", 0))
            label = f"{idx + 1}. {rec['source']} \u2014 \u20a6{amt:,.0f}"
            inc_map[label] = rec

        # ── EDIT INCOME ──
        if st.session_state.edit_income_id is not None:
            edit_rec = next((r for r in income_records if r["id"] == st.session_state.edit_income_id), None)
            if edit_rec:
                st.markdown('<div class="bw-edit-wrap"><span class="bw-edit-title">Edit Income Entry</span></div>', unsafe_allow_html=True)
                with st.form("edit_income_form"):
                    col_ea, col_eb = st.columns(2)
                    src_keys = list(income_type_map.keys())
                    cur_src  = edit_rec.get("source", src_keys[0])
                    src_idx  = src_keys.index(cur_src) if cur_src in src_keys else 0
                    with col_ea: new_source = st.selectbox("Source", src_keys, index=src_idx)
                    with col_eb: new_amount = st.number_input("Amount", min_value=0.0, step=1000.0, value=float(edit_rec.get("amount", 0)), format="%0.0f")
                    new_notes  = st.text_area("Notes", value=edit_rec.get("notes", "") or "", height=70)
                    col_sv, col_cx = st.columns([1, 1])
                    with col_sv: save_edit = st.form_submit_button("Save Changes")
                    with col_cx: cancel_edit = st.form_submit_button("Cancel")
                if save_edit:
                    with st.spinner("Saving..."):
                        delete_income(edit_rec["id"])
                        add_income(current_month, new_source, income_type_map[new_source], new_amount, new_notes)
                    st.session_state.edit_income_id = None
                    st.success("Income updated.")
                    st.rerun()
                if cancel_edit:
                    st.session_state.edit_income_id = None
                    st.rerun()

        elif st.session_state.confirm_del_income is None:
            col_sel, col_edit, col_del, col_clr = st.columns([3, 1, 1, 1])
            with col_sel:
                selected_inc = st.selectbox("Select entry", options=list(inc_map.keys()), key="del_inc_select", label_visibility="collapsed")
            with col_edit:
                if st.button("Edit", key="edit_inc_btn"):
                    st.session_state.edit_income_id = inc_map[selected_inc]["id"]
                    st.rerun()
            with col_del:
                if st.button("Remove", key="del_inc_btn"):
                    st.session_state.confirm_del_income = selected_inc
                    st.rerun()
            with col_clr:
                if st.button("Clear", key="clr_inc"):
                    with st.spinner("Clearing..."):
                        clear_income_month(current_month)
                    st.rerun()
        else:
            entry = st.session_state.confirm_del_income
            st.markdown(f'<div class="bw-confirm"><p>Remove <strong>{entry}</strong>?<br><span style="font-size:0.7rem;color:var(--cream-mute);">This cannot be undone.</span></p></div>', unsafe_allow_html=True)
            col_yes, col_no = st.columns([1, 1])
            with col_yes:
                if st.button("Yes, Remove", key="confirm_inc_yes"):
                    with st.spinner("Removing..."):
                        delete_income(inc_map[entry]["id"])
                    st.session_state.confirm_del_income = None
                    st.rerun()
            with col_no:
                if st.button("Cancel", key="confirm_inc_no"):
                    st.session_state.confirm_del_income = None
                    st.rerun()
else:
    st.markdown("""
    <div class="bw-empty">
        <span class="bw-empty-icon">&#8358;</span>
        <span class="bw-empty-text">No income recorded</span>
        <span class="bw-empty-sub">Add your first income entry for this period</span>
    </div>
    """, unsafe_allow_html=True)

# ====================== EXPENSES ======================
st.markdown('<span class="bw-section-label">Expenses</span>', unsafe_allow_html=True)

expense_categories = ["Rent", "Food", "Utilities", "Transport", "Healthcare", "Education", "Subscription", "Family Support"]

if not month_locked:
    with st.expander("Add Expense"):
        with st.form(f"expense_form_{st.session_state.expense_form_key}"):
            col_c, col_d = st.columns(2)
            with col_c: category = st.selectbox("Category", expense_categories)
            with col_d: expense_amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
            description = st.text_area("Description", height=70, placeholder="Optional context...")
            submit_expense = st.form_submit_button("Record Expense")
        if submit_expense:
            with st.spinner("Recording..."):
                add_expense(current_month, category, expense_amount, description)
            st.success("Expense recorded.")
            st.session_state.expense_form_key += 1
            st.rerun()

if not expense_df.empty:
    total_expense_display = expense_df["amount"].sum()
    rows_html2 = ""
    for _, row in expense_df.iterrows():
        share = f"{row['amount']/total_expense_display*100:.0f}%" if total_expense_display > 0 else "0%"
        rows_html2 += (
            f'<div class="bw-record-row">'
            f'<div class="rr-left">'
            f'<span class="rr-source">{row["category"]}</span>'
            f'<span class="rr-meta">{share} of total &nbsp;&middot;&nbsp; {row.get("description","") or "&mdash;"}</span>'
            f'</div>'
            f'<span class="rr-amount">&#8358;{float(row["amount"]):,.0f}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="bw-record-table">{rows_html2}</div>', unsafe_allow_html=True)

    if not month_locked:
        exp_map = {}
        for idx, rec in enumerate(expense_records):
            amt   = float(rec.get("amount", 0))
            label = f"{idx + 1}. {rec['category']} \u2014 \u20a6{amt:,.0f}"
            exp_map[label] = rec

        # ── EDIT EXPENSE ──
        if st.session_state.edit_expense_id is not None:
            edit_exp = next((r for r in expense_records if r["id"] == st.session_state.edit_expense_id), None)
            if edit_exp:
                st.markdown('<div class="bw-edit-wrap"><span class="bw-edit-title">Edit Expense Entry</span></div>', unsafe_allow_html=True)
                with st.form("edit_expense_form"):
                    col_ec, col_ed = st.columns(2)
                    cur_cat = edit_exp.get("category", expense_categories[0])
                    cat_idx = expense_categories.index(cur_cat) if cur_cat in expense_categories else 0
                    with col_ec: new_category = st.selectbox("Category", expense_categories, index=cat_idx)
                    with col_ed: new_exp_amount = st.number_input("Amount", min_value=0.0, step=1000.0, value=float(edit_exp.get("amount", 0)), format="%0.0f")
                    new_desc   = st.text_area("Description", value=edit_exp.get("description", "") or "", height=70)
                    col_sv2, col_cx2 = st.columns([1, 1])
                    with col_sv2: save_exp_edit = st.form_submit_button("Save Changes")
                    with col_cx2: cancel_exp_edit = st.form_submit_button("Cancel")
                if save_exp_edit:
                    with st.spinner("Saving..."):
                        delete_expense(edit_exp["id"])
                        add_expense(current_month, new_category, new_exp_amount, new_desc)
                    st.session_state.edit_expense_id = None
                    st.success("Expense updated.")
                    st.rerun()
                if cancel_exp_edit:
                    st.session_state.edit_expense_id = None
                    st.rerun()

        elif st.session_state.confirm_del_expense is None:
            col_sel2, col_edit2, col_del2, col_clr2 = st.columns([3, 1, 1, 1])
            with col_sel2:
                selected_exp = st.selectbox("Select entry", options=list(exp_map.keys()), key="del_exp_select", label_visibility="collapsed")
            with col_edit2:
                if st.button("Edit", key="edit_exp_btn"):
                    st.session_state.edit_expense_id = exp_map[selected_exp]["id"]
                    st.rerun()
            with col_del2:
                if st.button("Remove", key="del_exp_btn"):
                    st.session_state.confirm_del_expense = selected_exp
                    st.rerun()
            with col_clr2:
                if st.button("Clear", key="clr_exp"):
                    with st.spinner("Clearing..."):
                        clear_expense_month(current_month)
                    st.rerun()
        else:
            entry = st.session_state.confirm_del_expense
            st.markdown(f'<div class="bw-confirm"><p>Remove <strong>{entry}</strong>?<br><span style="font-size:0.7rem;color:var(--cream-mute);">This cannot be undone.</span></p></div>', unsafe_allow_html=True)
            col_yes2, col_no2 = st.columns([1, 1])
            with col_yes2:
                if st.button("Yes, Remove", key="confirm_exp_yes"):
                    with st.spinner("Removing..."):
                        delete_expense(exp_map[entry]["id"])
                    st.session_state.confirm_del_expense = None
                    st.rerun()
            with col_no2:
                if st.button("Cancel", key="confirm_exp_no"):
                    st.session_state.confirm_del_expense = None
                    st.rerun()
else:
    st.markdown("""
    <div class="bw-empty">
        <span class="bw-empty-icon">&#8599;</span>
        <span class="bw-empty-text">No expenses recorded</span>
        <span class="bw-empty-sub">Add your first expense entry for this period</span>
    </div>
    """, unsafe_allow_html=True)

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
        <span class="kpi-value">{fmt_amount(total_income, compact=True)}</span>
    </div>
    <div class="bw-kpi">
        <span class="kpi-label">Total<br>Expenses</span>
        <span class="kpi-value">{fmt_amount(total_expense, compact=True)}</span>
    </div>
    <div class="bw-kpi highlight">
        <span class="kpi-label">Net<br>Surplus</span>
        <span class="kpi-value {surplus_cls}">{fmt_amount(net_surplus, compact=True)}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Auto-expand performance analysis when data exists
has_data = total_income > 0
with st.expander("Performance Analysis", expanded=has_data):
    if total_income == 0:
        st.markdown("""
        <div class="bw-empty">
            <span class="bw-empty-icon">&#9782;</span>
            <span class="bw-empty-text">No data to analyse</span>
            <span class="bw-empty-sub">Record income to unlock performance insights</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        if savings_rate >= 30:   s_cls, s_txt = "green",  f"Savings rate {savings_rate:.1f}% \u2014 strong surplus discipline"
        elif savings_rate >= 15: s_cls, s_txt = "yellow", f"Savings rate {savings_rate:.1f}% \u2014 stable, room to optimise"
        elif savings_rate >= 1:  s_cls, s_txt = "yellow", f"Savings rate {savings_rate:.1f}% \u2014 margin is thin"
        else:                    s_cls, s_txt = "red",    f"Deficit \u2014 expenses exceed income by \u20a6{abs(net_surplus):,.0f}"
        st.markdown(f'<div class="bw-status {s_cls}"><span class="bw-status-dot"></span>{s_txt}</div>', unsafe_allow_html=True)

        bar_pct = min(max(savings_rate, 0), 100)
        st.markdown(f"""
        <div style="margin:18px 0 22px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:7px;">
                <span style="font-family:var(--font-disp);font-size:0.7rem;color:var(--cream-mute);">Savings Rate</span>
                <span style="font-family:var(--font-mono);font-size:0.67rem;color:var(--gold);">{savings_rate:.1f}%</span>
            </div>
            <div class="bw-bar-wrap"><div class="bw-bar-fill" style="width:{bar_pct}%"></div></div>
        </div>
        """, unsafe_allow_html=True)

        if not income_df.empty:
            active_income  = income_df[income_df["income_type"] == "Active"]["amount"].sum()
            passive_income = income_df[income_df["income_type"] == "Passive"]["amount"].sum()
            active_pct     = (active_income  / total_income * 100) if total_income else 0
            passive_pct    = (passive_income / total_income * 100) if total_income else 0
            st.markdown('<p style="font-family:var(--font-disp);font-size:0.7rem;color:var(--cream-mute);margin:18px 0 8px;">Income Structure</p>', unsafe_allow_html=True)
            st.markdown(f"""
            <div>
                <div class="bw-insight-row">
                    <span class="ir-label">Active Income</span>
                    <span class="ir-value">&#8358;{active_income:,.0f}<span class="ir-sub">{active_pct:.0f}%</span></span>
                </div>
                <div class="bw-insight-row">
                    <span class="ir-label">Passive Income</span>
                    <span class="ir-value">&#8358;{passive_income:,.0f}<span class="ir-sub">{passive_pct:.0f}%</span></span>
                </div>
            </div>
            <div style="margin:14px 0 18px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:7px;">
                    <span style="font-family:var(--font-disp);font-size:0.7rem;color:var(--cream-mute);">Passive Income Share</span>
                    <span style="font-family:var(--font-mono);font-size:0.67rem;color:var(--gold);">{passive_pct:.0f}%</span>
                </div>
                <div class="bw-bar-wrap"><div class="bw-bar-fill" style="width:{passive_pct}%"></div></div>
            </div>
            """, unsafe_allow_html=True)
            if active_pct >= 70:
                st.markdown('<div class="bw-status yellow"><span class="bw-status-dot"></span>Income heavily effort-dependent \u2014 grow passive streams</div>', unsafe_allow_html=True)
            elif passive_pct >= 50:
                st.markdown('<div class="bw-status green"><span class="bw-status-dot"></span>Passive income majority \u2014 strong foundation for wealth accumulation</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="bw-status yellow"><span class="bw-status-dot"></span>Moderately diversified \u2014 continue growing passive streams</div>', unsafe_allow_html=True)

        if not expense_df.empty:
            sorted_exp = expense_df.sort_values("amount", ascending=False).head(3)
            st.markdown('<p style="font-family:var(--font-disp);font-size:0.7rem;color:var(--cream-mute);margin:20px 0 8px;">Top Cost Drivers</p>', unsafe_allow_html=True)
            rows = "".join(
                f'<div class="bw-insight-row">'
                f'<span class="ir-label">{row["category"]}</span>'
                f'<span class="ir-value">&#8358;{row["amount"]:,.0f}<span class="ir-sub">{row["amount"]/total_expense*100:.0f}%</span></span>'
                f'</div>'
                for _, row in sorted_exp.iterrows()
            )
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
        st.markdown("""
        <div class="bw-empty">
            <span class="bw-empty-icon">&#9736;</span>
            <span class="bw-empty-text">No surplus to allocate</span>
            <span class="bw-empty-sub">Record income to unlock allocation planning</span>
        </div>
        """, unsafe_allow_html=True)
    elif net_surplus <= 0:
        st.markdown("""
        <div class="bw-empty" style="border-color:rgba(192,84,74,0.15);background:var(--red-bg);">
            <span class="bw-empty-icon" style="color:var(--red);">&#9650;</span>
            <span class="bw-empty-text" style="color:var(--red);">No surplus available</span>
            <span class="bw-empty-sub">Reduce expenses to generate allocatable surplus</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        mode = st.selectbox("Strategy", list(allocation_modes.keys()))
        allocation_list = [
            {"Category": cat, "Pct": pct, "Amount": round(net_surplus * pct / 100, 0)}
            for cat, pct in allocation_modes[mode].items()
        ]
        total_pct = sum(r["Pct"] for r in allocation_list)

        # 100% allocated badge
        st.markdown(f"""
        <div class="bw-alloc-total">
            <span class="at-label">Allocation Status</span>
            <span class="at-check">&#10003;&nbsp;{total_pct}% allocated</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('<p style="font-family:var(--font-disp);font-size:0.68rem;color:var(--cream-mute);margin:10px 0 10px;">Live allocation from current surplus</p>', unsafe_allow_html=True)
        alloc_rows = "".join(
            f'<div class="bw-alloc-row">'
            f'<span class="ar-cat">{r["Category"]}</span>'
            f'<span class="ar-pct">{r["Pct"]}%</span>'
            f'<span class="ar-amt">&#8358;{r["Amount"]:,.0f}</span>'
            f'</div>'
            for r in allocation_list
        )
        st.markdown(f'<div class="bw-alloc-wrap">{alloc_rows}</div>', unsafe_allow_html=True)
        st.markdown('<p style="font-family:var(--font-disp);font-size:0.65rem;color:var(--cream-mute);line-height:1.6;">Updates automatically as records change. Lock the month below to permanently freeze this period.</p>', unsafe_allow_html=True)

# ====================== LOCK MONTH ======================
st.markdown('<span class="bw-section-label">Period Control</span>', unsafe_allow_html=True)

if month_locked:
    st.markdown(f'<div class="bw-lock-banner">&#128274;&nbsp;{current_month_full} is permanently locked. All records are frozen.</div>', unsafe_allow_html=True)
else:
    with st.expander(f"Lock {current_month_full}"):
        st.markdown(f'<p style="font-family:var(--font-disp);font-size:0.78rem;color:var(--cream-dim);line-height:1.75;margin-bottom:18px;">Locking <strong style="color:var(--white);">{current_month_full}</strong> will permanently freeze all records for this period. Once locked, <strong style="color:var(--gold);">no entries can be added, edited, or deleted.</strong> This action cannot be undone.</p>', unsafe_allow_html=True)
        col_lock, col_space = st.columns([1, 2])
        with col_lock:
            if st.button(f"Lock {current_month_full}", key="lock_btn"):
                with st.spinner("Locking period..."):
                    if lock_month(current_month):
                        st.success(f"{current_month_full} has been permanently locked.")
                        st.rerun()

# ====================== FOOTER ======================
year = datetime.today().year
st.markdown(f'<div class="bw-footer">Biverway Financial OS &nbsp;&middot;&nbsp; Built on the Biverway Wealth System &nbsp;&middot;&nbsp; {year}</div>', unsafe_allow_html=True)
