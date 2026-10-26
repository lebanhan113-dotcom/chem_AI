-- Chạy trên Supabase SQL Editor. Không xóa hoặc ghi đè ngân hàng cũ.
create table if not exists public.eduplan_question_additions (
 id text primary key,
 fingerprint text not null unique,
 grade integer not null check (grade in (10,11,12)),
 chapter_no integer not null,
 lesson_id integer not null,
 part integer not null check (part between 1 and 4),
 content jsonb not null,
 answer jsonb not null,
 explanation text not null,
 source_title text not null,
 status text not null default 'approved' check(status in ('approved','blocked')),
 created_at timestamptz not null default now()
);
create index if not exists eduplan_additions_filter on public.eduplan_question_additions(grade,chapter_no,lesson_id,part,status);
alter table public.eduplan_question_additions enable row level security;
-- Không tạo policy cho anon/authenticated. Chỉ API máy chủ sử dụng service role.
revoke all on public.eduplan_question_additions from anon,authenticated;
