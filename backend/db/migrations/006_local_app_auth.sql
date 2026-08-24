-- CodeCraft-owned authentication identity. Apply after 003_external_auth_identities.sql.
-- Supabase remains the database only; auth.users is no longer required for new users.
alter table public.users
    add column if not exists password_hash text;
alter table public.users
    add column if not exists auth_user_id uuid;
alter table public.users
    add column if not exists auth_provider text;

create table if not exists public.app_auth_identities (
    id uuid primary key,
    email text not null unique,
    provider text not null default 'password' check (provider in ('password', 'google')),
    provider_subject text,
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (provider, provider_subject)
);

-- Preserve existing UUID-backed learner rows before changing their foreign keys.
insert into public.app_auth_identities (id, email, provider)
select p.id,
       coalesce(nullif(p.email, ''), 'legacy-' || p.id::text || '@local.invalid'),
       'password'
from public.profiles p
on conflict (id) do nothing;

insert into public.app_auth_identities (id, email, provider)
select u.auth_user_id,
       coalesce(nullif(u.email, ''), 'legacy-' || u.auth_user_id::text || '@local.invalid'),
       case when u.auth_provider = 'google' then 'google' else 'password' end
from public.users u
where u.auth_user_id is not null
on conflict (id) do nothing;

alter table public.users
    drop constraint if exists users_auth_user_id_fkey;
alter table public.users
    drop constraint if exists users_auth_provider_check;
alter table public.users
    add constraint users_auth_provider_check
    check (auth_provider is null or auth_provider in ('email', 'google'));
alter table public.users
    add constraint users_auth_user_id_app_fkey
    foreign key (auth_user_id) references public.app_auth_identities(id) on delete set null;

alter table public.profiles
    drop constraint if exists profiles_id_fkey;
alter table public.profiles
    add constraint profiles_id_app_auth_fkey
    foreign key (id) references public.app_auth_identities(id) on delete cascade;

alter table public.course_progress
    drop constraint if exists course_progress_user_id_fkey;
alter table public.course_progress
    add constraint course_progress_user_id_app_auth_fkey
    foreign key (user_id) references public.app_auth_identities(id) on delete cascade;

alter table public.lesson_progress
    drop constraint if exists lesson_progress_user_id_fkey;
alter table public.lesson_progress
    add constraint lesson_progress_user_id_app_auth_fkey
    foreign key (user_id) references public.app_auth_identities(id) on delete cascade;

alter table public.quiz_attempts
    drop constraint if exists quiz_attempts_user_id_fkey;
alter table public.quiz_attempts
    add constraint quiz_attempts_user_id_app_auth_fkey
    foreign key (user_id) references public.app_auth_identities(id) on delete cascade;

create index if not exists app_auth_provider_subject_idx
    on public.app_auth_identities(provider, provider_subject);

comment on table public.app_auth_identities is 'CodeCraft-owned identity records; not Supabase Auth users.';
comment on column public.users.password_hash is 'Werkzeug password hash for CodeCraft-owned email/password auth.';
