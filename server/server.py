"""Optional single-host account server. Serve behind HTTPS for remote students.
Run with APP_ORIGIN=https://your-domain.example and a persistent FOOTPATH_DATA directory.
Create teacher interactively: python3 server/server.py --create-teacher
"""
import argparse, functools, getpass, hashlib, hmac, json, os, re, secrets, sqlite3, time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from http.cookies import SimpleCookie
ROOT=Path(__file__).resolve().parents[1]
DATA=Path(os.environ.get('FOOTPATH_DATA',ROOT/'server'/'data'))
ORIGIN=os.environ.get('APP_ORIGIN','http://127.0.0.1:4174').rstrip('/')
SECURE=ORIGIN.startswith('https://')
DB=None
ATTEMPTS={}

def connect():
 c=sqlite3.connect(DB,timeout=10);c.row_factory=sqlite3.Row;return c

def init_db(directory=DATA):
 global DB
 directory=Path(directory);directory.mkdir(parents=True,exist_ok=True,mode=0o700);DB=directory/'footpath.sqlite3'
 with connect() as c:
  c.executescript('''CREATE TABLE IF NOT EXISTS users(id TEXT PRIMARY KEY,username TEXT UNIQUE NOT NULL,label TEXT NOT NULL,role TEXT NOT NULL,salt BLOB NOT NULL,password BLOB NOT NULL,owner TEXT,active INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,user_id TEXT NOT NULL,expires INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS progress(user_id TEXT PRIMARY KEY,data TEXT NOT NULL,revision INTEGER NOT NULL DEFAULT 1);
''')
 os.chmod(DB,0o600)

def password_hash(password,salt):
 return hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1,dklen=32)

def create_user(username,password,label,role,owner=None):
 if not re.fullmatch('[a-zA-Z0-9_-]{3,40}',username):raise ValueError('Use a 3–40 character ID with letters, digits, _ or -.')
 if not isinstance(password,str) or len(password)<10 or len(password)>200:raise ValueError('Use a password of 10–200 characters.')
 if not isinstance(label,str) or not 1<=len(label)<=60:raise ValueError('Use a short display label, preferably a student ID.')
 salt=secrets.token_bytes(16);uid=secrets.token_urlsafe(16);digest=password_hash(password,salt)
 with connect() as c:c.execute('INSERT INTO users(id,username,label,role,salt,password,owner) VALUES(?,?,?,?,?,?,?)',(uid,username.lower(),label,role,salt,digest,owner))
 return uid

def valid_progress(d):
 if not isinstance(d,dict) or d.get('target') not in (50,60):return False
 units=d.get('units')
 if not isinstance(units,list) or len(units)!=10:return False
 for u in units:
  if not isinstance(u,dict) or type(u.get('attempts')) is not int or not 0<=u['attempts']<=1000000:return False
  if type(u.get('correct')) is not int or not 0<=u['correct']<=u['attempts']:return False
  if not isinstance(u.get('misses'),list) or any(not isinstance(s,str) for s in u['misses']) or not isinstance(u.get('history'),list):return False
  if type(u.get('passed')) is not bool or not isinstance(u.get('read'),list) or any(type(i)is not int or i not in (0,1,2) for i in u['read']):return False
 return True

