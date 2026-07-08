import os
from dotenv import load_dotenv
from supabase import create_client, Client
import streamlit as st

# Lokal .env laden
load_dotenv()

# Erst Streamlit Secrets verwenden, falls vorhanden.
# Ansonsten lokal auf .env zurückfallen.
SUPABASE_URL = st.secrets.get("SUPABASE_URL", os.getenv("SUPABASE_URL"))
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", os.getenv("SUPABASE_KEY"))

#load_dotenv()
#SUPABASE_URL = os.getenv("SUPABASE_URL")
#SUPABASE_KEY = os.getenv("SUPABASE_KEY")


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


def refresh_session(refresh_token: str):
    """Tauscht einen gespeicherten Refresh-Token gegen eine frische Session
    (neuer Access-Token + neuer, rotierter Refresh-Token) ein. Damit lässt
    sich eine Anmeldung wiederherstellen, ohne E-Mail/Passwort erneut
    abzufragen – solange der Refresh-Token noch gültig ist."""
    client = _new_client()
    return client.auth.refresh_session(refresh_token)


def sign_out(access_token: str, refresh_token: str):
    """Beendet die Session serverseitig bei Supabase (der Refresh-Token wird
    dabei ungültig gemacht, nicht nur lokal vergessen)."""
    client = get_authenticated_client(access_token, refresh_token)
    client.auth.sign_out()
