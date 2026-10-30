-- A4: Teacher self-registration by verified email + private admin invitation.
-- Apply AFTER 202610300001_init.sql. Never publish this table via anon/authenticated REST.
create table if not exists public.teacher_invites (
  email text primary key check (email = lower(btrim(email)) and length(email) between 5 and 254),
  display_name text not null default '',
  invited_by uuid references auth.users(id) on delete set null,
  active boolean not null default true,
  created_at timestamptz not null default now(),
  expires_at timestamptz not null default (now() + interval '30 days'),
  claimed_by uuid references auth.users(id) on delete set null,
  claimed_at timestamptz
);
create index if not exists idx_teacher_invites_claimed_by on public.teacher_invites(claimed_by);
alter table public.teacher_invites enable row level security;
revoke all on public.teacher_invites from public, anon, authenticated;

-- Auth email confirmations can happen AFTER signup (auth.users UPDATE). Grant the
-- teacher role only after the invitation's exact email has been confirmed.
create or replace function public.claim_verified_teacher_invite()
returns trigger language plpgsql security definer set search_path = '' as $$
declare invited public.teacher_invites%rowtype;
begin
  if new.email is null or new.email_confirmed_at is null then return new; end if;
  select * into invited from public.teacher_invites
   where email=lower(btrim(new.email)) and active
     and expires_at>now()
     and (claimed_by is null or claimed_by=new.id)
   for update;
  if not found then return new; end if;
  insert into public.app_profiles(id, role)
    values (new.id,'teacher')
    on conflict(id) do update set role=case
      when public.app_profiles.role='admin' then 'admin'
      else 'teacher' end;
  update public.teacher_invites
    set claimed_by=new.id, claimed_at=coalesce(claimed_at,now())
    where email=invited.email;
  return new;
end $$;
revoke all on function public.claim_verified_teacher_invite() from public, anon, authenticated;
drop trigger if exists teacher_claim_invite_on_confirmation on auth.users;
create trigger teacher_claim_invite_on_confirmation
  after insert or update of email_confirmed_at, email on auth.users
  for each row execute function public.claim_verified_teacher_invite();

-- Called ONLY by the Edge Function's service-role client after verifying an
-- administrator. Covers already-confirmed accounts invited after signup.
create or replace function public.activate_teacher_by_invite(p_email text)
returns uuid language plpgsql security definer set search_path = '' as $$
declare v_email text := lower(btrim(p_email)); v_user uuid;
begin
  if not exists (select 1 from public.teacher_invites
    where email=v_email and active and expires_at>now() and claimed_by is null) then
    return null;
  end if;
  select id into v_user from auth.users
    where lower(btrim(email))=v_email and email_confirmed_at is not null limit 1;
  if v_user is null then return null; end if;
  insert into public.app_profiles(id,role) values(v_user,'teacher')
    on conflict(id) do update set role=case
      when public.app_profiles.role='admin' then 'admin' else 'teacher' end;
  update public.teacher_invites set claimed_by=v_user,claimed_at=now()
    where email=v_email and claimed_by is null;
  return v_user;
end $$;
revoke all on function public.activate_teacher_by_invite(text) from public,anon,authenticated;
grant execute on function public.activate_teacher_by_invite(text) to service_role;
