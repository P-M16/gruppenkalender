# Gruppenkalender

Eine Streamlit-App für eine Gruppe: einloggen, auf einen Tag klicken und man
ist eingetragen. Je mehr Leute an einem Tag Zeit haben, desto deutlicher
wechselt die Farbe (blau → grün → gelb → rot), nicht nur die Helligkeit.
Optional kann eine Aktivität für den Tag vorgeschlagen werden.

## 1. Supabase-Projekt einrichten

1. Auf [supabase.com](https://supabase.com) kostenlos ein Konto/Projekt anlegen.
2. Im Dashboard unter **SQL Editor** den Inhalt von `supabase_schema.sql`
   einfügen und ausführen. Das legt die Tabelle `availability` inkl. Regeln an.
3. Unter **Authentication → Providers** ist "Email" standardmäßig aktiv – das
   reicht für Login/Registrierung per E-Mail + Passwort.
   - Für schnelles Testen: unter **Authentication → Settings** die Option
     "Confirm email" deaktivieren, damit man sich direkt nach der
     Registrierung einloggen kann (ohne Bestätigungsmail).
4. Unter **Project Settings → API** findest du:
   - `Project URL` → kommt in `SUPABASE_URL`
   - `anon public` Key → kommt in `SUPABASE_KEY`

## 2. Projekt lokal einrichten (VS Code)

```bash
cd gruppenkalender

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

`.env.example` zu `.env` kopieren und Zugangsdaten eintragen:

```bash
cp .env.example .env
```

```
SUPABASE_URL=https://dein-projekt.supabase.co
SUPABASE_KEY=dein-anon-key
```

## 3. App starten

```bash
streamlit run app.py
```

Beim ersten Öffnen: registrieren (Name, E-Mail, Passwort), dann einloggen.
Danach reicht ein Klick auf einen Tag, um sich einzutragen – nochmal klicken
trägt wieder aus. Unten kann optional eine Aktivität für den Tag gespeichert
werden.

## 4. Mit anderen teilen

Damit **mehrere Leute gleichzeitig** zugreifen können, muss die App gehostet
werden (lokal läuft sie nur auf deinem Rechner):

- **Streamlit Community Cloud** (streamlit.io/cloud) – GitHub-Repo verbinden,
  `SUPABASE_URL` und `SUPABASE_KEY` als Secrets/Umgebungsvariablen eintragen.
- Alternativ: Render, Railway, Fly.io o.ä.

Jede Person registriert sich einmal mit eigenem Account – danach ist beim
Login der eigene Name automatisch hinterlegt.

## Projektstruktur

```
gruppenkalender/
├── app.py                 # Streamlit-App (UI, Login, Kalenderlogik)
├── auth_service.py         # Supabase Auth (Login/Registrierung)
├── database.py             # Supabase-Datenbankzugriffe
├── requirements.txt
├── .env.example
├── supabase_schema.sql     # Tabellendefinition + Zugriffsregeln (RLS)
└── README.md
```

## Wie die Farbskala funktioniert

`color_for_count()` in `app.py` bildet die Anzahl der Personen an einem Tag
auf einen Farbton (Hue) zwischen Blau (wenig) und Rot (viel) ab – dadurch
wirkt der Wechsel bei jeder zusätzlichen Person deutlich sichtbar anders,
nicht nur ein bisschen dunkler. Die Skala passt sich automatisch an den
Monat an (bezogen auf den Tag mit den meisten Eintragungen).

## Mögliche Erweiterungen

- **Magic-Link-Login** statt Passwort (Supabase unterstützt das nativ).
- **Wochenansicht** zusätzlich zur Monatsansicht.
- **Schöneres Kalender-Widget**: Für ein noch hübscheres Layout z. B. die
  Community-Komponente `streamlit-calendar` einbinden.
