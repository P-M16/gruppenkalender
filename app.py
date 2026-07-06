import streamlit as st
import calendar
from datetime import date, datetime, time as dt_time, timedelta
import pandas as pd
from streamlit_calendar import calendar as st_calendar

from auth_service import sign_up, sign_in, get_authenticated_client
import database as db

st.set_page_config(page_title="Gruppenkalender", page_icon="📅", layout="wide")

MONTH_NAMES_DE = [
    "", "Januar", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]
WEEKDAY_NAMES_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]

# ---------- Session State ----------
if "year" not in st.session_state:
    st.session_state.year = date.today().year
if "month" not in st.session_state:
    st.session_state.month = date.today().month
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None
if "auth" not in st.session_state:
    st.session_state.auth = None  # dict mit access_token, refresh_token, user_id, name, email


# ---------- Login / Registrierung ----------
def render_login():
    st.title("📅 Gruppenkalender")
    st.caption("Melde dich an, um zu sehen wer wann Zeit hat und dich selbst einzutragen.")

    tab_login, tab_signup = st.tabs(["Login", "Registrieren"])

    with tab_login:
        with st.form("login_form"):
            email = st.text_input("E-Mail")
            password = st.text_input("Passwort", type="password")
            submitted = st.form_submit_button("Einloggen", use_container_width=True)
            if submitted:
                try:
                    result = sign_in(email, password)
                    user = result.user
                    session = result.session
                    full_name = (user.user_metadata or {}).get("full_name") or email.split("@")[0]
                    st.session_state.auth = {
                        "access_token": session.access_token,
                        "refresh_token": session.refresh_token,
                        "user_id": user.id,
                        "name": full_name,
                        "email": email,
                    }
                    st.rerun()
                except Exception as e:
                    st.error(f"Login fehlgeschlagen: {e}")

    with tab_signup:
        with st.form("signup_form"):
            name = st.text_input("Dein Name")
            email = st.text_input("E-Mail", key="signup_email")
            password = st.text_input("Passwort (mind. 6 Zeichen)", type="password", key="signup_password")
            submitted = st.form_submit_button("Registrieren", use_container_width=True)
            if submitted:
                if not name.strip():
                    st.warning("Bitte gib deinen Namen ein.")
                else:
                    try:
                        sign_up(email, password, name.strip())
                        st.success(
                            "Registrierung erfolgreich! Falls in Supabase E-Mail-Bestätigung "
                            "aktiviert ist, bestätige zuerst deine E-Mail, bevor du dich einloggst."
                        )
                    except Exception as e:
                        st.error(f"Registrierung fehlgeschlagen: {e}")


if not st.session_state.auth:
    try:
        render_login()
    except ValueError as e:
        st.error(str(e))
        st.info("Trage SUPABASE_URL und SUPABASE_KEY in die .env Datei ein (siehe README.md).")
    st.stop()

auth = st.session_state.auth

try:
    client = get_authenticated_client(auth["access_token"], auth["refresh_token"])
except Exception as e:
    st.error(f"Sitzung ungültig, bitte erneut einloggen: {e}")
    st.session_state.auth = None
    st.stop()

# ---------- Sidebar ----------
with st.sidebar:
    st.write(f"👤 Angemeldet als **{auth['name']}**")
    if st.button("Logout"):
        st.session_state.auth = None
        st.session_state.selected_date = None
        st.rerun()

st.title("📅 Gruppenkalender")
st.caption("Klick auf einen Tag, um Details zu sehen. Mit dem Button unten trägst du dich ein.")

# ---------- Daten laden ----------
try:
    entries = db.get_all_entries(client)
    activity_entries = db.get_all_activities(client)
except Exception as e:
    st.error(f"Verbindung zur Datenbank fehlgeschlagen: {e}")
    st.stop()

df = pd.DataFrame(entries) if entries else pd.DataFrame(columns=["id", "date", "user_id", "name", "activity"])
if not df.empty:
    df["date"] = df["date"].astype(str)

df_activities = pd.DataFrame(activity_entries) if activity_entries else pd.DataFrame(
    columns=["id", "date", "user_id", "name", "activity"]
)
if not df_activities.empty:
    df_activities["date"] = df_activities["date"].astype(str)

counts = df.groupby("date").size().to_dict() if not df.empty else {}
max_count = max(counts.values()) if counts else 1


