import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet, delete_row, clear_sheet

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="Biverway Finance OS", layout="wide")

st.title("BIVERWAY FINANCE OS")
st.caption("Reliable. Efficient. Structured Capital.")
st.divider()

# ====================== MONTH SELECTOR ======================
top_col1, top_col2 = st.columns([2, 1])

with top_col1:
    working_month = st.date_input("Working Month", value=datetime.today())
    current_month = working_month.strftime("%b %Y")

with top_col2:
    st.markdown(f"**Operating Period:**  \n{current_month}")

st.divider()

# ====================== LOAD DATA ======================
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
    income_df_month["amount"] = pd.to_numeric(
        income_df_month["amount"], errors="coerce"
    ).fillna(0)

if not expense_df_month.empty:
    expense_df_month["amount"] = pd.to_numeric(
        expense_df_month["amount"], errors="coerce"
    ).fillna(0)

total_income = income_df_month["amount"].sum() if not income_df_month.empty else 0
total_expense = expense_df_month["amount"].sum() if not expense_df_month.empty else 0
net_surplus = total_income - total_expense
savings_rate = (net_surplus / total_income * 100) if total_income else 0

# ==========================================================
# ===================== CAPITAL POSITION ===================
# ==========================================================

st.subheader("Capital Position")

metric1, metric2, metric3 = st.columns(3)

metric1.metric("Total Income", f"₦{total_income:,.0f}")
metric2.metric("Total Expense", f"₦{total_expense:,.0f}")
metric3.metric("Net Surplus", f"₦{net_surplus:,.0f}")

st.markdown(f"**Savings Rate:** {savings_rate:.1f}%")

if total_income > 0:
    if savings_rate >= 30:
        st.success("Capital posture is strong and well controlled.")
    elif savings_rate >= 15:
        st.warning("Capital posture is stable but can be optimized.")
    else:
        st.error("Capital margin is under pressure.")

st.divider()

# ==========================================================
# ===================== CAPITAL INTAKE =====================
# ==========================================================

st.subheader("Capital Intake")

left_col, right_col = st.columns([1, 1])

income_type_map = {
    "Skill": "Active",
    "Salary": "Active",
    "Business": "Passive",
    "Dividend/Interest": "Passive",
    "Rental": "Passive"
}

with left_col:
    st.markdown("#### Add Capital Entry")

    with st.form("income_form"):
        income_source = st.selectbox("Income Source", list(income_type_map.keys()))
        amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
        notes = st.text_area("Notes (optional)")
        submit_income = st.form_submit_button("Add Capital")

    if submit_income:
        append_row(
            "Income",
            [current_month, income_source, income_type_map[income_source], amount, notes]
        )
        st.success("Capital recorded.")
        st.rerun()

with right_col:
    st.markdown("#### Recorded Income")

    if not income_df_month.empty:
        st.dataframe(
            income_df_month[["income_source", "income_type", "amount"]],
            use_container_width=True
        )

        if st.button("Clear Income Records"):
            clear_sheet("Income")
            st.rerun()

    else:
        st.info("No income entries for this month.")

st.divider()

# ==========================================================
# ===================== CAPITAL OUTFLOW ====================
# ==========================================================

st.subheader("Capital Outflow")

left_col2, right_col2 = st.columns([1, 1])

expense_categories = [
    "Rent", "Food", "Utilities", "Transport",
    "Healthcare", "Education", "Subscription", "Family Support"
]

with left_col2:
    st.markdown("#### Add Outflow Entry")

    with st.form("expense_form"):
        category = st.selectbox("Category", expense_categories)
        expense_amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
        description = st.text_area("Description (optional)")
        submit_expense = st.form_submit_button("Add Outflow")

    if submit_expense:
        append_row("Expense", [current_month, category, expense_amount, description])
        st.success("Outflow recorded.")
        st.rerun()

with right_col2:
    st.markdown("#### Recorded Expenses")

    if not expense_df_month.empty:
        total_expense = expense_df_month["amount"].sum()

        if total_expense > 0:
            expense_df_month["% of Total"] = (
                expense_df_month["amount"] / total_expense * 100
            ).round(0).astype(int).astype(str) + "%"

        st.dataframe(
            expense_df_month[["category", "amount", "% of Total"]],
            use_container_width=True
        )

        if st.button("Clear Expense Records"):
            clear_sheet("Expense")
            st.rerun()

    else:
        st.info("No expenses recorded for this month.")

st.divider()

# ==========================================================
# ===================== ALLOCATION ENGINE ==================
# ==========================================================

st.subheader("Allocation Engine")

allocation_modes = {
    "Default": {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 5},
    "Wealth Focus": {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 5, "Charity": 5},
    "Giving Focus": {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 25},
    "Savings / Security Focus": {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5, "Charity": 5},
}

mode = st.selectbox("Allocation Mode", list(allocation_modes.keys()))

if total_income == 0:
    st.info("No income recorded — allocation unavailable.")
elif net_surplus <= 0:
    st.warning("No surplus available for allocation.")
else:
    allocation_list = []
    for category, pct in allocation_modes[mode].items():
        allocated_amount = round(net_surplus * pct / 100, 0)
        allocation_list.append({
            "Category": category,
            "Percentage (%)": pct,
            "Allocated Amount (₦)": allocated_amount
        })

    allocation_df = pd.DataFrame(allocation_list)
    st.dataframe(allocation_df, use_container_width=True)

    if st.button("Save Allocation"):
        for row in allocation_list:
            append_row(
                "Allocation_Log",
                [current_month, row["Category"], row["Percentage (%)"], row["Allocated Amount (₦)"]]
            )
        st.success("Allocation saved successfully.")
