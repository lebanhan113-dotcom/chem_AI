-- PHONG THI THPT HON DAT: VERSIONED RELEASE SYNC (V11.6)
-- Chay SAU khi da tao app_admins bang supabase_setup_v11.sql.
-- Chi luu trang thai phat hanh; KHONG xoa bai thi, diem, kho de hay lich su git.
create table if not exists public.app_release_sync (
  id uuid primary key default gen_random_uuid(),
  version text not null unique,
  created_at timestamptz not null default now(),
  completed_at timestamptz,
  created_by uuid not null references auth.users(id),
  github_status text not null default 'pending' check (github_status in ('pending','success','error')),
  github_sha text,
  vercel_status text not null default 'pending' check (vercel_status in ('pending','success','error')),
  vercel_deployment_id text,
  vercel_url text,
  supabase_status text not null default 'pending' check (supabase_status in ('pending','success','error')),
  active boolean not null default false,
  error_detail text,
  constraint release_state_consistency check (not active or (github_status='success' and vercel_status='success' and supabase_status='success'))
);
create unique index if not exists app_release_sync_one_active on public.app_release_sync(active) where active;
create index if not exists app_release_sync_created_idx on public.app_release_sync(created_at desc);
alter table public.app_release_sync enable row level security;
revoke all on public.app_release_sync from public, anon;
grant select on public.app_release_sync to authenticated;
drop policy if exists release_admin_read on public.app_release_sync;
create policy release_admin_read on public.app_release_sync for select to authenticated using (public.hd_is_admin());
-- Cap nhat release chi duoc thuc hien boi Edge Function voi quyen server.
revoke insert, update, delete on public.app_release_sync from authenticated;

create or replace function public.hd_activate_release(p_release_id uuid)
returns void language plpgsql security definer set search_path=public,pg_temp as $$
begin
  -- Khong cho phep goi truc tiep tu client: chi service_role.
  if auth.role() is distinct from 'service_role' then
     raise exception 'Server only';
  end if;
  if not exists (
    select 1 from public.app_release_sync
    where id=p_release_id and github_status='success' and vercel_status='success' and supabase_status='success'
  ) then
    raise exception 'Chua xac minh dong bo ba dich vu';
  end if;
  update public.app_release_sync set active=false where active;
  update public.app_release_sync set active=true, completed_at=now() where id=p_release_id;
  -- Khong xoa bai thi hoc sinh, phien ban de thi va lich su GitHub/Vercel.
end; $$;
revoke all on function public.hd_activate_release(uuid) from public, anon, authenticated;
grant execute on function public.hd_activate_release(uuid) to service_role;