def color_for_count(count: int, max_count: int) -> str:
    """Dezente, pastellige Grünskala: je mehr Personen Zeit haben, desto
    kräftiger (aber immer noch ruhig) das Grün."""
    if count == 0:
        return "#f6f7f6"
    ratio = min(count / max_count, 1.0)
    lightness = 92 - 32 * ratio  # 92% (sehr hell) bis 60% (kräftiger)
    return f"hsl(150, 40%, {lightness:.0f}%)"


# ---------- Kalender ----------
today_str = date.today().isoformat()


def to_bold_unicode(text: str) -> str:
    """Wandelt normalen Text in fett aussehende Unicode-Zeichen um.
    Funktioniert unabhängig von CSS, da es echte (andere) Zeichen sind."""
    result = []
    for ch in text:
        if "A" <= ch <= "Z":
            result.append(chr(0x1D5D4 + (ord(ch) - ord("A"))))
        elif "a" <= ch <= "z":
            result.append(chr(0x1D5EE + (ord(ch) - ord("a"))))
        elif "0" <= ch <= "9":
            result.append(chr(0x1D7EC + (ord(ch) - ord("0"))))
        else:
            result.append(ch)  # z.B. Umlaute/Sonderzeichen bleiben unverändert
    return "".join(result)


events = []
for date_str, count in counts.items():
    bg_color = color_for_count(count, max_count)
    is_mine = not df.empty and ((df["date"] == date_str) & (df["user_id"] == auth["user_id"])).any()

    # Farbfläche über den ganzen Tag
    events.append(
        {
            "start": date_str,
            "end": date_str,
            "display": "background",
            "backgroundColor": bg_color,
            "allDay": True,
        }
    )
    # Sichtbares Label mit Anzahl (+ Häkchen falls man selbst eingetragen ist)
    label = f"{count} Person" + ("en" if count != 1 else "") + (" ✓" if is_mine else "")
    events.append(
        {
            "title": label,
            "start": date_str,
            "allDay": True,
            "backgroundColor": "transparent",
            "borderColor": "transparent",
            "textColor": "#1a1a1a",
        }
    )

# Aktivitätsvorschläge zusätzlich als eigene Zeilen unter der Personenzahl anzeigen
if not df_activities.empty:
    all_activity_ids = df_activities["id"].astype(int).tolist()
    all_votes = db.get_votes_for_entries(client, all_activity_ids)
    all_votes_df = (
        pd.DataFrame(all_votes) if all_votes else pd.DataFrame(columns=["activity_id", "voter_id"])
    )
    all_vote_counts = (
        all_votes_df.groupby("activity_id").size().to_dict() if not all_votes_df.empty else {}
    )

    for date_str, group in df_activities.groupby("date"):
        group_votes = group["id"].astype(int).map(all_vote_counts).fillna(0)
        day_max_votes = group_votes.max()

        for (_, row), vote_count in zip(group.iterrows(), group_votes):
            is_top = day_max_votes > 0 and vote_count == day_max_votes

            event = {
                "title": to_bold_unicode(row["activity"]) if is_top else row["activity"],
                "backgroundColor": "#bfe3cf" if is_top else "#eaf3ee",
                "borderColor": "#8fc9a8" if is_top else "#d3e5da",
                "textColor": "#1f3d2c" if is_top else "#3f5449",
            }

            activity_time = row.get("activity_time")
            if activity_time and not pd.isna(activity_time):
                start_dt = datetime.strptime(f"{date_str} {activity_time}", "%Y-%m-%d %H:%M:%S")
                end_dt = start_dt + timedelta(hours=1)
                event["start"] = start_dt.isoformat()
                event["end"] = end_dt.isoformat()
                event["allDay"] = False
            else:
                event["start"] = date_str
                event["allDay"] = True

            events.append(event)

calendar_options = {
    "initialView": "dayGridMonth",
    "initialDate": date.today().isoformat(),
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth,timeGridWeek"},
    "locale": "de",
    "height": 650,
    "fixedWeekCount": False,
    "firstDay": 1,
}

cal_result = st_calendar(
    events=events,
    options=calendar_options,
    key="group_calendar",
)

clicked_date = None
if cal_result:
    if cal_result.get("callback") == "dateClick":
        clicked_date = cal_result["dateClick"]["date"][:10]
    elif cal_result.get("callback") == "eventClick":
        clicked_date = cal_result["eventClick"]["event"]["start"][:10]

if clicked_date and clicked_date != st.session_state.selected_date:
    st.session_state.selected_date = clicked_date
    st.rerun()

