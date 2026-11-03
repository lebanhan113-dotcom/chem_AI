/**
 * PHONG THI TRUC TUYEN - secure 3-service release orchestrator V11.7
 * 1) Authenticated Supabase admin calls publish with PUBLIC student index.html.
 * 2) Server writes a GitHub commit (uses GITHUB_TOKEN secret, not browser).
 * 3) GitHub-linked Vercel deploys the production branch automatically.
 * 4) Poll status; only after matching Git SHA, Vercel READY AND deployed HTML marker
 *    are verified will the new release become active in Supabase.
 * No automatic deletion of student data, Git history, or deployments needed for rollback.
 */
import { createClient } from 'npm:@supabase/supabase-js@2';

const cors = {
  'Access-Control-Allow-Origin': Deno.env.get('ALLOWED_ORIGIN') || '*',
  'Access-Control-Allow-Headers': 'authorization, apikey, content-type, x-client-info',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Content-Type': 'application/json; charset=utf-8',
  'Cache-Control': 'no-store',
};
function response(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), { status, headers: cors });
}
const env = (k: string) => (Deno.env.get(k) || '').trim();
const errText = async (r: Response) => `${r.status}: ${(await r.text()).slice(0,600)}`;
const GH = 'https://api.github.com';
const vPattern = /^V[0-9]+(?:\.[0-9]+){1,2}$/;
const GITHUB_OWNER = env('GITHUB_OWNER');
const GITHUB_REPO = env('GITHUB_REPO');
const GITHUB_BRANCH = env('GITHUB_BRANCH') || 'main';
const VERCEL_PROJECT_ID = env('VERCEL_PROJECT_ID');
const VERCEL_TEAM_ID = env('VERCEL_TEAM_ID');
const VERCEL_PRODUCTION_URL = env('VERCEL_PRODUCTION_URL').replace(/\/$/, '');

