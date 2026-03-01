import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Biverway Finance OS", layout="wide")

# ================= HEADER =================
st.markdown("# BIVERWAY FINANCE OS")
st.markdown("Reliable. Efficient. Structured Capital.")
st.divider()

# ================= MONTH SELECTOR =================
colA, colB = st.columns([3,1])

with colA:
    working_month = st.date_input("Month", value=datetime.today())
    current_month = working_month.strftime("%b %Y")

with colB:
    allocation_mode = st.selectbox(
        "Allocation Mode",
        ["Default", "Wealth Focus", "Giving Focus", "Savings / Security Focus"]
    )

st.divider()

# ================= LOAD DATA =================
income_headers = ["month_year", "income_source", "income_type", "amount", "notes"]
expense_headers = ["month_year", "category", "amount", "description"]

income_records = load_sheet("Income", income_headers)
expense_records = load_sheet("Expense", expense_headers)

income_df = pd.DataFrame(income_records)
expense_df = pd.DataFrame(expense_records)

if "month_year" not in income_df.columns:
    income_df["month_year"] = ""

if "month_year" not in expense_df.columns:
    expense_df["month_year"] = ""

income_df_month = income_df[income_df["month_year"] == current_month].copy()
expense_df_month = expense_df[expense_df["month_year"] == current_month].copy()

if not income_df_month.empty:
    income_df_month["amount"] = pd.to_numeric(income_df_month["amount"], errors="coerce").fillna(0)

if not expense_df_month.empty:
    expense_df_month["amount"] = pd.to_numeric(expense_df_month["amount"], errors="coerce").fillna(0)

total_income = income_df_month["amount"].sum() if not income_df_month.empty else 0
total_expense = expense_df_month["amount"].sum() if not expense_df_month.empty else 0
net_surplus = total_income - total_expense
savings_rate = (net_surplus / total_income * 100) if total_income else 0

# ================= EXECUTIVE OVERVIEW =================
st.subheader("Capital Position")

col1, col2, col3 = st.columns(3)

col1.metric("Net Surplus", f"₦{net_surplus:,.0f}")
col2.metric("Total Income", f"₦{total_income:,.0f}")
col3.metric("Total Expense", f"₦{total_expense:,.0f}")

st.write(f"Savings Rate: {savings_rate:.1f}%")

st.divider()

# ================= MODULE GRID =================
st.subheader("Control Modules")

m1, m2 = st.columns(2)
m3, m4 = st.columns(2)
m5, m6 = st.columns(2)

with m1:
    intake = st.button("Capital Intake")

with m2:
    outflow = st.button("Capital Outflow")

with m3:
    allocation = st.button("Allocation Engine")

with m4:
    performance = st.button("Performance History")

with m5:
    assets = st.button("Asset Control")

with m6:
    liabilities = st.button("Liability Control")

st.divider()

# ================= CAPITAL INTAKE =================
if intake:
    st.subheader("Capital Intake")

    income_type_map = {
        "Skill": "Active",
        "Salary": "Active",
        "Business": "Passive",
        "Dividend/Interest": "Passive",
        "Rental": "Passive"
    }

    with st.form("os_income"):
        source = st.selectbox("Source", list(income_type_map.keys()))
        amount = st.number_input("Amount", min_value=0.0)
        notes = st.text_area("Notes")
        submit = st.form_submit_button("Add Entry")

    if submit:
        append_row(
            "Income",
            [current_month, source, income_type_map[source], amount, notes]
        )
        st.success("Capital recorded.")

    if not income_df_month.empty:
        st.dataframe(income_df_month[["income_source","income_type","amount"]])

# ================= CAPITAL OUTFLOW =================
if outflow:
    st.subheader("Capital Outflow")

    categories = ["Rent","Food","Transport","Utilities","Healthcare","Education"]

    with st.form("os_expense"):
        category = st.selectbox("Category", categories)
        amount = st.number_input("Amount", min_value=0.0)
        description = st.text_area("Description")
        submit2 = st.form_submit_button("Add Entry")

    if submit2:
        append_row("Expense", [current_month, category, amount, description])
        st.success("Outflow recorded.")

    if not expense_df_month.empty:
        st.dataframe(expense_df_month[["category","amount"]])

# ================= ALLOCATION ENGINE =================
if allocation:
    st.subheader("Allocation Engine")

    allocation_modes = {
        "Default": {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 5},
        "Wealth Focus": {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 5, "Charity": 5},
        "Giving Focus": {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 25},
        "Savings / Security Focus": {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5, "Charity": 5},
    }

    mode_data = allocation_modes[allocation_mode]

    allocation_list = []
    for category, pct in mode_data.items():
        allocated_amount = round(net_surplus * pct / 100, 0)
        allocation_list.append({
            "Category": category,
            "Percentage (%)": pct,
            "Allocated Amount (₦)": allocated_amount
        })

    allocation_df = pd.DataFrame(allocation_list)
    st.dataframe(allocation_df)

# ================= PERFORMANCE =================
if performance:
    st.subheader("Performance History")
    st.write("Historical performance tracking will be structured here.")

# ================= ASSETS =================
if assets:
    st.subheader("Asset Control")
    st.write("Asset tracking module coming next.")

# ================= LIABILITIES =================
if liabilities:
    st.subheader("Liability Control")
    st.write("Liability tracking module coming next.")
