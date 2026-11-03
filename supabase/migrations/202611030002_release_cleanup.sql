-- THPT HON DAT V11.7: keep only the newest verified release in the active table.
-- Older release records are moved into a private audit archive, not erased from history.
-- Exam versions, student submissions, source code history, and rollback deployments
-- are intentionally untouched.

create table if not exists public.app_release_sync_archive (
  id uuid primary key,
  version text not null unique,
  created_at timestamptz,
  completed_at timestamptz,
  created_by uuid,
  github_status text,
  github_sha text,
  vercel_status text,
  vercel_deployment_id text,
  vercel_url text,
  supabase_status text,
  active boolean,
  error_detail text,
  archived_at timestamptz not null default now(),
  archive_reason text not null default 'replaced_by_new_verified_release'
);
alter table public.app_release_sync_archive enable row level security;
revoke all on public.app_release_sync_archive from public, anon, authenticated;
grant select on public.app_release_sync_archive to authenticated;
drop policy if exists archived_release_admin_read on public.app_release_sync_archive;
create policy archived_release_admin_read on public.app_release_sync_archive
  for select to authenticated using (public.hd_is_admin());

create or replace function public.hd_activate_release(p_release_id uuid)
returns void language plpgsql security definer set search_path=public,pg_temp as $$
begin
  if auth.role() is distinct from 'service_role' then
    raise exception 'Server only';
  end if;
  if not exists (
    select 1 from public.app_release_sync
    where id=p_release_id and github_status='success'
      and vercel_status='success' and supabase_status='success'
  ) then
    raise exception 'Chua xac minh dong bo ba dich vu';
  end if;
  -- A single transaction: if archive/cleanup fails, activation rolls back.
  update public.app_release_sync set active=false where active;
  update public.app_release_sync
    set active=true,completed_at=now()
    where id=p_release_id;
  insert into public.app_release_sync_archive (
    id,version,created_at,completed_at,created_by,github_status,github_sha,
    vercel_status,vercel_deployment_id,vercel_url,supabase_status,active,
    error_detail,archived_at,archive_reason
  )
  select id,version,created_at,completed_at,created_by,github_status,github_sha,
    vercel_status,vercel_deployment_id,vercel_url,supabase_status,active,
    error_detail,now(),'replaced_by_' || (select version from public.app_release_sync where id=p_release_id)
  from public.app_release_sync where id<>p_release_id
  on conflict (id) do nothing;
  delete from public.app_release_sync where id<>p_release_id;
end; $$;
revoke all on function public.hd_activate_release(uuid) from public, anon, authenticated;
grant execute on function public.hd_activate_release(uuid) to service_role;
