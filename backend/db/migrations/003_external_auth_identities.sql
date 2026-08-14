-- Codehaven external-auth identity migration.
-- Apply after 001_auth_roles.sql and 002_learning_platform.sql.
-- OTP and Google OAuth users are linked to public.users without replacing app roles.

alter table if exists public.users
    add column if not exists auth_user_id uuid;

alter table if exists public.users
    add column if not exists auth_provider text;

alter table if exists public.users
    add column if not exists avatar_url text;

alter table if exists public.users
    drop constraint if exists users_auth_provider_check;

alter table if exists public.users
    add constraint users_auth_provider_check
    check (auth_provider is null or auth_provider in ('email', 'google'));

create unique index if not exists users_auth_user_id_uidx
    on public.users (auth_user_id)
    where auth_user_id is not null;

create index if not exists users_auth_provider_idx
    on public.users (auth_provider);
