# Gruppenkalender

Eine Streamlit-App für eine Gruppe: einloggen, sehen wer wann Zeit hat, sich
selbst eintragen und Aktivitäten vorschlagen – inklusive Abstimmung, Wetter-
vorschau und dauerhafter Anmeldung.

Dieses Dokument richtet sich in erster Linie an **dich als Betreiber:in** der
App (Einrichtung, Hosting). Der Abschnitt ["Für deine Freunde/Nutzer:innen"](#für-deine-freundenutzerinnen)
ganz unten ist bewusst kurz gehalten – den kannst du ihnen bei Bedarf einfach
weiterleiten.

## Funktionen im Überblick

- **Login mit Supabase Auth** (E-Mail + Passwort). Einmal eingeloggt, bleibt
  man auch nach Schließen des Browsers angemeldet (Session wird über ein
  Cookie sicher wiederhergestellt).
- **Monats- und Wochenansicht** über eine echte Kalender-Komponente
  (FullCalendar), inklusive Vor/Zurück- und Heute-Navigation.
- Klick auf einen Tag zeigt Details; über einen eigenen Button trägt man sich
  ein bzw. wieder aus.
- **Aktivitätsvorschläge** sind unabhängig davon möglich, ob man an dem Tag
  Zeit hat – mehrere Vorschläge pro Tag und Person sind erlaubt.
- Optional kann zu einem Vorschlag eine **Uhrzeit** angegeben werden; mit
  Uhrzeit erscheint er in der Wochenansicht an der richtigen Zeitposition.
- Vorschläge können **abgestimmt** werden (👍); der Vorschlag mit den meisten
  Stimmen pro Tag wird automatisch farblich und fett hervorgehoben.
- **Wettervorschau** (Open-Meteo) direkt im Kalender und in der Detailansicht
  für die nächsten ca. 16 Tage (weiter in der Zukunft ist keine Vorhersage
  möglich).
- Dezentes, minimalistisches Design in Pastellgrün/-grau.

---

## Einmalige Einrichtung für App-Betreiber

### 1. Supabase-Projekt einrichten

1. Auf [supabase.com](https://supabase.com) kostenlos ein Konto/Projekt anlegen.
2. Im Dashboard unter **SQL Editor** den Inhalt von `supabase_schema.sql`
   einfügen und ausführen. Das legt die Tabellen `availability`, `activities`
   und `activity_votes` inkl. Zugriffsregeln (RLS) an.
3. Unter **Authentication → Providers** ist "Email" standardmäßig aktiv – das
   reicht für Login/Registrierung per E-Mail + Passwort.
   - Für schnelles Testen: unter **Authentication → Settings** die Option
     "Confirm email" deaktivieren, damit man sich direkt nach der
     Registrierung einloggen kann (ohne Bestätigungsmail).
4. Unter **Project Settings → API**:
   - `Project URL` → kommt in `SUPABASE_URL`
   - `anon public` Key → kommt in `SUPABASE_KEY`

### 2. Projekt lokal einrichten (VS Code)

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
WEATHER_CITY=Innsbruck
```

`WEATHER_CITY` ist der Ort, für den die Wettervorhersage im Kalender
angezeigt wird (für alle Nutzer:innen gleich).

### 3. App lokal testen

```bash
streamlit run app.py
```

### 4. Mit anderen teilen (hosten)

Damit **mehrere Leute gleichzeitig** zugreifen können, muss die App gehostet
werden:

- **Streamlit Community Cloud** (streamlit.io/cloud) – GitHub-Repo verbinden,
  `SUPABASE_URL`, `SUPABASE_KEY` und `WEATHER_CITY` als Secrets/
  Umgebungsvariablen eintragen.
- Alternativ: Render, Railway, Fly.io o.ä.


## Projektstruktur

```
gruppenkalender/
├── app.py                    # Streamlit-App (UI, Login, Kalenderlogik)
├── auth_service.py            # Supabase Auth (Login, Registrierung, Session-Refresh, Logout)
├── database.py                 # Supabase-Datenbankzugriffe (Termine, Aktivitäten, Stimmen)
├── weather_service.py          # Wettervorhersage über Open-Meteo
├── requirements.txt
├── .env.example
├── supabase_schema.sql         # Tabellendefinitionen + Zugriffsregeln (RLS)
└── README.md
```

## Design

Farben und Kalender-Buttons (Heute/Zurück/Vor/Monat/Woche) sind über
`custom_css` in `app.py` auf ein pastelliges Grün-/Grauschema abgestimmt,
statt der FullCalendar-Standardfarben. Die Personenzahl-Hintergrundfläche
(`color_for_count()`) und die Aktivitäts-Hervorhebung nutzen dieselbe Palette.

## Mögliche Erweiterungen

- **Eigene Farbe pro Person** statt nur Gruppenfarbe.
- Anzeige nur der Top-3-Aktivitäten pro Tag im Kalender, falls es mit der
  Zeit zu viele Vorschläge an einem Tag werden.

---

## Für Freunde/Nutzer:innen

1. Link öffnen, unter "Registrieren" Name, E-Mail und Passwort eingeben.
2. Danach einloggen – man bleibt angemeldet, auch nach Schließen des Browsers.
3. Auf einen Tag im Kalender klicken, um zu sehen wer Zeit hat und was
   geplant ist.
4. Über den Button "Ich habe an diesem Tag Zeit" eintragen bzw. austragen.
5. Aktivitätsvorschläge machen und für Vorschläge anderer abstimmen