st.divider()

# ---------- Detailansicht für ausgewählten Tag ----------
if st.session_state.selected_date:
    sel = st.session_state.selected_date
    sel_display = datetime.strptime(sel, "%Y-%m-%d").strftime("%A, %d.%m.%Y")
    st.subheader(sel_display)

    day_entries = df[df["date"] == sel] if not df.empty else pd.DataFrame()
    my_current_entry = (
        day_entries[day_entries["user_id"] == auth["user_id"]]
        if not day_entries.empty
        else pd.DataFrame()
    )
    is_registered = not my_current_entry.empty

    if is_registered:
        if st.button("Eingetragen – hier klicken zum Austragen", use_container_width=True, type="secondary"):
            db.delete_entry(client, int(my_current_entry.iloc[0]["id"]))
            st.rerun()
    else:
        if st.button("Ich habe an diesem Tag Zeit", use_container_width=True, type="primary"):
            db.add_entry(client, sel, auth["user_id"], auth["name"])
            st.rerun()

    st.write("")

    day_activities = df_activities[df_activities["date"] == sel] if not df_activities.empty else pd.DataFrame()

    col_people, col_activities = st.columns(2)

    with col_people:
        st.markdown(f"**Wer Zeit hat ({len(day_entries)})**")
        if not day_entries.empty:
            for _, row in day_entries.iterrows():
                st.write(row["name"])
        else:
            st.caption("Noch niemand eingetragen.")

    with col_activities:
        st.markdown("**Aktivitäten**")

        if not day_activities.empty:
            activities = day_activities.copy()
            activity_ids = activities["id"].astype(int).tolist()
            votes = db.get_votes_for_entries(client, activity_ids)
            votes_df = pd.DataFrame(votes) if votes else pd.DataFrame(columns=["activity_id", "voter_id"])

            vote_counts = (
                votes_df.groupby("activity_id").size().to_dict() if not votes_df.empty else {}
            )
            my_votes = (
                set(votes_df[votes_df["voter_id"] == auth["user_id"]]["activity_id"])
                if not votes_df.empty
                else set()
            )

            activities["votes"] = activities["id"].astype(int).map(vote_counts).fillna(0).astype(int)
            activities = activities.sort_values("votes", ascending=False)

            for _, row in activities.iterrows():
                activity_id = int(row["id"])
                already_voted = activity_id in my_votes
                is_mine = row["user_id"] == auth["user_id"]

                c1, c2, c3 = st.columns([5, 1, 1])
                time_val = row.get("activity_time")
                time_prefix = f"{str(time_val)[:5]} · " if time_val and not pd.isna(time_val) else ""
                c1.write(f"{time_prefix}{row['activity']}")
                c1.caption(f"von {row['name']} · {row['votes']} Stimme(n)")
                vote_label = "👍" if not already_voted else "✅"
                if c2.button(vote_label, key=f"vote_{activity_id}"):
                    if already_voted:
                        db.remove_vote(client, activity_id, auth["user_id"])
                    else:
                        db.add_vote(client, activity_id, auth["user_id"])
                    st.rerun()
                if is_mine:
                    if c3.button("🗑️", key=f"del_act_{activity_id}"):
                        db.delete_activity(client, activity_id)
                        st.rerun()
        else:
            st.caption("Noch keine Aktivität vorgeschlagen.")

    st.write("---")
    st.write("**Neuen Aktivitätsvorschlag hinzufügen**")
    st.caption("Das geht unabhängig davon, ob du an diesem Tag Zeit hast.")
    with st.form("activity_form", clear_on_submit=True):
        new_activity = st.text_input("Aktivität", placeholder="z.B. Bouldern, Wandern, Kino...")
        col_check, col_time = st.columns([1, 2])
        with col_check:
            st.write("")
            set_time = st.checkbox("Uhrzeit festlegen")
        with col_time:
            new_time = st.time_input("Uhrzeit (optional)", value=dt_time(18, 0))
        if st.form_submit_button("Vorschlag hinzufügen"):
            if new_activity.strip():
                time_str = new_time.strftime("%H:%M:%S") if set_time else None
                db.add_activity(client, sel, auth["user_id"], auth["name"], new_activity.strip(), time_str)
                st.success("Vorschlag hinzugefügt!")
                st.rerun()
            else:
                st.warning("Bitte einen Vorschlag eingeben.")
else:
    st.info("Klicke auf einen Tag im Kalender, um Details zu sehen.")
