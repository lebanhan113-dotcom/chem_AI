-- PHÒNG THI A4: tất cả dữ liệu thi riêng tư. Chỉ Edge Function với secret được quyền đọc/ghi.
create extension if not exists pgcrypto;
create table if not exists public.app_profiles (
 id uuid primary key references auth.users(id) on delete cascade,
 role text not null default 'pending' check (role in ('pending','teacher','admin')),
 created_at timestamptz not null default now()
);
create or replace function public.create_profile_for_new_user() returns trigger language plpgsql security definer set search_path = '' as $$
begin insert into public.app_profiles(id,role) values (new.id,'pending') on conflict(id) do nothing; return new; end $$;
drop trigger if exists auth_user_created_profile on auth.users;
create trigger auth_user_created_profile after insert on auth.users for each row execute procedure public.create_profile_for_new_user();
create table if not exists public.exams (
 id uuid primary key default gen_random_uuid(), owner_uid uuid not null references auth.users(id),
 title text not null, subject text not null default 'Hóa học', grade text not null default '', topic text not null default '',
 source_file text, source_storage_path text, status text not null default 'draft' check (status in ('draft','published')),
 revision integer not null default 1, created_at timestamptz not null default now(), updated_at timestamptz not null default now()
);
create table if not exists public.exam_questions (
 id uuid primary key, exam_id uuid not null references public.exams(id) on delete cascade,
 position int not null, section text not null, type text not null check(type in ('mcq','tf','short','essay')),
 body text not null, options jsonb not null default '[]', statements jsonb not null default '[]', media jsonb not null default '[]',
 points numeric not null check(points>=0), answer jsonb, grading jsonb not null default '{}', rubric text,
 approved boolean not null default false, issues jsonb not null default '[]',
 unique(exam_id, position)
);
create table if not exists public.exam_versions (
 id uuid primary key default gen_random_uuid(), exam_id uuid not null references public.exams(id) on delete cascade,
 revision int not null, snapshot jsonb not null, created_at timestamptz not null default now(),
 unique(exam_id,revision)
);
create table if not exists public.exam_rooms (
 id uuid primary key default gen_random_uuid(), exam_id uuid not null references public.exams(id),
 owner_uid uuid not null references auth.users(id), code text not null unique,
 starts_at timestamptz not null, ends_at timestamptz not null,
 duration_minutes int not null check(duration_minutes between 1 and 300),
 active boolean not null default true, created_at timestamptz not null default now()
);
create table if not exists public.exam_attempts (
 id uuid primary key default gen_random_uuid(), room_id uuid not null references public.exam_rooms(id) on delete cascade,
 student_name text not null, student_class text not null, token_hash text not null unique,
 started_at timestamptz not null default now(), deadline_at timestamptz not null,
 submitted_at timestamptz, status text not null default 'active' check(status in ('active','submitted')),
 answers jsonb not null default '{}', auto_score numeric, final_score numeric, grading_details jsonb,
 teacher_notes text, created_at timestamptz not null default now()
);
create index if not exists idx_attempts_room on public.exam_attempts(room_id);
create index if not exists idx_exams_owner on public.exams(owner_uid);
create index if not exists idx_rooms_owner on public.exam_rooms(owner_uid);
-- Chặn mọi truy cập trực tiếp qua REST dù biết ID; Edge Function kiểm tra mọi quyền trước khi dùng secret.
alter table public.app_profiles enable row level security;
alter table public.exams enable row level security;
alter table public.exam_questions enable row level security;
alter table public.exam_versions enable row level security;
alter table public.exam_rooms enable row level security;
alter table public.exam_attempts enable row level security;
revoke all on public.app_profiles, public.exams, public.exam_questions, public.exam_versions, public.exam_rooms, public.exam_attempts from anon, authenticated;
-- KHÔNG tạo policy public trả đáp án. Chỉ service_role được quyền truy vấn.
-- Save revision inside one SQL transaction to avoid half-updated exams.
create or replace function public.save_exam_revision(p_owner uuid,p_exam_id uuid,p_meta jsonb,p_questions jsonb)
returns uuid language plpgsql security invoker set search_path = public as $$
declare v_id uuid; v_revision integer; v_q jsonb;
begin
 if p_exam_id is null then
   insert into public.exams(owner_uid,title,subject,grade,topic,source_file)
   values(p_owner,p_meta->>'title',coalesce(p_meta->>'subject','Hóa học'),coalesce(p_meta->>'grade',''),coalesce(p_meta->>'topic',''),p_meta->>'source_file') returning id,revision into v_id,v_revision;
 else
   select id,revision into v_id,v_revision from public.exams where id=p_exam_id and owner_uid=p_owner for update;
   if not found then raise exception 'Không tìm thấy đề hoặc không có quyền'; end if;
   if exists(select 1 from public.exam_rooms where exam_id=v_id) then raise exception 'Đề đã có phòng thi; hãy sao chép đề để chỉnh sửa'; end if;
   v_revision := v_revision+1;
   update public.exams set title=p_meta->>'title',subject=coalesce(p_meta->>'subject','Hóa học'),grade=coalesce(p_meta->>'grade',''),
     topic=coalesce(p_meta->>'topic',''),source_file=p_meta->>'source_file',revision=v_revision,updated_at=now() where id=v_id;
   delete from public.exam_questions where exam_id=v_id;
 end if;
 for v_q in select value from jsonb_array_elements(p_questions) loop
   insert into public.exam_questions(id,exam_id,position,section,type,body,options,statements,media,points,answer,grading,rubric,approved,issues)
   values((v_q->>'id')::uuid,v_id,(v_q->>'position')::integer,v_q->>'section',v_q->>'type',v_q->>'body',
      coalesce(v_q->'options','[]'::jsonb),coalesce(v_q->'statements','[]'::jsonb),coalesce(v_q->'media','[]'::jsonb),
      coalesce((v_q->>'points')::numeric,0),v_q->'answer',coalesce(v_q->'grading','{}'::jsonb),v_q->>'rubric',coalesce((v_q->>'approved')::boolean,false),coalesce(v_q->'issues','[]'::jsonb));
 end loop;
 insert into public.exam_versions(exam_id,revision,snapshot) values(v_id,v_revision,jsonb_build_object('meta',p_meta,'questions',p_questions));
 return v_id;
end $$;
revoke all on function public.save_exam_revision(uuid,uuid,jsonb,jsonb) from public,anon,authenticated;
grant execute on function public.save_exam_revision(uuid,uuid,jsonb,jsonb) to service_role;

-- Private file bucket for teachers' uploaded .docx originals.
insert into storage.buckets (id,name,public,file_size_limit,allowed_mime_types)
values ('exam-sources','exam-sources',false,6291456,array['application/vnd.openxmlformats-officedocument.wordprocessingml.document'])
on conflict(id) do nothing;
