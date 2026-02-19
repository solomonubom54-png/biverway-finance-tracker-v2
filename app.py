import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet, delete_row, clear_sheet

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="💎 Biverway Personal Finance Tracker", layout="wide")
st.title("💎 Biverway Personal Finance Tracker")
st.markdown("Performance-Driven Financial Control")
st.divider()

# ====================== MONTH SELECTOR ======================
st.header("📅 Select Working Month")
working_month = st.date_input("Working Month", value=datetime.today())
current_month = working_month.strftime("%b %Y")
st.info(f"All data below is for {current_month}")

# ====================== HEADERS ======================
income_headers = ["month_year", "income_source", "income_type", "amount", "notes"]
expense_headers = ["month_year", "category", "amount", "description"]

# ====================== LOAD DATA ======================
income_records = load_sheet("Income", income_headers)
expense_records = load_sheet("Expense", expense_headers)

income_df = pd.DataFrame(income_records)
expense_df = pd.DataFrame(expense_records)

# Ensure required columns exist
for col in income_headers:
    if col not in income_df.columns:
        income_df[col] = ""

for col in expense_headers:
    if col not in expense_df.columns:
        expense_df[col] = ""

income_df_month = income_df[income_df["month_year"] == current_month].copy()
expense_df_month = expense_df[expense_df["month_year"] == current_month].copy()

if not income_df_month.empty:
    income_df_month["amount"] = pd.to_numeric(
        income_df_month["amount"], errors="coerce"
    ).fillna(0)

if not expense_df_month.empty:
    expense_df_month["amount"] = pd.to_numeric(
        expense_df_month["amount"], errors="coerce"
    ).fillna(0)

# ====================== INCOME SECTION ======================
st.header("💰 Income Tracker")

income_type_map = {
    "Skill": "Active",
    "Salary": "Active",
    "Business": "Passive",
    "Dividend/Interest": "Passive",
    "Rental": "Passive"
}

with st.form("income_form"):
    st.subheader("➕ Add New Income Entry")
    income_source = st.selectbox("Income Source", list(income_type_map.keys()))
    amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
    notes = st.text_area("Notes (optional)")
    submit_income = st.form_submit_button("Add Income")

if submit_income:
    append_row(
        "Income",
        [current_month, income_source, income_type_map[income_source], amount, notes]
    )
    st.success("Income added successfully.")
    st.rerun()

st.subheader(f"📋 Income Records – {current_month}")

if not income_df_month.empty:
    st.dataframe(
        income_df_month[["income_source", "income_type", "amount", "notes"]],
        use_container_width=True
    )

    if st.button("🗑 Clear All Income Records"):
        clear_sheet("Income")
        st.rerun()

    for idx, row in income_df_month.iterrows():
        if st.button(
            f"Delete {row['income_source']} - ₦{row['amount']:,.0f}",
            key=f"inc_{idx}"
        ):
            delete_row("Income", idx + 2)
            st.rerun()
else:
    st.info("No income entries yet.")

# ====================== EXPENSE SECTION ======================
st.divider()
st.header("💸 Expense Tracker")

expense_categories = [
    "Rent", "Food", "Utilities", "Transport",
    "Healthcare", "Education", "Subscription", "Family Support"
]

with st.form("expense_form"):
    st.subheader("➕ Add New Expense Entry")
    category = st.selectbox("Category", expense_categories)
    expense_amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
    description = st.text_area("Description (optional)")
    submit_expense = st.form_submit_button("Add Expense")

if submit_expense:
    append_row("Expense", [current_month, category, expense_amount, description])
    st.success("Expense added successfully.")
    st.rerun()

st.subheader(f"📋 Expense Records – {current_month}")

if not expense_df_month.empty:
    total_expense = expense_df_month["amount"].sum()

    if total_expense > 0:
        expense_df_month["% of Total"] = (
            expense_df_month["amount"] / total_expense * 100
        ).round(0).astype(int).astype(str) + "%"
    else:
        expense_df_month["% of Total"] = "0%"

    st.dataframe(
        expense_df_month[["category", "amount", "% of Total", "description"]],
        use_container_width=True
    )

    if st.button("🗑 Clear All Expense Records"):
        clear_sheet("Expense")
        st.rerun()

    for idx, row in expense_df_month.iterrows():
        if st.button(
            f"Delete {row['category']} - ₦{row['amount']:,.0f}",
            key=f"exp_{idx}"
        ):
            delete_row("Expense", idx + 2)
            st.rerun()
else:
    st.info("No expense entries yet.")

# ====================== PERFORMANCE ======================
st.divider()
st.header("📊 Financial Performance")

total_income = income_df_month["amount"].sum() if not income_df_month.empty else 0
total_expense = expense_df_month["amount"].sum() if not expense_df_month.empty else 0
net_surplus = total_income - total_expense
savings_rate = (net_surplus / total_income * 100) if total_income else 0

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₦{total_income:,.0f}")
col2.metric("Total Expenses", f"₦{total_expense:,.0f}")
col3.metric("Net Surplus", f"₦{net_surplus:,.0f}")
