#!/user/sbin/env python 

import tornado.httpserver 
import tornado.ioloop
import tornado.options
import tornado.websocket
import tornado.web
import os
from uuid import uuid4
import json
import MySQLdb
from tornado.options import define,options
define("port",default=8080,help="run on the given port",type=int)

class SayHi(object):
    def say(self):
        print "test import "
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('username',None)
        
class IndexHandler(BaseHandler):
    def get(self):
        data  = [1,2,3,4,5,]
        autoescape = 'helloS'
        print self.get_current_user()
        cur = self.application.db.cursor()
        id = 1
        cur.execute("""select * from Host where id = %s""",id)
        print cur.fetchall()
        cur.close()
        self.render('index.html',data=data,autoescape=autoescape)
        
class reNameHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,name):
        self.write('hello,'+name);
        
class showHi(tornado.web.RequestHandler):
    def get(self,title):
        self.render('index.html')
        
class PoemPageHandler(tornado.web.RequestHandler):
    def post(self):
        
        noun1 = self.get_argument('noun1')
        noun2 = self.get_argument('noun2')
        verb = self.get_argument('verb')
        noun3 = self.get_argument('noun3')
        self.render('poem.html',roads=noun1,wood=noun2,made=verb,difference=noun3)
        
class chatIndexHandler(tornado.web.RequestHandler):
    def get(self):
        session = uuid4()
        self.render("webwechat.html",session=session)

    def post(self):
        data = {}
        data['session'] = self.get_argument('session')
        data['message'] = self.get_argument('argument')
        self.application.webDataHandler.on_message(data)
        
class webDataHandler(object):
    loginuser = []
    callbacks = []
        
    def tologin(self,session,callback):
        data = {}
        data['action']='login'
        data['data'] = session
        if ( session not in self.loginuser):
            print "TO login:%s" %session
            self.loginuser.append(session)
            self.callbacks.append(callback)
            print "%s,%s" %(self.loginuser,self.callbacks)
            self.notify(data)
        else:
            pass
            
    def tologout(self,session,callback):
        data = {}
        data['action']='logout'
        data['data']=session
        print "To logout user:%s" %session
        self.loginuser.remove(session)
        self.callbacks.remove(callback)
        print "%s,%s" %(self.loginuser,self.callbacks)
        self.notify(data)
    
    def on_message(self,getdata):
        self.notify(getdata)
        
    def notify(self,data):
        try:
            for callback in self.callbacks:
                callback(json.dumps(data))
        except:
            pass
            
class wechatServer(tornado.websocket.WebSocketHandler):
    
    def open(self):
        print "Have a new user login"
        
    def on_close(self):
        #self.application.webDataHandler.tologout(self.session,self.callback)
        try:
            print "Have a user logout,sessuion:%s and close !" %self.session
            self.application.webDataHandler.tologout(self.session,self.callback)
        except:
            print "close!"
        
    def on_message(self,message):
        print "Get Message:"+ message
        message = json.loads(message)
        if message['action'] == 'login':
            print "login user:%s" %message['data']
            self.application.webDataHandler.tologin(message['data'],self.callback)
            self.session = message['data']
        else:
            print "send message:%s" %message['data'] 
            self.application.webDataHandler.on_message(message)
            
    def callback(self,data):
        self.write_message(data)
    
class SetCookietHandler(tornado.web.RequestHandler):
    def get(self):
        cookie = self.get_secure_cookie("count")
        count = int(cookie) + 1 if cookie else 1
        countString = "1 time" if count == 1 else "%d times" %count
        self.set_secure_cookie('count',str(count))
        self.render('index2.html',countString=countString)

        
class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html',next=self.get_argument('next','/'))
            
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if ( password == "123456"):
            self.set_secure_cookie('username',username)
            print "User is login? %s" %self.get_current_user()
            self.redirect(self.get_argument('next','/'))
        else:
            print "password is error"
            self.redirect("/login")
            
class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        if (self.get_argument("logout", None)):
            self.clear_cookie("username")
            self.clear_cookie('loginStatus')
            self.redirect("/")
        else:
            self.redirect("/")
            
class Application(tornado.web.Application):
    def __init__(self):
        self.webDataHandler = webDataHandler()
        #print self.webDataHandler.loginuser
        handlers=[
            (r"/",IndexHandler),
            (r"/name/(\w+)",reNameHandler),
            (r"/poem",PoemPageHandler),
            (r"/wechat",chatIndexHandler),
            (r"/wechatServer",wechatServer),
            (r"/cookie",SetCookietHandler),
            (r"/login",LoginHandler),
            (r"/logout",LogoutHandler),
        ]
        settings = {
            "cookie_secret":"bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "template_path":os.path.join(os.path.dirname(__file__),"template1"),
            'static_path':os.path.join(os.path.dirname(__file__), "static"),
            'debug':True,
            'login_url':'/login',
        }
        self.db = MySQLdb.connect(host='127.0.0.1',user='root',passwd='root',db='deltaOPS')
        #template_path=os.path.join(os.path.dirname(__file__),"template")
        #static_path=os.path.join(os.path.dirname(__file__), "static")
        #tornado.web.Application.__init__(self, handlers,template_path=template_path,static_path=static_path,debug=True)
        tornado.web.Application.__init__(self, handlers,**settings)
        
if __name__ == "__main__":
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
    
    
