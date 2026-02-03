import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

def get_db_connection(access_token=None) -> Client:
    """
    Establishes and returns a connection to the Supabase project.
    If access_token is provided, it configures the client to use it for RLS.
    """
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in the .env file.")
    
    supabase: Client = create_client(url, key)
    
    if access_token:
        # Set the access token in the headers for all subsequent requests
        # This is necessary for Row Level Security (RLS) to work
        supabase.postgrest.auth(access_token)
        
    return supabase

def init_db():
    """
    Placeholder for any specific initialization if needed.
    Supabase is generally managed via dashboard or migrations, 
    but this could be used for initial setup checks.
    """
    print("Supabase connection configured.")
