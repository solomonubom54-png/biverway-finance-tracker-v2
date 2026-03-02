import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Biverway Finance OS", layout="wide")

st.title("BIVERWAY FINANCE OS")
st.markdown("Reliable. Efficient. Structured Capital.")
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

# ================= MONTH SELECTOR =================
working_month = st.date_input("Working Month", value=datetime.today())
current_month = working_month.strftime("%b %Y")

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

# ===============================================================
# ====================== CAPITAL POSITION =======================
# ===============================================================

st.subheader("Capital Position")

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₦{total_income:,.0f}")
col2.metric("Total Expense", f"₦{total_expense:,.0f}")
col3.metric("Net Surplus", f"₦{net_surplus:,.0f}")

st.write(f"Savings Rate: {savings_rate:.1f}%")

if total_income > 0:
    if savings_rate >= 30:
        st.success("Capital posture: Strong and controlled.")
    elif savings_rate >= 15:
        st.warning("Capital posture: Stable but optimization possible.")
    else:
        st.error("Capital posture: Margin under pressure.")

st.divider()

# ===============================================================
# ====================== INCOME STRUCTURE =======================
# ===============================================================

st.subheader("Income Structure")

if not income_df_month.empty:
    active_income = income_df_month[
        income_df_month["income_type"] == "Active"
    ]["amount"].sum()

    passive_income = income_df_month[
        income_df_month["income_type"] == "Passive"
    ]["amount"].sum()

    active_pct = (active_income / total_income * 100) if total_income else 0
    passive_pct = (passive_income / total_income * 100) if total_income else 0

    st.write(f"Active Income: ₦{active_income:,.0f} ({active_pct:.0f}%)")
    st.write(f"Passive Income: ₦{passive_income:,.0f} ({passive_pct:.0f}%)")

    if active_pct >= 70:
        st.warning("Income base heavily effort-dependent.")
    elif passive_pct >= 50:
        st.success("Income structure resilient and diversified.")
    else:
        st.info("Income structure moderately balanced.")
else:
    st.info("No income recorded for this month.")

st.divider()

# ===============================================================
# ====================== EXPENSE STRUCTURE ======================
# ===============================================================

st.subheader("Expense Structure")

if not expense_df_month.empty:
    total_expense = expense_df_month["amount"].sum()
    sorted_expense = expense_df_month.sort_values("amount", ascending=False)

    if total_expense > 0:
        sorted_expense["% of Total"] = (
            sorted_expense["amount"] / total_expense * 100
        ).round(0).astype(int).astype(str) + "%"

    st.dataframe(
        sorted_expense[["category", "amount", "% of Total"]],
        use_container_width=True
    )

    top = sorted_expense.head(1).iloc[0]
    st.write(f"Largest cost driver: {top['category']} ({top['% of Total']})")

else:
    st.info("No expenses recorded for this month.")

st.divider()

# ===============================================================
# ======================= ALLOCATION ENGINE =====================
# ===============================================================

st.subheader("Allocation Engine")

allocation_modes = {
    "Default": {
        "Asset Building": 35,
        "Investing": 30,
        "Insurance": 10,
        "Savings": 5,
        "Emergency": 5,
        "Lifestyle": 10,
        "Charity": 5,
    },
    "Wealth Focus": {
        "Asset Building": 40,
        "Investing": 30,
        "Insurance": 10,
        "Savings": 5,
        "Emergency": 5,
        "Lifestyle": 5,
        "Charity": 5,
    },
    "Giving Focus": {
        "Asset Building": 25,
        "Investing": 20,
        "Insurance": 10,
        "Savings": 5,
        "Emergency": 5,
        "Lifestyle": 10,
        "Charity": 25,
    },
    "Savings / Security Focus": {
        "Asset Building": 20,
        "Investing": 15,
        "Insurance": 20,
        "Savings": 20,
        "Emergency": 15,
        "Lifestyle": 5,
        "Charity": 5,
    },
}

mode = st.selectbox("Allocation Mode", list(allocation_modes.keys()))

if net_surplus > 0:
    allocation_list = []
    for category, pct in allocation_modes[mode].items():
        allocated_amount = round(net_surplus * pct / 100, 0)
        allocation_list.append(
            {
                "Category": category,
                "Percentage (%)": pct,
                "Allocated Amount (₦)": allocated_amount,
            }
        )

    allocation_df = pd.DataFrame(allocation_list)

    st.dataframe(allocation_df, use_container_width=True)

else:
    st.info("No surplus available for allocation.")
