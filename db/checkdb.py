import supabase
import os
from dotenv import load_dotenv
load_dotenv()

supabase_url = os.getenv("SUPABASE_URL", "")
supabase_key = os.getenv("SUPABASE_KEY", "")

supabase = supabase.create_client(supabase_url, supabase_key)

if __name__ == "__main__":
    supabase.table("users").insert({
    "username": "test",
    "password_hash": "abc",
    "name": "Test User"
}).execute()