class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist'),**kwargs)
 def log_message(self,fmt,*args):pass  # Do not log IDs, passwords, answers or session values.
 def end_headers(self):
  self.send_header('X-Content-Type-Options','nosniff');self.send_header('Referrer-Policy','same-origin');self.send_header('X-Frame-Options','SAMEORIGIN')
  if SECURE:self.send_header('Strict-Transport-Security','max-age=31536000')
  super().end_headers()
 def send_json(self,status,body,cookie=None):
  data=json.dumps(body,ensure_ascii=False).encode();self.send_response(status);self.send_header('Content-Type','application/json; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('Content-Length',str(len(data)))
  if cookie:self.send_header('Set-Cookie',cookie)
  self.end_headers();self.wfile.write(data)
 def user(self):
  cookie=SimpleCookie()
  try:cookie.load(self.headers.get('Cookie',''));token=cookie.get('footpath_session');token=token.value if token else ''
  except:return None
  if not token:return None
  key=hashlib.sha256(token.encode()).hexdigest()
  with connect() as c:return c.execute('SELECT u.* FROM sessions s JOIN users u ON u.id=s.user_id WHERE s.token=? AND s.expires>? AND u.active=1',(key,int(time.time()))).fetchone()
 def safe_user(self,u):return {k:u[k] for k in ['id','username','label','role']}
 def read_body(self):
  n=int(self.headers.get('Content-Length','0'))
  if n<=0 or n>250000:raise ValueError('Invalid request size.')
  if 'application/json' not in self.headers.get('Content-Type',''):raise ValueError('JSON required.')
  return json.loads(self.rfile.read(n))
 def do_GET(self):
  if self.path=='/api/me':
   u=self.user();return self.send_json(200,{'user':self.safe_user(u) if u else None})
  if self.path=='/api/progress':
   u=self.user()
   if not u:return self.send_json(401,{'error':'Please sign in.'})
   with connect() as c:r=c.execute('SELECT data,revision FROM progress WHERE user_id=?',(u['id'],)).fetchone()
   return self.send_json(200,{'data':json.loads(r['data']) if r else None,'revision':r['revision'] if r else 0})
  if self.path=='/api/students':
   u=self.user()
   if not u or u['role']!='teacher':return self.send_json(403,{'error':'Teacher access required.'})
   with connect() as c:rows=c.execute('SELECT u.id,u.username,u.label,u.active,p.data FROM users u LEFT JOIN progress p ON u.id=p.user_id WHERE u.owner=? ORDER BY u.username',(u['id'],)).fetchall()
   students=[]
   for r in rows:
    d=json.loads(r['data']) if r['data'] else {};units=d.get('units',[]);students.append({'id':r['id'],'username':r['username'],'label':r['label'],'active':bool(r['active']),'attempts':sum(x.get('attempts',0) for x in units),'mastered':sum(bool(x.get('passed')) for x in units)})
   return self.send_json(200,{'students':students})
  if self.path.startswith('/api/'):return self.send_json(404,{'error':'Unknown endpoint.'})
  return super().do_GET()
 def do_POST(self):self.mutate('POST')
 def do_PUT(self):self.mutate('PUT')
 def mutate(self,method):
  # Exact same-origin requirement provides CSRF protection; no cross-origin API access.
  if self.headers.get('Origin')!=ORIGIN:return self.send_json(403,{'error':'Origin rejected. Check APP_ORIGIN.'})
  try:d=self.read_body()
  except (ValueError,TypeError,json.JSONDecodeError):return self.send_json(400,{'error':'Invalid JSON request.'})
  if not isinstance(d,dict):return self.send_json(400,{'error':'A JSON object is required.'})
  u=self.user()
  try:
   if self.path=='/api/login' and method=='POST':
    username=d.get('username','');pw=d.get('password','')
    if not isinstance(username,str) or not isinstance(pw,str) or len(username)>40 or len(pw)>200:return self.send_json(400,{'error':'Invalid login.'})
    now=time.time();ip=self.client_address[0];key=(ip,username.lower());recent=[t for t in ATTEMPTS.get(key,[]) if now-t<900];global_key=(ip,'*');ip_recent=[t for t in ATTEMPTS.get(global_key,[]) if now-t<900]
    if len(recent)>=10 or len(ip_recent)>=60:return self.send_json(429,{'error':'Too many attempts. Try again in 15 minutes.'})
    ATTEMPTS[key]=recent+[now];ATTEMPTS[global_key]=ip_recent+[now]
    if len(ATTEMPTS)>5000:
     for k in list(ATTEMPTS):
      if not ATTEMPTS[k] or now-ATTEMPTS[k][-1]>900:del ATTEMPTS[k]
    with connect() as c:r=c.execute('SELECT * FROM users WHERE username=? AND active=1',(username.lower(),)).fetchone()
    salt=r['salt'] if r else b'footpath-dummy-00';digest=password_hash(pw,salt)
    if not r or not hmac.compare_digest(digest,r['password']):return self.send_json(401,{'error':'Student ID or password is incorrect.'})
    token=secrets.token_urlsafe(32);hashed=hashlib.sha256(token.encode()).hexdigest()
    with connect() as c:
     c.execute('DELETE FROM sessions WHERE expires<?',(int(now),));c.execute('INSERT INTO sessions VALUES(?,?,?)',(hashed,r['id'],int(now)+86400))
    ATTEMPTS.pop(key,None)
    cookie=f'footpath_session={token}; Path=/; HttpOnly; SameSite=Strict; Max-Age=86400'+('; Secure' if SECURE else '')
    return self.send_json(200,{'user':self.safe_user(r)},cookie)
   if self.path=='/api/logout' and method=='POST':
    cookie=SimpleCookie();cookie.load(self.headers.get('Cookie',''));t=cookie.get('footpath_session')
    if t:
     with connect() as c:c.execute('DELETE FROM sessions WHERE token=?',(hashlib.sha256(t.value.encode()).hexdigest(),))
    return self.send_json(200,{'ok':True},'footpath_session=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0'+('; Secure' if SECURE else ''))
   if not u:return self.send_json(401,{'error':'Please sign in.'})
   if self.path=='/api/progress' and method=='PUT':
    data=d.get('data');rev=d.get('revision')
    if not valid_progress(data) or type(rev)is not int:return self.send_json(400,{'error':'Invalid progress data.'})
    with connect() as c:
     c.execute('BEGIN IMMEDIATE');r=c.execute('SELECT revision FROM progress WHERE user_id=?',(u['id'],)).fetchone();actual=r['revision'] if r else 0
     if actual!=rev:return self.send_json(409,{'error':'Progress changed on another device. Reload the account before saving again.'})
     newrev=actual+1;c.execute('INSERT INTO progress VALUES(?,?,?) ON CONFLICT(user_id) DO UPDATE SET data=excluded.data,revision=excluded.revision',(u['id'],json.dumps(data),newrev))
    return self.send_json(200,{'revision':newrev})
   if self.path=='/api/students' and method=='POST':
    if u['role']!='teacher':return self.send_json(403,{'error':'Teacher access required.'})
    uid=create_user(d.get('username'),d.get('password'),d.get('label'),'student',u['id']);return self.send_json(201,{'id':uid})
   if self.path=='/api/students/reset' and method=='POST':
    if u['role']!='teacher':return self.send_json(403,{'error':'Teacher access required.'})
    pw=d.get('password');uid=d.get('id')
    if not isinstance(pw,str) or not 10<=len(pw)<=200:return self.send_json(400,{'error':'Password must have 10–200 characters.'})
    salt=secrets.token_bytes(16);digest=password_hash(pw,salt)
    with connect() as c:
     r=c.execute('SELECT id FROM users WHERE id=? AND owner=?',(uid,u['id'])).fetchone()
     if not r:return self.send_json(404,{'error':'Student not found.'})
     c.execute('UPDATE users SET salt=?,password=? WHERE id=?',(salt,digest,uid));c.execute('DELETE FROM sessions WHERE user_id=?',(uid,))
    return self.send_json(200,{'ok':True})
   return self.send_json(404,{'error':'Unknown endpoint.'})
  except sqlite3.IntegrityError:return self.send_json(409,{'error':'That student ID already exists.'})
  except (ValueError,TypeError):return self.send_json(400,{'error':'Check the ID, label and password requirements.'})

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--create-teacher',action='store_true');p.add_argument('--port',type=int,default=4174);p.add_argument('--bind',default='127.0.0.1');args=p.parse_args();init_db()
 if args.create_teacher:
  username=input('Teacher ID: ');label=input('Display label: ');pw=getpass.getpass('Password (10+ characters): ');confirm=getpass.getpass('Repeat password: ')
  if pw!=confirm:raise SystemExit('Passwords differ.')
  create_user(username,pw,label,'teacher');print('Teacher created. No password is stored in plain text.')
 else:
  print(f'English Footpath server: {ORIGIN}. Keep behind an HTTPS reverse proxy for remote use.');ThreadingHTTPServer((args.bind,args.port),Handler).serve_forever()
