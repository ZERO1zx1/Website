-- Content Studio metadata for lessons and coding challenges.
-- Apply after 002_learning_platform.sql.

alter table public.problems add column if not exists slug text;
alter table public.problems add column if not exists content_type text not null default 'exercise';
alter table public.problems add column if not exists course_slug text;
alter table public.problems add column if not exists lesson_slug text;
alter table public.problems add column if not exists xp_reward integer not null default 80;
alter table public.problems add column if not exists status text not null default 'draft';
alter table public.problems add column if not exists explanation text not null default '';

update public.problems
set slug = coalesce(nullif(slug, ''), 'problem-' || id::text)
where slug is null or slug = '';

alter table public.problems drop constraint if exists problems_content_type_check;
alter table public.problems add constraint problems_content_type_check
    check (content_type in ('lesson', 'exercise', 'bug_lab', 'guided_project', 'portfolio_project'));

alter table public.problems drop constraint if exists problems_status_check;
alter table public.problems add constraint problems_status_check
    check (status in ('draft', 'review', 'published', 'archived'));

alter table public.problems drop constraint if exists problems_xp_reward_check;
alter table public.problems add constraint problems_xp_reward_check
    check (xp_reward >= 0 and xp_reward <= 5000);

create unique index if not exists problems_slug_unique_idx
    on public.problems (slug) where slug is not null;
create index if not exists problems_course_status_idx
    on public.problems (course_slug, status, content_type);
create index if not exists problems_lesson_idx
    on public.problems (lesson_slug);

comment on column public.problems.content_type is 'lesson, exercise, bug_lab, guided_project or portfolio_project';
comment on column public.problems.status is 'draft, review, published or archived';
