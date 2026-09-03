create table if not exists public.students (
    id bigint generated always as identity primary key,
    name text not null,
    email text not null unique,
    age integer,
    course text,
    created_at timestamptz not null default now()
);

alter table public.students
add column if not exists age integer;

notify pgrst, 'reload schema';
