from calendar import monthrange


def get_entries_for_month(client, year: int, month: int):
    """Holt alle Einträge für einen Monat (alle Nutzer:innen, da RLS
    authentifizierten Lesezugriff auf alle Zeilen erlaubt)."""
    last_day = monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    response = (
        client.table("availability")
        .select("*")
        .gte("date", start_date)
        .lte("date", end_date)
        .order("date")
        .execute()
    )
    return response.data


def get_all_entries(client):
    """Holt ALLE Einträge, unabhängig vom Monat – FullCalendar übernimmt die
    Navigation zwischen den Monaten selbst im Frontend."""
    response = client.table("availability").select("*").order("date").execute()
    return response.data


def add_entry(client, entry_date: str, user_id: str, name: str, activity: str = ""):
    """Trägt den eingeloggten Nutzer für einen Tag ein."""
    client.table("availability").insert(
        {"date": entry_date, "user_id": user_id, "name": name, "activity": activity}
    ).execute()


def get_activities_for_month(client, year: int, month: int):
    """Holt alle Aktivitätsvorschläge für einen Monat (mehrere pro Person/Tag möglich)."""
    last_day = monthrange(year, month)[1]
    start_date = f"{year}-{month:02d}-01"
    end_date = f"{year}-{month:02d}-{last_day:02d}"

    response = (
        client.table("activities")
        .select("*")
        .gte("date", start_date)
        .lte("date", end_date)
        .order("created_at")
        .execute()
    )
    return response.data


def get_all_activities(client):
    """Holt ALLE Aktivitätsvorschläge, unabhängig vom Monat."""
    response = client.table("activities").select("*").order("created_at").execute()
    return response.data


def add_activity(client, entry_date: str, user_id: str, name: str, activity: str, activity_time: str = None):
    """Fügt einen NEUEN Aktivitätsvorschlag hinzu, ohne bestehende zu überschreiben.
    activity_time ist optional, Format 'HH:MM:SS' oder None."""
    client.table("activities").insert(
        {
            "date": entry_date,
            "user_id": user_id,
            "name": name,
            "activity": activity,
            "activity_time": activity_time,
        }
    ).execute()


def delete_activity(client, activity_id: int):
    """Löscht einen eigenen Aktivitätsvorschlag."""
    client.table("activities").delete().eq("id", activity_id).execute()


def delete_entry(client, entry_id: int):
    """Löscht einen Eintrag (RLS erlaubt das nur für den eigenen Eintrag)."""
    client.table("availability").delete().eq("id", entry_id).execute()


def get_votes_for_entries(client, entry_ids: list):
    """Holt alle Stimmen für eine Liste von Aktivitäts-Einträgen (IDs aus availability)."""
    if not entry_ids:
        return []
    response = (
        client.table("activity_votes")
        .select("*")
        .in_("activity_id", entry_ids)
        .execute()
    )
    return response.data


def add_vote(client, activity_id: int, voter_id: str):
    """Gibt eine Stimme für einen Aktivitätsvorschlag ab."""
    client.table("activity_votes").insert(
        {"activity_id": activity_id, "voter_id": voter_id}
    ).execute()


def remove_vote(client, activity_id: int, voter_id: str):
    """Nimmt die eigene Stimme wieder zurück."""
    client.table("activity_votes").delete().eq("activity_id", activity_id).eq(
        "voter_id", voter_id
    ).execute()
