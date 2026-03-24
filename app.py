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
current_month = working_month.strftime("%B %Y")  # FIXED
st.info(f"All data below is for {current_month}")

# ====================== HEADERS ======================
income_headers = ["month_year", "income_source", "income_type", "amount", "notes"]
expense_headers = ["month_year", "category", "amount", "description"]
allocation_headers = ["month_year", "category", "percentage", "amount"]

# ====================== LOAD DATA ======================
income_records = load_sheet("Income", income_headers)
expense_records = load_sheet("Expense", expense_headers)
allocation_records = load_sheet("Allocation_Log", allocation_headers)

income_df = pd.DataFrame(income_records)
expense_df = pd.DataFrame(expense_records)
allocation_df = pd.DataFrame(allocation_records)

# Ensure columns exist
for df, headers in [(income_df, income_headers), (expense_df, expense_headers)]:
    for col in headers:
        if col not in df.columns:
            df[col] = ""

# Filter by month
income_df_month = income_df[income_df["month_year"] == current_month].copy()
expense_df_month = expense_df[expense_df["month_year"] == current_month].copy()
allocation_df_month = allocation_df[allocation_df["month_year"] == current_month].copy()

# Convert amounts
if not income_df_month.empty:
    income_df_month["amount"] = pd.to_numeric(income_df_month["amount"], errors="coerce").fillna(0)

if not expense_df_month.empty:
    expense_df_month["amount"] = pd.to_numeric(expense_df_month["amount"], errors="coerce").fillna(0)

# ====================== GLOBAL METRICS (FIXED SCOPE) ======================
total_income = income_df_month["amount"].sum() if not income_df_month.empty else 0
total_expense = expense_df_month["amount"].sum() if not expense_df_month.empty else 0
net_surplus = total_income - total_expense

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
    append_row("Income", [current_month, income_source, income_type_map[income_source], amount, notes])
    st.success("Income added successfully.")
    st.rerun()

st.subheader(f"📋 Income Records – {current_month}")

if not income_df_month.empty:
    st.dataframe(
        income_df_month[["income_source", "income_type", "amount", "notes"]],
        use_container_width=True
    )

    # Delete specific
    selected_income = st.selectbox(
        "Select income to delete",
        income_df_month.index,
        format_func=lambda x: f"{income_df_month.loc[x, 'income_source']} - ₦{income_df_month.loc[x, 'amount']:,}"
    )

    if st.button("Delete Selected Income"):
        delete_row("Income", selected_income + 2)
        st.rerun()

    # Clear month safely
    if st.button("🗑 Clear This Month's Income"):
        rows_to_delete = [i + 2 for i, row in income_df.iterrows() if row["month_year"] == current_month]
        for r in sorted(rows_to_delete, reverse=True):
            delete_row("Income", r)
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

    selected_expense = st.selectbox(
        "Select expense to delete",
        expense_df_month.index,
        format_func=lambda x: f"{expense_df_month.loc[x, 'category']} - ₦{expense_df_month.loc[x, 'amount']:,}"
    )

    if st.button("Delete Selected Expense"):
        delete_row("Expense", selected_expense + 2)
        st.rerun()

    if st.button("🗑 Clear This Month's Expenses"):
        rows_to_delete = [i + 2 for i, row in expense_df.iterrows() if row["month_year"] == current_month]
        for r in sorted(rows_to_delete, reverse=True):
            delete_row("Expense", r)
        st.rerun()

else:
    st.info("No expense entries yet.")

# ====================== FINANCIAL PERFORMANCE ======================
st.divider()
st.header("📊 Financial Performance")

with st.expander("View Details", expanded=False):
    savings_rate = (net_surplus / total_income * 100) if total_income else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₦{total_income:,.0f}")
    col2.metric("Total Expenses", f"₦{total_expense:,.0f}")
    col3.metric("Net Surplus", f"₦{net_surplus:,.0f}")

    st.divider()
    st.subheader("Savings Insight")
    st.write(f"Savings Rate: {savings_rate:.1f}%")

    if total_income == 0:
        st.error("No income recorded.")
    elif savings_rate >= 30:
        st.success("Excellent financial discipline.")
    elif savings_rate >= 15:
        st.warning("Stable but improvable.")
    elif savings_rate >= 1:
        st.warning("Weak margin.")
    else:
        st.error("Deficit.")

# ====================== ALLOCATION LOG ======================
st.divider()
st.header("📂 Allocation Log")

with st.expander("View / Manage Allocation Log", expanded=False):
    if total_income == 0:
        st.info("No income recorded.")
    elif net_surplus <= 0:
        st.warning("No surplus available.")
    else:
        allocation_modes = {
            "Default": {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 5}
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

        if st.button("💾 Save Allocation"):
            for row in allocation_list:
                append_row("Allocation_Log", [current_month, row["Category"], row["Percentage (%)"], row["Allocated Amount (₦)"]])
            st.success("Saved successfully.")

    if not allocation_df_month.empty:
        st.subheader("Saved Allocation History")
        st.dataframe(allocation_df_month, use_container_width=True)
