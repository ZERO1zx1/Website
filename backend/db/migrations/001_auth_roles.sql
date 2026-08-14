-- Codehaven authentication and role migration.
-- Run this migration before enabling the normal backend auth flow.

alter table if exists public.users
    add column if not exists password_hash text;

alter table if exists public.users
    add column if not exists requested_role text;

alter table if exists public.users
    add column if not exists teacher_approval_status text default 'approved';

update public.users
set teacher_approval_status = 'approved'
where teacher_approval_status is null;

alter table if exists public.users
    drop constraint if exists users_role_check;

alter table if exists public.users
    add constraint users_role_check
    check (role in ('owner', 'admin', 'teacher', 'student'));

alter table if exists public.users
    drop constraint if exists users_requested_role_check;

alter table if exists public.users
    add constraint users_requested_role_check
    check (requested_role is null or requested_role in ('teacher'));

create index if not exists users_teacher_approval_idx
    on public.users (requested_role, teacher_approval_status);

-- Existing plaintext passwords must not be copied into password_hash.
-- Force a password reset for legacy users before production login is enabled.
