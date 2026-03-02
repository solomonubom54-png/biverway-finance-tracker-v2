import streamlit as st
import pandas as pd
from datetime import datetime
import uuid
from core.sheets import append_row, load_sheet, delete_by_id

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
income_headers = ["id", "month_year", "income_source", "income_type", "amount", "notes"]
expense_headers = ["id", "month_year", "category", "amount", "description"]
allocation_headers = ["id", "month_year", "category", "percentage", "allocated_amount"]

# ====================== LOAD DATA ======================
income_records = load_sheet("Income", income_headers)
expense_records = load_sheet("Expense", expense_headers)
allocation_records = load_sheet("Allocation_Log", allocation_headers)

income_df = pd.DataFrame(income_records)
expense_df = pd.DataFrame(expense_records)
allocation_df = pd.DataFrame(allocation_records)

if not income_df.empty:
    income_df["amount"] = pd.to_numeric(income_df["amount"], errors="coerce").fillna(0)

if not expense_df.empty:
    expense_df["amount"] = pd.to_numeric(expense_df["amount"], errors="coerce").fillna(0)

income_df_month = income_df[income_df["month_year"] == current_month] if not income_df.empty else pd.DataFrame()
expense_df_month = expense_df[expense_df["month_year"] == current_month] if not expense_df.empty else pd.DataFrame()

# ====================== INCOME TRACKER ======================
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
        [str(uuid.uuid4()), current_month, income_source,
         income_type_map[income_source], amount, notes]
    )
    st.success("Income added successfully.")
    st.rerun()

st.subheader(f"📋 Income Records – {current_month}")

if not income_df_month.empty:
    st.dataframe(
        income_df_month[["income_source", "income_type", "amount", "notes"]],
        use_container_width=True
    )

    if st.button("🗑 Clear This Month Income"):
        for _, row in income_df_month.iterrows():
            delete_by_id("Income", row["id"])
        st.rerun()

    for _, row in income_df_month.iterrows():
        if st.button(
            f"Delete {row['income_source']} - ₦{row['amount']:,}",
            key=row["id"]
        ):
            delete_by_id("Income", row["id"])
            st.rerun()
else:
    st.info("No income entries yet.")

# ====================== EXPENSE TRACKER ======================
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
    append_row(
        "Expense",
        [str(uuid.uuid4()), current_month, category,
         expense_amount, description]
    )
    st.success("Expense added successfully.")
    st.rerun()

st.subheader(f"📋 Expense Records – {current_month}")

if not expense_df_month.empty:
    total_expense = expense_df_month["amount"].sum()
    expense_df_month["% of Total"] = (
        (expense_df_month["amount"] / total_expense * 100)
        .round(0).astype(int).astype(str) + "%"
        if total_expense > 0 else "0%"
    )

    st.dataframe(
        expense_df_month[["category", "amount", "% of Total", "description"]],
        use_container_width=True
    )

    if st.button("🗑 Clear This Month Expense"):
        for _, row in expense_df_month.iterrows():
            delete_by_id("Expense", row["id"])
        st.rerun()

    for _, row in expense_df_month.iterrows():
        if st.button(
            f"Delete {row['category']} - ₦{row['amount']:,}",
            key=row["id"]
        ):
            delete_by_id("Expense", row["id"])
            st.rerun()
else:
    st.info("No expense entries yet.")

# ====================== FINANCIAL PERFORMANCE ======================
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

st.write(f"Savings Rate: {savings_rate:.1f}%")

# ====================== ALLOCATION ======================
st.divider()
st.header("📂 Allocation")

if total_income > 0 and net_surplus > 0:

    allocation_modes = {
        "Default": {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 5},
        "Wealth Focus": {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 5, "Charity": 5},
        "Giving Focus": {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 25},
        "Security Focus": {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5, "Charity": 5},
    }

    mode = st.selectbox("Select Allocation Mode", list(allocation_modes.keys()))
    allocation_list = []

    for category, pct in allocation_modes[mode].items():
        allocation_list.append({
            "Category": category,
            "Percentage (%)": pct,
            "Allocated Amount (₦)": round(net_surplus * pct / 100, 0)
        })

    allocation_df_display = pd.DataFrame(allocation_list)
    st.dataframe(allocation_df_display, use_container_width=True)

    if st.button("💾 Save Allocation for Month"):

        if not allocation_df.empty and current_month in allocation_df["month_year"].values:
            st.warning("Allocation already saved for this month.")
        else:
            for row in allocation_list:
                append_row(
                    "Allocation_Log",
                    [
                        str(uuid.uuid4()),
                        current_month,
                        row["Category"],
                        row["Percentage (%)"],
                        row["Allocated Amount (₦)"]
                    ]
                )
            st.success("Allocation saved successfully.")
else:
    st.info("Allocation available only when surplus is positive.")
