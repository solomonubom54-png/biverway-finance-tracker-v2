import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet, delete_row, clear_sheet, clear_sheet_by_month

# ====================== PAGE CONFIG ======================
st.set_page_config(page_title="💎 Biverway Personal Finance Tracker", layout="wide")
st.title("💎 Biverway Personal Finance Tracker")
st.markdown("Performance-Driven Financial Control")
st.divider()

# ====================== SESSION STATE FOR FORM RESET ======================
if "income_form_key" not in st.session_state:
    st.session_state.income_form_key = 0
if "expense_form_key" not in st.session_state:
    st.session_state.expense_form_key = 0

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

# ====================== INCOME TRACKER ======================
st.header("💰 Income Tracker")

income_type_map = {
    "Skill": "Active",
    "Salary": "Active",
    "Business": "Passive",
    "Dividend/Interest": "Passive",
    "Rental": "Passive"
}

with st.form(f"income_form_{st.session_state.income_form_key}"):
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
    st.session_state.income_form_key += 1  # Reset form to defaults
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
            f"Delete {row['income_source']} - ₦{row['amount']:,}",
            key=f"inc_{idx}"
        ):
            delete_row("Income", idx + 2)
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

with st.form(f"expense_form_{st.session_state.expense_form_key}"):
    st.subheader("➕ Add New Expense Entry")
    category = st.selectbox("Category", expense_categories)
    expense_amount = st.number_input("Amount", min_value=0.0, step=1000.0, format="%0.0f")
    description = st.text_area("Description (optional)")
    submit_expense = st.form_submit_button("Add Expense")

if submit_expense:
    append_row("Expense", [current_month, category, expense_amount, description])
    st.success("Expense added successfully.")
    st.session_state.expense_form_key += 1  # Reset form to defaults
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
            f"Delete {row['category']} - ₦{row['amount']:,}",
            key=f"exp_{idx}"
        ):
            delete_row("Expense", idx + 2)
            st.rerun()
else:
    st.info("No expense entries yet.")

# ====================== FINANCIAL PERFORMANCE ======================
st.divider()
st.header("📊 Financial Performance")

with st.expander("View Details", expanded=False):
    total_income = income_df_month["amount"].sum() if not income_df_month.empty else 0
    total_expense = expense_df_month["amount"].sum() if not expense_df_month.empty else 0
    net_surplus = total_income - total_expense
    savings_rate = (net_surplus / total_income * 100) if total_income else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₦{total_income:,.0f}")
    col2.metric("Total Expenses", f"₦{total_expense:,.0f}")
    col3.metric("Net Surplus", f"₦{net_surplus:,.0f}")

    st.divider()
    st.subheader("Savings Insight")
    st.write(f"Net Surplus: ₦{net_surplus:,.0f}")
    st.write(f"Savings Rate: {savings_rate:.1f}%")
    if total_income == 0:
        st.error("No income recorded — financial performance cannot be evaluated.")
    else:
        if savings_rate >= 30:
            st.success("Strong financial position — excellent surplus discipline.")
        elif 15 <= savings_rate < 30:
            st.warning("Stable position — good, but optimization possible.")
        elif 1 <= savings_rate < 15:
            st.warning("Weak margin — expenses are too close to income.")
        else:
            st.error("Deficit — expenses exceed income.")

    st.divider()
    # Income Insight
    if not income_df_month.empty:
        active_income = income_df_month[income_df_month["income_type"] == "Active"]["amount"].sum()
        passive_income = income_df_month[income_df_month["income_type"] == "Passive"]["amount"].sum()
        active_pct = (active_income / total_income * 100) if total_income else 0
        passive_pct = (passive_income / total_income * 100) if total_income else 0

        st.subheader("Income Insight")
        st.write(f"Active Income: ₦{active_income:,.0f} ({active_pct:.0f}%)")
        st.write(f"Passive Income: ₦{passive_income:,.0f} ({passive_pct:.0f}%)")

        if active_pct >= 70:
            st.warning("Income is heavily effort-dependent. Increasing passive streams would improve resilience.")
        elif passive_pct >= 50:
            st.success("Healthy passive structure — income base is becoming resilient.")
        else:
            st.info("Income structure moderately balanced.")

    st.divider()
    # Expense Insight
    if not expense_df_month.empty:
        sorted_expense = expense_df_month.sort_values("amount", ascending=False)
        top = sorted_expense.head(2)
        st.subheader("Expense Insight")
        if len(top) == 1:
            row = top.iloc[0]
            st.write(f"{row['category']} ({row['% of Total']}) is the largest cost driver.")
        else:
            categories_text = " and ".join([f"{row['category']} ({row['% of Total']})" for _, row in top.iterrows()])
            st.write(f"{categories_text} are the largest cost drivers.")

# ====================== ALLOCATION LOG ======================
st.divider()
st.header("📂 Allocation Log")

with st.expander("View / Manage Allocation Log", expanded=False):
    if total_income == 0:
        st.info("No income recorded — allocation cannot be calculated.")
    elif net_surplus <= 0:
        st.warning("No surplus available — allocation only works when Net Surplus is positive.")
    else:
        allocation_modes = {
            "Default": {"Asset Building": 35, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 5},
            "Wealth Focus": {"Asset Building": 40, "Investing": 30, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 5, "Charity": 5},
            "Giving Focus": {"Asset Building": 25, "Investing": 20, "Insurance": 10, "Savings": 5, "Emergency": 5, "Lifestyle": 10, "Charity": 25},
            "Savings / Security Focus": {"Asset Building": 20, "Investing": 15, "Insurance": 20, "Savings": 20, "Emergency": 15, "Lifestyle": 5, "Charity": 5},
        }

        mode = st.selectbox("Select Allocation Mode", list(allocation_modes.keys()))
        allocation_list = []
        for category, pct in allocation_modes[mode].items():
            allocated_amount = round(net_surplus * pct / 100, 0)
            allocation_list.append({"Category": category, "Percentage (%)": pct, "Allocated Amount (₦)": allocated_amount})

        allocation_df = pd.DataFrame(allocation_list)
        st.dataframe(allocation_df, use_container_width=True)

        if st.button("💾 Save Allocation for Month"):
            # Clear existing rows for this month before saving fresh data
            clear_sheet_by_month("Allocation_Log", current_month)
            for row in allocation_list:
                append_row(
                    "Allocation_Log",
                    [current_month, row["Category"], row["Percentage (%)"], row["Allocated Amount (₦)"]]
                )
            st.success("Allocation saved to Google Sheet successfully.")
