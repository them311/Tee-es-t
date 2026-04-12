-- StudentFlow — Supabase schema
-- Run this in the Supabase SQL editor once.
-- Idempotent: safe to run multiple times.

create extension if not exists "uuid-ossp";

-- ---------- offers ----------
create table if not exists offers (
    id            uuid primary key default uuid_generate_v4(),
    source        text not null,
    source_id     text not null,
    title         text not null,
    description   text default '',
    company       text default '',
    city          text default '',
    remote        boolean not null default false,
    contract      text not null default 'other',
    hours_per_week integer,
    skills        text[] default '{}',
    starts_on     date,
    ends_on       date,
    url           text default '',
    scraped_at    timestamptz not null default now(),
    unique (source, source_id)
);

create index if not exists idx_offers_scraped_at on offers (scraped_at desc);
create index if not exists idx_offers_city on offers (city);
create index if not exists idx_offers_contract on offers (contract);

-- ---------- students ----------
create table if not exists students (
    id                 uuid primary key default uuid_generate_v4(),
    email              text not null unique,
    full_name          text default '',
    city               text default '',
    remote_ok          boolean not null default true,
    skills             text[] default '{}',
    accepted_contracts text[] default '{}',
    max_hours_per_week integer not null default 20,
    available_from     date,
    available_until    date,
    active             boolean not null default true,
    created_at         timestamptz not null default now()
);

create index if not exists idx_students_active on students (active);
create index if not exists idx_students_city on students (city);

-- ---------- matches ----------
create table if not exists matches (
    id          uuid primary key default uuid_generate_v4(),
    offer_id    uuid not null references offers(id) on delete cascade,
    student_id  uuid not null references students(id) on delete cascade,
    score       numeric(5, 4) not null,
    reasons     text[] default '{}',
    created_at  timestamptz not null default now(),
    notified_at timestamptz,
    unique (offer_id, student_id)
);

create index if not exists idx_matches_unnotified on matches (notified_at)
    where notified_at is null;
create index if not exists idx_matches_student on matches (student_id);
create index if not exists idx_matches_offer on matches (offer_id);

-- ---------- notifications ----------
create table if not exists notifications (
    id          uuid primary key default uuid_generate_v4(),
    match_id    uuid not null references matches(id) on delete cascade,
    channel     text not null default 'webhook',
    payload     jsonb default '{}'::jsonb,
    sent_at     timestamptz not null default now(),
    succeeded   boolean not null default true,
    error       text
);

create index if not exists idx_notifications_match on notifications (match_id);

-- ---------- RLS ----------
-- Enable RLS. Policies are intentionally strict: all writes go through the
-- service role (agents + API), never a client token.
alter table offers enable row level security;
alter table students enable row level security;
alter table matches enable row level security;
alter table notifications enable row level security;

-- Students can read their own row and their own matches (via a future client
-- token). Add such policies when you wire the mobile app.
