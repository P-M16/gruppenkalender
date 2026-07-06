import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")


def _new_client() -> Client:
    """Erzeugt IMMER einen frischen Client (wichtig: kein globaler Singleton,
    da sonst Auth-Sessions verschiedener Nutzer:innen sich vermischen könnten)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError(
            "SUPABASE_URL und SUPABASE_KEY sind nicht gesetzt. Bitte .env Datei anlegen (siehe .env.example)."
        )
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def sign_up(email: str, password: str, full_name: str):
    """Registriert einen neuen Nutzer und speichert den Namen als Metadaten."""
    client = _new_client()
    return client.auth.sign_up(
        {
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}},
        }
    )


def sign_in(email: str, password: str):
    """Loggt einen Nutzer ein und gibt Session + User zurück."""
    client = _new_client()
    return client.auth.sign_in_with_password({"email": email, "password": password})


def get_authenticated_client(access_token: str, refresh_token: str) -> Client:
    """Erstellt einen Client, der im Namen des eingeloggten Nutzers agiert.
    Wird pro Anfrage neu erzeugt, damit Streamlit-Sessions verschiedener
    Nutzer:innen sich nicht gegenseitig beeinflussen."""
    client = _new_client()
    client.auth.set_session(access_token, refresh_token)
    return client
