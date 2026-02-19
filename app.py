
import streamlit as st
import pandas as pd
from datetime import datetime
from core.sheets import append_row, load_sheet

st.set_page_config(page_title="Biverway Finance Tracker", layout="wide")

st.title("💎 Biverway Finance Tracker")

# Select Month
working_month = st.date_input("Select Month", value=datetime.today())
current_month = working_month.strftime("%b %Y")

# ================= INCOME =================
st.header("Income")

with st.form("income_form", clear_on_submit=True):
    source = st.text_input("Income Source")
    amount = st.number_input("Amount", min_value=0.0)
    submit_income = st.form_submit_button("Add Income")

if submit_income:
    append_row("Income", [current_month, source, amount])
    st.success("Income added")

income_data = load_sheet("Income")
income_df = pd.DataFrame(income_data)

if not income_df.empty:
    income_df = income_df[income_df["month_year"] == current_month]
    income_df["amount"] = pd.to_numeric(income_df["amount"], errors="coerce").fillna(0)
    st.dataframe(income_df)

# ================= EXPENSE =================
st.header("Expense")

with st.form("expense_form", clear_on_submit=True):
    category = st.text_input("Category")
    expense_amount = st.number_input("Expense Amount", min_value=0.0)
    submit_expense = st.form_submit_button("Add Expense")

if submit_expense:
    append_row("Expense", [current_month, category, expense_amount])
    st.success("Expense added")

expense_data = load_sheet("Expense")
expense_df = pd.DataFrame(expense_data)

if not expense_df.empty:
    expense_df = expense_df[expense_df["month_year"] == current_month]
    expense_df["amount"] = pd.to_numeric(expense_df["amount"], errors="coerce").fillna(0)
    st.dataframe(expense_df)

# ================= SUMMARY =================
st.header("Summary")

total_income = income_df["amount"].sum() if not income_df.empty else 0
total_expense = expense_df["amount"].sum() if not expense_df.empty else 0
net = total_income - total_expense

col1, col2, col3 = st.columns(3)
col1.metric("Total Income", f"₦{total_income:,.0f}")
col2.metric("Total Expense", f"₦{total_expense:,.0f}")
col3.metric("Net", f"₦{net:,.0f}")