function safeConfig(html: string, version: string, publicUrl: string, publicKey: string) {
  if (!/const\s+PUBLIC_STUDENT_ONLY\s*=\s*true\s*;/.test(html)) {
    throw Error('Chi chap nhan index.html hoc sinh (PUBLIC_STUDENT_ONLY=true), khong tai ban quan tri len GitHub!');
  }
  if (!/<script[^>]*id="exam-data"[^>]*>\s*\{[^<]*"questions"\s*:\s*\[\s*\]/.test(html)) {
    throw Error('File student index.html con co du lieu de thi rieng; khong duoc cong khai.');
  }
  if (/id="original-word-embedded"/.test(html)) throw Error('File van chua tep Word rieng, khong duoc cong khai.');
  if (/sb_secret_[A-Za-z0-9_]{16,}|github_pat_[A-Za-z0-9_]{16,}|ghp_[A-Za-z0-9]{25,}/.test(html)) {
    throw Error('File chua chuoi co dang khoa bi mat, dung phat hanh.');
  }
  if (!/const\s+APP_VERSION\s*=\s*['"][^'"\n]*['"]\s*;/.test(html)) throw Error('Khong thay APP_VERSION');
  html = html.replace(/const\s+APP_VERSION\s*=\s*['"][^'"\n]*['"]\s*;/, `const APP_VERSION='${version}';`);
  if (!/<script\s+type="application\/json"\s+id="cloud-config">[\s\S]*?<\/script>/.test(html)) {
    throw Error('Khong thay cloud-config');
  }
  html = html.replace(/(<script\s+type="application\/json"\s+id="cloud-config">)[\s\S]*?(<\/script>)/,
    (_, a, b) => a + JSON.stringify({ url: publicUrl, anonKey: publicKey }).replace(/</g, '\\u003c') + b);
  html = html.replace(/<meta\s+name="hd-release-version"\s+content="[^"]*"\s*\/?\s*>/g, '');
  html = html.replace(/<head([^>]*)>/i, `<head$1>\n<meta name="hd-release-version" content="${version}">`);
  return html;
}
function toBase64(utf8: string) {
  const bytes = new TextEncoder().encode(utf8);
  // Avoid call stack overflow for large all-in-one MathJax HTML.
  let binary = '';
  for (let i = 0; i < bytes.length; i += 0x6000) {
    binary += String.fromCharCode(...bytes.subarray(i, i + 0x6000));
  }
  return btoa(binary);
}
function listEndpoint() {
  const u = new URL('https://api.vercel.com/v6/deployments');
  u.searchParams.set('projectId', VERCEL_PROJECT_ID);
  u.searchParams.set('target', 'production');
  u.searchParams.set('limit', '35');
  if (VERCEL_TEAM_ID) u.searchParams.set('teamId', VERCEL_TEAM_ID);
  return u.toString();
}
function exposed(row: Record<string, unknown>) {
  return {
    id: row.id, version: row.version,
    github: row.github_status, vercel: row.vercel_status, supabase: row.supabase_status,
    active: row.active, githubSha: row.github_sha,
    vercelUrl: row.vercel_url, error: row.error_detail,
    createdAt: row.created_at, completedAt: row.completed_at,
    githubUrl: `https://github.com/${GITHUB_OWNER}/${GITHUB_REPO}`,
    vercelDashboardUrl: 'https://vercel.com/dashboard',
    supabaseDashboardUrl: 'https://supabase.com/dashboard',
  };
}

Deno.serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response(null, { status: 204, headers: cors });
  if (req.method !== 'POST') return response({ error: 'POST only' }, 405);
  const origin = req.headers.get('origin') || '';
  if (env('ALLOWED_ORIGIN') && origin && origin !== env('ALLOWED_ORIGIN')) return response({error:'Origin not allowed'},403);
  const token = (req.headers.get('authorization') || '').replace(/^Bearer\s+/i, '').trim();
  if (!token) return response({ error: 'Chua dang nhap Supabase Auth' }, 401);
  const serverUrl = env('SUPABASE_URL');
  const serviceKey = env('SUPABASE_SERVICE_ROLE_KEY');
  if (!serverUrl || !serviceKey) return response({ error: 'Server missing Supabase credentials' }, 500);
  const db = createClient(serverUrl, serviceKey, { auth: { persistSession:false, autoRefreshToken:false } });
  const { data: auth, error: authErr } = await db.auth.getUser(token);
  if (authErr || !auth?.user?.id) return response({ error: 'Phien dang nhap da het han' }, 401);
  const uid = auth.user.id;
  const { data: admin, error: adminErr } = await db.from('app_admins').select('user_id').eq('user_id', uid).maybeSingle();
  if (adminErr || !admin) return response({ error: 'Khong co quyen quan tri server' }, 403);

  let body: Record<string, unknown>;
  try { body = await req.json(); } catch { return response({ error: 'JSON khong hop le' }, 400); }
  const action = String(body.action || 'status');
  try {
    if (action === 'publish') {
      const version = String(body.version || '').trim();
      if (!vPattern.test(version)) throw Error('Version phai co dang V11.6.1');
      if (!env('GITHUB_TOKEN') || !GITHUB_OWNER || !GITHUB_REPO || !VERCEL_PROJECT_ID || !env('VERCEL_TOKEN') || !VERCEL_PRODUCTION_URL) {
        throw Error('Chua cau hinh GITHUB_TOKEN/OWNER/REPO, VERCEL_TOKEN/PROJECT_ID/PRODUCTION_URL tren Edge Function Secrets');
      }
      const html = String(body.html || '');
      if (html.length < 5000 || html.length > 8_000_000) throw Error('Kich thuoc index.html khong hop le');
      const key = String(body.publicKey || '');
      const url = String(body.publicUrl || '').replace(/\/$/, '');
      if (url !== serverUrl || key.length < 20 || key.startsWith('sb_secret_')) throw Error('Cau hinh cong khai Supabase khong hop le');
      const content = safeConfig(html, version, url, key);
      const { data: exists } = await db.from('app_release_sync').select('id').eq('version', version).maybeSingle();
      if (exists) throw Error('Version da ton tai. Hay chon phien ban moi.');
      const { data: oldArchive, error: archiveErr } = await db.from('app_release_sync_archive').select('id').eq('version',version).maybeSingle();
      if (archiveErr) throw Error('Chua chay migration V11.7: ' + archiveErr.message);
      if (oldArchive) throw Error('Version nay da phat hanh truoc day; khong duoc tai su dung.');
      const { data: pending, error: insertErr } = await db.from('app_release_sync').insert({
        version, created_by: uid, github_status: 'pending', supabase_status: 'success', vercel_status:'pending'
      }).select('*').single();
      if (insertErr || !pending) throw Error('Supabase khong luu duoc bien ban phat hanh: '+(insertErr?.message||''));
      const githubHeaders = {
        'Authorization': `Bearer ${env('GITHUB_TOKEN')}`, 'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28', 'Content-Type':'application/json'
      };
      const ghPath = `${GH}/repos/${encodeURIComponent(GITHUB_OWNER)}/${encodeURIComponent(GITHUB_REPO)}/contents/index.html`;
      try {
        const oldResp = await fetch(ghPath+'?ref='+encodeURIComponent(GITHUB_BRANCH), { headers:githubHeaders });
        if (!oldResp.ok && oldResp.status !== 404) throw Error('Github GET: '+await errText(oldResp));
        const old = oldResp.ok ? await oldResp.json() : null;
        const bodyPut: Record<string,unknown> = {
          message:`release: phong thi Hon Dat ${version}`,
          content: toBase64(content), branch: GITHUB_BRANCH
        };
        if (old?.sha) bodyPut.sha = old.sha;
        const put = await fetch(ghPath, { method:'PUT', headers:githubHeaders, body:JSON.stringify(bodyPut) });
        if (!put.ok) throw Error('GitHub PUT: '+await errText(put));
        const pushed = await put.json();
        const sha = String(pushed?.commit?.sha || '');
        if (!/^[a-f0-9]{40}$/i.test(sha)) throw Error('GitHub khong tra commit SHA hop le');
        const {error:saveErr} = await db.from('app_release_sync').update({github_status:'success',github_sha:sha,error_detail:null}).eq('id',pending.id);
        if (saveErr) throw Error('Da push Github nhung khong ghi duoc trang thai: '+saveErr.message);
        return response({ ok:true, status:exposed({...pending,github_status:'success',github_sha:sha}), message:'Github da xac nhan commit; cho Vercel build.' });
      } catch (e) {
        await db.from('app_release_sync').update({github_status:'error',error_detail:String(e)}).eq('id',pending.id);
        throw e;
      }
    }
    if (action === 'status') {
      const id = String(body.id || '');
      let query = db.from('app_release_sync').select('*');
      if (id) query = query.eq('id',id); else query=query.order('created_at',{ascending:false}).limit(1);
      const {data:rows,error:loadErr} = await query;
      if (loadErr) throw Error(loadErr.message);
      const row = rows?.[0];
      if (!row) return response({ok:true,status:null});
      if (row.github_status === 'success' && row.vercel_status !== 'success') {
        if (!env('VERCEL_TOKEN') || !VERCEL_PROJECT_ID || !VERCEL_PRODUCTION_URL) return response({ok:true,status:exposed(row),warning:'Vercel chua cau hinh day du'});
        const resp = await fetch(listEndpoint(), { headers:{ Authorization:`Bearer ${env('VERCEL_TOKEN')}` } });
        if (!resp.ok) return response({ok:true,status:exposed(row),warning:'Khong doc duoc Vercel API: '+await errText(resp)});
        const deploys = (await resp.json()).deployments || [];
        const matching = deploys.find((d:Record<string,any>) => String(d.meta?.githubCommitSha || d.gitSource?.sha || '').toLowerCase()===String(row.github_sha).toLowerCase());
        if (matching?.readyState === 'ERROR' || matching?.readyState === 'CANCELED') {
          await db.from('app_release_sync').update({vercel_status:'error',error_detail:'Vercel build: '+matching.readyState}).eq('id',row.id);
          row.vercel_status='error';row.error_detail='Vercel build: '+matching.readyState;
        } else if (matching?.readyState === 'READY') {
          // Read deployed production content, not just an API acknowledgement.
          const site = await fetch(VERCEL_PRODUCTION_URL+'/?hd_release='+encodeURIComponent(row.version),{headers:{'Cache-Control':'no-cache'}});
          const txt = site.ok ? await site.text() : '';
          const match = txt.includes(`name="hd-release-version" content="${row.version}"`);
          if (match) {
            row.vercel_status='success'; row.vercel_deployment_id=matching.uid||matching.id||null;
            row.vercel_url=VERCEL_PRODUCTION_URL;
            const {error:upErr}=await db.from('app_release_sync').update({vercel_status:'success',vercel_deployment_id:row.vercel_deployment_id,vercel_url:VERCEL_PRODUCTION_URL}).eq('id',row.id);
            if (upErr) throw Error(upErr.message);
          }
        }
      }
      if (!row.active && row.github_status==='success' && row.vercel_status==='success' && row.supabase_status==='success') {
        const {error:actErr}=await db.rpc('hd_activate_release',{p_release_id:row.id});
        if (actErr) throw Error('Chua the chot ban phat hanh: '+actErr.message);
        // Re-query database: never report success based only on UI assumptions.
        const {data:checked,error:checkErr}=await db.from('app_release_sync').select('*').eq('id',row.id).maybeSingle();
        if (checkErr || !checked?.active) throw Error('Supabase chua xac nhan ban phat hanh dang hoat dong: '+(checkErr?.message||''));
        Object.assign(row,checked);
      }
      return response({ok:true,status:exposed(row)});
    }
    return response({error:'Unknown action'},400);
  } catch(e) {
    return response({error:String(e instanceof Error?e.message:e)},400);
  }
});
