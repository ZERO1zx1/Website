-- CodeCraft Academy: Supabase Auth profile and learning-progress foundation.
-- This migration changes only CodeCraft-owned tables and leaves the legacy public.users
-- table untouched because it belongs to a separate application domain.

create table if not exists public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  display_name text,
  role text not null default 'student' check (role in ('student', 'teacher', 'admin', 'owner')),
  locale text not null default 'mn',
  theme text not null default 'system' check (theme in ('light', 'dark', 'system')),
  created_at timestamptz not null default timezone('utc', now()),
  updated_at timestamptz not null default timezone('utc', now())
);

alter table public.profiles add column if not exists email text;
alter table public.profiles add column if not exists display_name text;
alter table public.profiles add column if not exists role text not null default 'student';
alter table public.profiles add column if not exists locale text not null default 'mn';
alter table public.profiles add column if not exists theme text not null default 'system';
alter table public.profiles add column if not exists created_at timestamptz not null default timezone('utc', now());
alter table public.profiles add column if not exists updated_at timestamptz not null default timezone('utc', now());

create table if not exists public.course_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  course_id text not null,
  progress_percent smallint not null default 0 check (progress_percent between 0 and 100),
  updated_at timestamptz not null default timezone('utc', now()),
  primary key (user_id, course_id)
);

create table if not exists public.lesson_progress (
  user_id uuid not null references auth.users(id) on delete cascade,
  course_id text not null,
  lesson_id text not null,
  completed_at timestamptz not null default timezone('utc', now()),
  primary key (user_id, course_id, lesson_id)
);

-- Existing projects may have created these tables before a primary key was added.
-- Unique indexes make the progress upserts deterministic without touching user records.
create unique index if not exists course_progress_user_course_key
  on public.course_progress (user_id, course_id);
create unique index if not exists lesson_progress_user_course_lesson_key
  on public.lesson_progress (user_id, course_id, lesson_id);
create index if not exists lesson_progress_user_course_idx
  on public.lesson_progress (user_id, course_id);

alter table public.profiles enable row level security;
alter table public.course_progress enable row level security;
alter table public.lesson_progress enable row level security;

-- Profiles are created server-side by the Auth trigger. Authenticated users can read
-- and update only their own account preferences.
drop policy if exists "CodeCraft profile select own" on public.profiles;
create policy "CodeCraft profile select own"
  on public.profiles for select to authenticated
  using ((select auth.uid()) = id);

drop policy if exists "CodeCraft profile update own" on public.profiles;
create policy "CodeCraft profile update own"
  on public.profiles for update to authenticated
  using ((select auth.uid()) = id)
  with check ((select auth.uid()) = id);

-- A user can only see or change learning progress belonging to their own Supabase Auth UUID.
drop policy if exists "CodeCraft course progress own" on public.course_progress;
create policy "CodeCraft course progress own"
  on public.course_progress for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

drop policy if exists "CodeCraft lesson progress own" on public.lesson_progress;
create policy "CodeCraft lesson progress own"
  on public.lesson_progress for all to authenticated
  using ((select auth.uid()) = user_id)
  with check ((select auth.uid()) = user_id);

-- Create/update a profile for any email/password, OTP, or Google OAuth user.
create or replace function public.handle_new_codecraft_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, email, display_name)
  values (
    new.id,
    new.email,
    coalesce(new.raw_user_meta_data ->> 'display_name', new.raw_user_meta_data ->> 'full_name', split_part(coalesce(new.email, ''), '@', 1))
  )
  on conflict (id) do update
    set email = excluded.email,
        display_name = coalesce(excluded.display_name, public.profiles.display_name),
        updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists on_auth_user_created_codecraft on auth.users;
create trigger on_auth_user_created_codecraft
  after insert on auth.users
  for each row execute procedure public.handle_new_codecraft_user();

create or replace function public.touch_codecraft_profile_updated_at()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  new.updated_at = timezone('utc', now());
  return new;
end;
$$;

drop trigger if exists on_codecraft_profile_updated on public.profiles;
create trigger on_codecraft_profile_updated
  before update on public.profiles
  for each row execute procedure public.touch_codecraft_profile_updated_at();
