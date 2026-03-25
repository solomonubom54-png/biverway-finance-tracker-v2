from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["anon_key"]

client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_client():
    """Inject the user's access token into the postgrest client so RLS works."""
    session = st.session_state.get("supabase_session")
    if session:
        token = session.access_token
        client.postgrest.auth(token)
    return client


def get_user_id():
    session = st.session_state.get("supabase_session")
    if session:
        return session.user.id
    return None


# ── INCOME ──────────────────────────────────────────

def add_income(month_year, source, income_type, amount, notes):
    get_client().table("income").insert({
        "user_id":     get_user_id(),
        "month_year":  month_year,
        "source":      source,
        "income_type": income_type,
        "amount":      float(amount),
        "notes":       notes or ""
    }).execute()

def load_income(month_year):
    res = get_client().table("income") \
        .select("*") \
        .eq("month_year", month_year) \
        .order("created_at") \
        .execute()
    return res.data or []

def delete_income(row_id):
    get_client().table("income").delete().eq("id", row_id).execute()

def clear_income_month(month_year):
    get_client().table("income").delete().eq("month_year", month_year).execute()


# ── EXPENSE ─────────────────────────────────────────

def add_expense(month_year, category, amount, description):
    get_client().table("expense").insert({
        "user_id":     get_user_id(),
        "month_year":  month_year,
        "category":    category,
        "amount":      float(amount),
        "description": description or ""
    }).execute()

def load_expense(month_year):
    res = get_client().table("expense") \
        .select("*") \
        .eq("month_year", month_year) \
        .order("created_at") \
        .execute()
    return res.data or []

def delete_expense(row_id):
    get_client().table("expense").delete().eq("id", row_id).execute()

def clear_expense_month(month_year):
    get_client().table("expense").delete().eq("month_year", month_year).execute()


# ── ALLOCATION LOG ───────────────────────────────────

def save_allocation(month_year, allocation_list):
    get_client().table("allocation_log").delete().eq("month_year", month_year).execute()
    rows = [{
        "user_id":          get_user_id(),
        "month_year":       month_year,
        "category":         r["Category"],
        "percentage":       int(r["Percentage (%)"]),
        "allocated_amount": float(r["Allocated Amount (₦)"])
    } for r in allocation_list]
    get_client().table("allocation_log").insert(rows).execute()
