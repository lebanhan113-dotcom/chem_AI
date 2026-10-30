// One-time administrative setup, run by the Supabase project owner only.
// No credential is stored in this source file or included in the Vercel build.
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';
export const ADMIN_EMAIL = 'lebanhan113@gmail.com';

function checkURL(url) {
  let u;
  try { u = new URL(url); } catch { throw Error('Project URL khong hop le'); }
  if (u.protocol !== 'https:' || !u.hostname.endsWith('.supabase.co') || u.username || u.password || u.search || u.hash || u.pathname !== '/') {
    throw Error('Chi chap nhan URL https cua du an *.supabase.co');
  }
  return u.origin;
}

function headersFor(key) {
  if (!key || key.startsWith('sb_publishable_')) throw Error('Can secret key phia may chu, khong dung publishable key');
  if (!(key.startsWith('sb_secret_') || key.split('.').length === 3)) throw Error('Secret key khong dung dinh dang');
  const headers = { apikey: key, 'Content-Type': 'application/json' };
  if (!key.startsWith('sb_secret_')) headers.Authorization = `Bearer ${key}`;
  return headers;
}

async function apiJson(fetcher,url,init) {
  const res = await fetcher(url,init);
  let body = {};
  try { body = await res.json(); } catch {}
  if (!res.ok) {
    // Do not echo raw error details, which might include credentials.
    throw Error(`Supabase API tra ve HTTP ${res.status}; kiem tra log trong Supabase`);
  }
  return body;
}

export async function provisionAdmin({url,secretKey,password,resetExisting=false,fetcher=fetch}) {
  const origin = checkURL(url);
  const headers = headersFor(secretKey);
  if (typeof password !== 'string' || password.length < 12) {
    throw Error('Mat khau can it nhat 12 ky tu');
  }
  const email = ADMIN_EMAIL;
  let user = null;
  for (let page=1; page<=100; page++) {
    const r = await apiJson(fetcher,`${origin}/auth/v1/admin/users?page=${page}&per_page=200`,{headers});
    const users = Array.isArray(r.users) ? r.users : [];
    user = users.find(x=>String(x.email||'').toLowerCase()===email) || null;
    if (user || users.length<200) break;
  }
  let created = false;
  if (!user) {
    const createdRow = await apiJson(fetcher,`${origin}/auth/v1/admin/users`,{
      method:'POST',headers,body:JSON.stringify({email,password,email_confirm:true,user_metadata:{full_name:'Lê Bá Nhẫn'}})
    });
    user = createdRow.user || createdRow;
    created = true;
  } else if (!user.email_confirmed_at) {
    throw Error('Tai khoan da ton tai nhung email chua duoc xac minh; hay xac minh trong Supabase Auth truoc');
  } else if (resetExisting) {
    user = await apiJson(fetcher,`${origin}/auth/v1/admin/users/${encodeURIComponent(user.id)}`,{
      method:'PUT',headers,body:JSON.stringify({password})
    });
    user = user.user || user;
  }
  const uid = user?.id;
  if (!/^[a-f0-9-]{36}$/i.test(String(uid||''))) {
    throw Error('Khong nhan duoc User ID hop le tu Supabase Auth');
  }
  const changed = await apiJson(fetcher,`${origin}/rest/v1/app_profiles?on_conflict=id`,{
    method:'POST',headers:{...headers,Prefer:'resolution=merge-duplicates,return=representation'},
    body:JSON.stringify({id:uid,role:'admin'})
  });
  if (!Array.isArray(changed) || !changed.some(x=>x.id===uid && x.role==='admin')) {
    throw Error('Chua xac nhan duoc quyen admin; kiem tra migration SQL va bang app_profiles');
  }
  return {created,reset:(!created && resetExisting),email,role:'admin',id:uid};
}

const isMain = Boolean(process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url));
if (isMain) {
  const readline = await import('node:readline');
  const { stdin,stdout } = process;
  if (!stdin.isTTY || !stdout.isTTY) {
    console.error('Hay chay trong cua so PowerShell/Terminal tuong tac (khong truyen mat khau qua argv).');
    process.exit(1);
  }
  const rl=readline.createInterface({input:stdin,output:stdout});
  const ask=q=>new Promise(resolve=>rl.question(q,resolve));
  // The prompt is masked to avoid printing password/secret in terminal history.
  const askSecret=q=>new Promise((resolve,reject)=>{
    rl.pause();stdout.write(q);let result='';
    stdin.setRawMode(true);stdin.resume();
    const onData=chunk=>{
      for (const ch of chunk.toString('utf8')) {
        if (ch==='\u0003') {cleanup();reject(Error('Da huy'));return;}
        if (ch==='\r'||ch==='\n') {stdout.write('\n');cleanup();resolve(result);return;}
        if (ch==='\u007f'||ch==='\b') {result=result.slice(0,-1);continue;}
        result+=ch;
      }
    };
    function cleanup(){stdin.off('data',onData);stdin.setRawMode(false);stdin.pause();rl.resume();}
    stdin.on('data',onData);
  });
  try {
    console.log('THIET LAP QUAN TRI VIEN - chi thuc hien tu may cua chu du an');
    console.log('Email quan tri:', ADMIN_EMAIL);
    const url=(await ask('Project URL (https://...supabase.co): ')).trim();
    const secretKey=await askSecret('Supabase SECRET key / service_role (nhap an): ');
    const password=await askSecret('Mat khau quan tri (nhap an, it nhat 12 ky tu): ');
    const confirm=await askSecret('Nhap lai mat khau: ');
    if (password!==confirm) throw Error('Hai mat khau khong khop');
    const reset=(await ask('Neu tai khoan da ton tai, co dat lai mat khau? (y/N): ')).trim().toLowerCase()==='y';
    if ((await ask('Xac nhan du an da chay SQL migration A4 va ban la chu du an? (go YES): ')).trim()!=='YES') throw Error('Da huy');
    const result=await provisionAdmin({url,secretKey,password,resetExisting:reset});
    console.log(`HOAN THANH: ${result.email} duoc cap role admin. ${result.created?'Da tao tai khoan moi.':'Tai khoan da ton tai.'}`);
    console.log('Dang nhap tai website Vercel -> GIAO VIEN. Doi mat khau neu da tung chia se.');
  } catch(e) {console.error('KHONG THE HOAN THANH:',e.message);process.exitCode=1;}
  finally {rl.close();}
}
