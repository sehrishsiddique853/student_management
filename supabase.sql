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

alter table public.students enable row level security;

drop policy if exists "Allow public read" on public.students;
create policy "Allow public read"
on public.students
for select
to anon
using (true);

drop policy if exists "Allow public insert" on public.students;
create policy "Allow public insert"
on public.students
for insert
to anon
with check (true);

drop policy if exists "Allow public update" on public.students;
create policy "Allow public update"
on public.students
for update
to anon
using (true)
with check (true);

drop policy if exists "Allow public delete" on public.students;
create policy "Allow public delete"
on public.students
for delete
to anon
using (true);

notify pgrst, 'reload schema';
