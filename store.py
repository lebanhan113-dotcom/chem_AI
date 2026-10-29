import copy
import json
import sqlite3
import threading
from datetime import datetime, timezone
from settings import DB_PATH
_lock = threading.RLock()

def now():
    return datetime.now(timezone.utc).isoformat()

def init():
    with _lock, sqlite3.connect(DB_PATH) as con:
        con.execute('CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, title TEXT NOT NULL, data TEXT NOT NULL, updated_at TEXT NOT NULL)')

def save(project):
    p=copy.deepcopy(project)
    p['updated_at']=now()
    with _lock, sqlite3.connect(DB_PATH, timeout=30) as con:
        con.execute('INSERT INTO projects(id,title,data,updated_at) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET title=excluded.title, data=excluded.data, updated_at=excluded.updated_at', (p['id'],p['title'],json.dumps(p,ensure_ascii=False),p['updated_at']))
    return p

def get(project_id):
    with _lock, sqlite3.connect(DB_PATH) as con:
        r=con.execute('SELECT data FROM projects WHERE id=?',(project_id,)).fetchone()
    return json.loads(r[0]) if r else None

def all_projects():
    with _lock, sqlite3.connect(DB_PATH) as con:
        rows=con.execute('SELECT data FROM projects ORDER BY updated_at DESC').fetchall()
    out=[]
    for (payload,) in rows:
        p=json.loads(payload)
        out.append({'id':p['id'],'title':p['title'],'subject':p['config']['subject'],'grade':p['config']['grade'],'status':p['status'],'step':p['step'],'updated_at':p['updated_at'],'total_scenes':len(p['scenes'])})
    return out

def file_dir(project_id):
    from settings import DATA_DIR
    p=(DATA_DIR / 'media' / project_id).resolve()
    p.mkdir(parents=True,exist_ok=True)
    return p
