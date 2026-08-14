-- Codehaven starter content for a new Supabase project.
-- Apply after migrations 001, 002 and 003. Safe to re-run for the same titles.

insert into public.courses (title, description, created_by)
select 'Python foundations', 'Learn Python syntax, data structures, functions and practical problem solving.', null
where not exists (select 1 from public.courses where title = 'Python foundations');

insert into public.courses (title, description, created_by)
select 'HTML & CSS responsive web', 'Build semantic, accessible and responsive pages with modern HTML and CSS.', null
where not exists (select 1 from public.courses where title = 'HTML & CSS responsive web');

do $$
declare
    python_course_id bigint;
    web_course_id bigint;
    python_module_id bigint;
    web_module_id bigint;
    even_problem_id bigint;
    unique_problem_id bigint;
    skill_python_id bigint;
    skill_web_id bigint;
begin
    select id into python_course_id from public.courses where title = 'Python foundations' order by id limit 1;
    select id into web_course_id from public.courses where title = 'HTML & CSS responsive web' order by id limit 1;

    insert into public.modules (course_id, title, description, position, status)
    select python_course_id, 'Python essentials', 'Variables, types and control flow.', 1, 'published'
    where not exists (select 1 from public.modules where course_id = python_course_id and position = 1);
    insert into public.modules (course_id, title, description, position, status)
    select python_course_id, 'Functions and clean code', 'Scope, arguments and reusable patterns.', 2, 'published'
    where not exists (select 1 from public.modules where course_id = python_course_id and position = 2);
    insert into public.modules (course_id, title, description, position, status)
    select python_course_id, 'Collections and comprehensions', 'Lists, dictionaries and expressive iteration.', 3, 'published'
    where not exists (select 1 from public.modules where course_id = python_course_id and position = 3);

    insert into public.modules (course_id, title, description, position, status)
    select web_course_id, 'HTML structure', 'Semantic elements, forms and accessible markup.', 1, 'published'
    where not exists (select 1 from public.modules where course_id = web_course_id and position = 1);
    insert into public.modules (course_id, title, description, position, status)
    select web_course_id, 'CSS layout systems', 'Box model, Flexbox, Grid and responsive rules.', 2, 'published'
    where not exists (select 1 from public.modules where course_id = web_course_id and position = 2);

    select id into python_module_id from public.modules where course_id = python_course_id and position = 1;
    insert into public.lessons (module_id, title, content, position, estimated_minutes)
    select python_module_id, 'Variables and control flow', 'Learn the core building blocks of Python programs.', 1, 20
    where not exists (select 1 from public.lessons where module_id = python_module_id and position = 1);

    select id into web_module_id from public.modules where course_id = web_course_id and position = 1;
    insert into public.lessons (module_id, title, content, position, estimated_minutes)
    select web_module_id, 'Semantic HTML', 'Use meaningful landmarks, headings and labels.', 1, 20
    where not exists (select 1 from public.lessons where module_id = web_module_id and position = 1);

    insert into public.skills (name, description, category)
    values ('Python', 'Python programming fundamentals.', 'programming')
    on conflict (name) do nothing;
    insert into public.skills (name, description, category)
    values ('Web fundamentals', 'Semantic HTML and responsive CSS.', 'frontend')
    on conflict (name) do nothing;

    select id into skill_python_id from public.skills where name = 'Python';
    select id into skill_web_id from public.skills where name = 'Web fundamentals';

    insert into public.problems (title, description, difficulty, starter_code, explanation, language)
    select 'Even number filter', 'Return only the even numbers from a list while keeping the original order.', 'easy',
           'def even_numbers(values):\n    return []\n\nprint(even_numbers([1, 2, 3, 4]))',
           'Use a list comprehension or a loop with a modulo check.', 'python'
    where not exists (select 1 from public.problems where title = 'Even number filter');

    insert into public.problems (title, description, difficulty, starter_code, explanation, language)
    select 'First unique character', 'Find the first character that occurs exactly once in a string.', 'medium',
           'def first_unique(value):\n    return None',
           'Count characters first, then scan the original string in order.', 'python'
    where not exists (select 1 from public.problems where title = 'First unique character');

    select id into even_problem_id from public.problems where title = 'Even number filter' order by id limit 1;
    select id into unique_problem_id from public.problems where title = 'First unique character' order by id limit 1;

    insert into public.test_cases (problem_id, input, expected_output, is_hidden)
    select even_problem_id, '', '[2, 4]', false
    where not exists (select 1 from public.test_cases where problem_id = even_problem_id and expected_output = '[2, 4]');
    insert into public.test_cases (problem_id, input, expected_output, is_hidden)
    select even_problem_id, '', '[]', true
    where not exists (select 1 from public.test_cases where problem_id = even_problem_id and expected_output = '[]');
    insert into public.test_cases (problem_id, input, expected_output, is_hidden)
    select unique_problem_id, '', 'a', false
    where not exists (select 1 from public.test_cases where problem_id = unique_problem_id and expected_output = 'a');

    insert into public.problem_skills (problem_id, skill_id)
    select even_problem_id, skill_python_id
    where not exists (select 1 from public.problem_skills where problem_id = even_problem_id and skill_id = skill_python_id);
    insert into public.problem_skills (problem_id, skill_id)
    select unique_problem_id, skill_python_id
    where not exists (select 1 from public.problem_skills where problem_id = unique_problem_id and skill_id = skill_python_id);
end $$;
