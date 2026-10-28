import importlib.util, tempfile, threading, unittest, urllib.request, urllib.error, http.cookiejar, json
from pathlib import Path
spec=importlib.util.spec_from_file_location('accountserver',Path(__file__).parents[1]/'server'/'server.py');app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
class Accounts(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory();app.init_db(cls.tmp.name);app.create_user('teacher-one','test-only-password-A','Teacher','teacher');app.create_user('teacher-two','test-only-password-B','Other Teacher','teacher');cls.server=app.ThreadingHTTPServer(('127.0.0.1',0),app.Handler);cls.origin='http://127.0.0.1:'+str(cls.server.server_port);app.ORIGIN=cls.origin;threading.Thread(target=cls.server.serve_forever,daemon=True).start()
 @classmethod
 def tearDownClass(cls):cls.server.shutdown();cls.server.server_close();cls.tmp.cleanup()
 def client(self):return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
 def request(self,c,path,data=None,method=None,origin=True):
  headers={'Content-Type':'application/json'}
  if origin:headers['Origin']=self.origin
  req=urllib.request.Request(self.origin+'/api/'+path,data=json.dumps(data).encode() if data is not None else None,headers=headers,method=method)
  try:
   with c.open(req) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:
   with e:return e.code,json.load(e)
 def test_account_permissions_and_progress(self):
  teacher=self.client();student=self.client();other=self.client();guest=self.client()
  self.assertEqual(self.request(guest,'students')[0],403)
  self.assertEqual(self.request(teacher,'login',{'username':'teacher-one','password':'test-only-password-A'},origin=False)[0],403)
  self.assertEqual(self.request(teacher,'login',{'username':'teacher-one','password':'wrong'})[0],401)
  self.assertEqual(self.request(teacher,'login',{'username':'teacher-one','password':'test-only-password-A'})[0],200)
  code,d=self.request(teacher,'students',{'username':'student-001','label':'Learner 001','password':'student-test-password'});self.assertEqual(code,201);uid=d['id']
  self.assertEqual(self.request(student,'login',{'username':'student-001','password':'student-test-password'})[0],200)
  self.assertEqual(self.request(student,'students')[0],403)
  data={'target':50,'units':[{'attempts':0,'correct':0,'passed':False,'read':[],'history':[],'misses':[]} for _ in range(10)]}
  self.assertEqual(self.request(student,'progress',{'data':data,'revision':0},'PUT')[0],200)
  self.assertEqual(self.request(student,'progress',{'data':data,'revision':0},'PUT')[0],409)
  self.assertEqual(self.request(teacher,'progress')[1]['data'],None,'accounts must be isolated')
  self.assertEqual(self.request(teacher,'students')[1]['students'][0]['username'],'student-001')
  self.request(other,'login',{'username':'teacher-two','password':'test-only-password-B'})
  self.assertEqual(self.request(other,'students/reset',{'id':uid,'password':'new-student-password'})[0],404)
  self.assertEqual(self.request(teacher,'students/reset',{'id':uid,'password':'new-student-password'})[0],200)
  self.assertEqual(self.request(student,'progress')[0],401,'password reset invalidates old sessions')
  self.assertEqual(self.request(student,'login',{'username':'student-001','password':'new-student-password'})[0],200)
  self.assertEqual(self.request(student,'logout',{})[0],200)
  self.assertEqual(self.request(student,'progress')[0],401)
if __name__=='__main__':unittest.main()
