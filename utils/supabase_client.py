# utils/supabase_client.py

import os

from typing import Optional

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

def _get_client() -> Optional["Client"]:
    if not create_client or not SUPABASE_URL or not SUPABASE_KEY:
        return None
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_user_profile(email: str):
    client = _get_client()
    if client is None:
        # mock profile when supabase is not configured
        return {"email": email, "is_subscribed": False}
    res = client.table("profiles").select("*").eq("email", email).execute()
    if res.data:
        return res.data[0]
    return {"email": email, "is_subscribed": False}

def user_has_subscription(profile) -> bool:
    return bool(profile.get("is_subscribed"))
