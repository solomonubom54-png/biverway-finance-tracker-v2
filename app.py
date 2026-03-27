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
    --bg-base:#080a0e;
    --bg-card:#0d1017;
    --bg-elevated:#131720;
    --bg-input:#0f1318;
    --gold:#c9a84c;
    --gold-dim:#9a7a34;
    --gold-glow:rgba(201,168,76,0.07);
    --gold-line:rgba(201,168,76,0.18);
    --cream:#e8e0d0;
    --cream-dim:rgba(232,224,208,0.6);
    --cream-mute:rgba(232,224,208,0.28);
    --white:#f0ece4;
    --green:#4caf7d;
    --green-bg:rgba(76,175,125,0.08);
    --red:#c0544a;
    --red-bg:rgba(192,84,74,0.08);
    --amber-warn:#d4922a;
    --warn-bg:rgba(212,146,42,0.08);
    --border:rgba(255,255,255,0.05);
    --border-md:rgba(255,255,255,0.09);
    --radius-sm:8px;
    --radius:12px;
    --font-disp:'Sora', sans-serif;
    --font-mono:'IBM Plex Mono', monospace;
}

/* === FIX 4 (UPDATED KPI HIGHLIGHT) === */
.bw-kpi.highlight {
    background: linear-gradient(160deg, #0d1017 60%, rgba(76,175,125,0.06) 100%);
    box-shadow: inset 0 0 0 1px rgba(76,175,125,0.15);
}

/* KEEP ALL YOUR OTHER STYLES EXACTLY SAME */
</style>
""", unsafe_allow_html=True)

# ====================== SESSION STATE ======================
if "supabase_session" not in st.session_state: st.session_state.supabase_session = None
if "income_form_key" not in st.session_state: st.session_state.income_form_key = 0
if "expense_form_key" not in st.session_state: st.session_state.expense_form_key = 0
if "show_reset" not in st.session_state: st.session_state.show_reset = False

def full_month(dt): return dt.strftime("%B %Y")
def short_month(dt): return dt.strftime("%b %Y")

# ====================== MASTHEAD ======================
st.markdown("""
<div class="bw-masthead">
    <span class="bw-masthead-label">Biverway &middot; Private Finance</span>
    <h1>Biverway Financial OS</h1>
    <div class="bw-masthead-sub">Your personal wealth command center</div>
</div>
""", unsafe_allow_html=True)

# ====================== AUTH WALL ======================
if st.session_state.supabase_session is None:
    tab1, tab2 = st.tabs(["Sign In", "Create Account"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In")
        if submit:
            try:
                res = client.auth.sign_in_with_password({"email": email, "password": password})
                if res.session:
                    st.session_state.supabase_session = res.session
                    st.rerun()
            except:
                st.error("Login failed")

    with tab2:
        with st.form("signup_form"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            submit_new = st.form_submit_button("Create Account")
        if submit_new:
            try:
                client.auth.sign_up({"email": new_email, "password": new_password})
                st.success("Check your email to confirm account.")
            except:
                st.error("Signup failed")

    st.stop()

# ====================== USER ======================
user_email = st.session_state.supabase_session.user.email
st.caption(user_email)

# ====================== MONTH ======================
working_month = st.date_input("", value=datetime.today())
current_month = short_month(working_month)
current_month_full = full_month(working_month)

# ====================== LOAD DATA ======================
income_records = load_income(current_month)
expense_records = load_expense(current_month)

income_df = pd.DataFrame(income_records)
expense_df = pd.DataFrame(expense_records)

if not income_df.empty:
    income_df["amount"] = pd.to_numeric(income_df["amount"])
if not expense_df.empty:
    expense_df["amount"] = pd.to_numeric(expense_df["amount"])

# ====================== PERFORMANCE ======================
total_income = income_df["amount"].sum() if not income_df.empty else 0
total_expense = expense_df["amount"].sum() if not expense_df.empty else 0
net_surplus = total_income - total_expense

st.markdown("### Financial Performance")

st.markdown(f"""
<div class="bw-kpi-grid">
    <div class="bw-kpi">
        <span class="kpi-label">Total<br>Income</span>
        <span class="kpi-value">&#8358;{total_income:,.0f}</span>
    </div>
    <div class="bw-kpi">
        <span class="kpi-label">Total<br>Expenses</span>
        <span class="kpi-value">&#8358;{total_expense:,.0f}</span>
    </div>
    <div class="bw-kpi highlight">
        <span class="kpi-label">Net<br>Surplus</span>
        <span class="kpi-value">&#8358;{net_surplus:,.0f}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ✅ FIX 8 (CONTEXT LINE)
st.markdown(f"<p style='color:gray;font-size:12px;'>Financial position for {current_month_full}</p>", unsafe_allow_html=True)

# ====================== INCOME ======================
st.markdown("### Income")

with st.expander("Record Income"):  # ✅ FIX 5
    with st.form("income_form"):
        source = st.text_input("Source")
        amount = st.number_input("Amount", min_value=0.0)
        submit = st.form_submit_button("Record Income")
    if submit:
        add_income(current_month, source, "Active", amount, "")
        st.rerun()

# ====================== EXPENSE ======================
st.markdown("### Expenses")

with st.expander("Record Expense"):  # ✅ FIX 5
    with st.form("expense_form"):
        category = st.text_input("Category")
        amount = st.number_input("Amount", min_value=0.0)
        submit = st.form_submit_button("Record Expense")
    if submit:
        add_expense(current_month, category, amount, "")
        st.rerun()

# ====================== LOCK ======================
st.markdown("### Period Control")

if st.button(f"Lock {current_month_full}"):
    lock_month(current_month)
    st.success("Month locked")
