from supabase import create_client
import streamlit as st

SUPABASE_URL = st.secrets["supabase"]["url"]
SUPABASE_KEY = st.secrets["supabase"]["anon_key"]

client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_client():
    session = st.session_state.get("supabase_session")
    if session:
        client.postgrest.auth(session.access_token)
    return client


def get_user_id():
    session = st.session_state.get("supabase_session")
    if session:
        return session.user.id
    return None


# ── INCOME ──────────────────────────────────────────

def add_income(month_year, source, income_type, amount, notes):
    try:
        get_client().table("income").insert({
            "user_id":     get_user_id(),
            "month_year":  month_year,
            "source":      source,
            "income_type": income_type,
            "amount":      float(amount),
            "notes":       notes or ""
        }).execute()
    except Exception as e:
        st.error(f"Add income error: {str(e)}")

def load_income(month_year):
    try:
        res = get_client().table("income") \
            .select("id, user_id, month_year, source, income_type, amount, notes") \
            .eq("month_year", month_year) \
            .execute()
        return res.data or []
    except Exception as e:
        st.error(f"Load income error: {str(e)}")
        return []

def delete_income(row_id):
    try:
        get_client().table("income").delete().eq("id", str(row_id)).execute()
    except Exception as e:
        st.error(f"Delete income error: {str(e)}")

def clear_income_month(month_year):
    try:
        get_client().table("income").delete().eq("month_year", month_year).execute()
    except Exception as e:
        st.error(f"Clear income error: {str(e)}")


# ── EXPENSE ─────────────────────────────────────────

def add_expense(month_year, category, amount, description):
    try:
        get_client().table("expense").insert({
            "user_id":     get_user_id(),
            "month_year":  month_year,
            "category":    category,
            "amount":      float(amount),
            "description": description or ""
        }).execute()
    except Exception as e:
        st.error(f"Add expense error: {str(e)}")

def load_expense(month_year):
    try:
        res = get_client().table("expense") \
            .select("id, user_id, month_year, category, amount, description") \
            .eq("month_year", month_year) \
            .execute()
        return res.data or []
    except Exception as e:
        st.error(f"Load expense error: {str(e)}")
        return []

def delete_expense(row_id):
    try:
        get_client().table("expense").delete().eq("id", str(row_id)).execute()
    except Exception as e:
        st.error(f"Delete expense error: {str(e)}")

def clear_expense_month(month_year):
    try:
        get_client().table("expense").delete().eq("month_year", month_year).execute()
    except Exception as e:
        st.error(f"Clear expense error: {str(e)}")


# ── LOCK MONTH ───────────────────────────────────────

def is_month_locked(month_year):
    try:
        res = get_client().table("locked_months") \
            .select("id") \
            .eq("user_id", get_user_id()) \
            .eq("month_year", month_year) \
            .execute()
        return len(res.data) > 0
    except Exception:
        return False

def lock_month(month_year):
    try:
        get_client().table("locked_months").insert({
            "user_id":    get_user_id(),
            "month_year": month_year
        }).execute()
        return True
    except Exception as e:
        st.error(f"Lock error: {str(e)}")
        return False
        
