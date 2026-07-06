-- Im Supabase Dashboard unter "SQL Editor" ausführen

create table if not exists availability (
  id bigint generated always as identity primary key,
  date date not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  activity text,
  created_at timestamp with time zone default now(),
  unique (date, user_id)  -- pro Nutzer:in nur ein Eintrag pro Tag
);

-- Row Level Security aktivieren
alter table availability enable row level security;

-- Eingeloggte Nutzer:innen dürfen alle Einträge lesen (um zu sehen, wer Zeit hat)
create policy "Authenticated users can read all" on availability
  for select
  using (auth.role() = 'authenticated');

-- Nur eigene Einträge dürfen erstellt werden
create policy "Users can insert own entries" on availability
  for insert
  with check (auth.uid() = user_id);

-- Nur eigene Einträge dürfen bearbeitet werden (z.B. Aktivität ändern)
create policy "Users can update own entries" on availability
  for update
  using (auth.uid() = user_id);

-- Nur eigene Einträge dürfen gelöscht werden (Austragen)
create policy "Users can delete own entries" on availability
  for delete
  using (auth.uid() = user_id);


-- ---------- Aktivitätsvorschläge (mehrere pro Person und Tag möglich) ----------

create table if not exists activities (
  id bigint generated always as identity primary key,
  date date not null,
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  activity text not null,
  activity_time time,  -- optional, kann leer bleiben
  created_at timestamp with time zone default now()
);

-- Falls die Tabelle schon existiert (ohne diese Spalte), diese Zeile separat ausführen:
-- alter table activities add column if not exists activity_time time;

alter table activities enable row level security;

create policy "Authenticated users can read activities" on activities
  for select
  using (auth.role() = 'authenticated');

create policy "Users can insert own activities" on activities
  for insert
  with check (auth.uid() = user_id);

create policy "Users can delete own activities" on activities
  for delete
  using (auth.uid() = user_id);


-- ---------- Abstimmung über vorgeschlagene Aktivitäten ----------
-- Hinweis: activity_votes zeigt jetzt auf die neue activities-Tabelle
-- statt auf availability. Falls du activity_votes schon einmal angelegt
-- hattest, zuerst mit "drop table if exists activity_votes cascade;" löschen.

create table if not exists activity_votes (
  id bigint generated always as identity primary key,
  activity_id bigint not null references activities(id) on delete cascade,
  voter_id uuid not null references auth.users(id) on delete cascade,
  created_at timestamp with time zone default now(),
  unique (activity_id, voter_id)  -- pro Nutzer:in nur eine Stimme je Vorschlag
);

alter table activity_votes enable row level security;

create policy "Authenticated users can read votes" on activity_votes
  for select
  using (auth.role() = 'authenticated');

create policy "Users can vote" on activity_votes
  for insert
  with check (auth.uid() = voter_id);

create policy "Users can remove own vote" on activity_votes
  for delete
  using (auth.uid() = voter_id);
