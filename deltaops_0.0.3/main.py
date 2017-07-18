#!/user/sbin/env python 
# -*- coding:utf-8 -*-  

import tornado.httpserver 
import tornado.ioloop

from daemon import Bridge
from data import ClientData
from utils import check_ip, check_port

import tornado.options
import tornado.websocket
import tornado.web
import os,time
import re
import ansibleapi
import subhandlers
from uuid import uuid4
import json
import MySQLdb
import ast
import hashlib
from handlers import *
from ioloop import IOLoop


from tornado.options import define,options
define("port",default=8080,help="run on the given port",type=int)
#HTML Router
class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_cookie('username',None)
        if user_json:
            return user_json
        else:
            return None
        #return self.get_secure_cookie('username',None)

class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('index.html')
        
class TestHandler(BaseHandler):
    def get(self):
        self.render('test.html')
        
class HostHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('charts.html')
class ActionIndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('action.html')
class ArgumentIndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('argument.html')
class GroupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('group.html')
        
class ProjectHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('project.html')
        
class AddPlayBookHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('addplaybook.html')
        
class ConfHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('conftmp.html')
        
class ServiceManageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('servicemange.html')
        
class DeployCodeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('deploycode.html')

# Operation api     
class HostManageHandler(BaseHandler):
    
    def getHostGoup(self,data):
        cur = self.db.cursor()
        cur.execute("SELECT GroupName FROM HostGroup INNER JOIN Map_Host_Group ON Map_Host_Group.GroupID=HostGroup.id where Map_Host_Group.HostID=%s",int(data[0]))
        gpresult = cur.fetchall()
        data = list(data)
        data.insert(3,','.join(map(lambda x:x[0],list(gpresult))))
        cur.close()
        return data
    
    @tornado.web.authenticated
    def get(self,page=1):
        data = {}
        self.db = self.application.db()
        cur = self.db.cursor()
        cur.execute("select * from Host limit %s,%s",(int(page)*10-10,int(page)*10))
        result = list(cur.fetchall())
        result = map(self.getHostGoup,result)
        for d in result:
            data[d[0]]=d
        cur.close()
        self.db.close()
        self.write(json.dumps(data))
        
    @tornado.web.authenticated    
    def post(self):
        #print self.get_argument('hostname1')
        values = []
        data={'status':'success'}
        try:
            db = self.application.db()
            values.append(self.get_argument('hostname'))
            values.append(self.get_argument('ipaddr'))
            values.append(self.get_argument('htype'))
            values.append(self.get_argument('hposition'))
            cur = db.cursor()
            cur.execute("INSERT INTO Host(HostName,HostIP,HostType,HostPosition) VALUES(%s,%s,%s,%s)",(values))
            cur.execute("SELECT id From Host where HostName=%s and HostIP=%s",(values[0],values[1]))
            id = cur.fetchone()
            cur.execute("INSERT INTO Map_Host_Group(HostID,GroupID) VALUES(%s,'1')",id[0])
            db.commit()
            db.close()
        except:
            data['status']='fail'
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def delete(self):
        hostid=map(lambda x:int(x),json.loads(self.get_argument('hostid')))
        data = {'status':'success'}
        try:
            sql = ("DELETE FROM Map_Host_Group WHERE HostID in (%s)" % ','.join(['%s']*len(hostid))) %tuple(hostid)
            sql1 = ("DELETE FROM Host WHERE id in (%s)" % ','.join(['%s']*len(hostid))) %tuple(hostid)
            delete_host_action_history_sql = ("DELETE from Actionhistory join Action where Action.objecttype='host' and Action.objectid in (%s)" % ','.join(['%s']*len(hostid))) %tuple(hostid)
            delete_host_action_sql = ("DELETE from Action where objecttype='host' and objectid in (%s)" % ','.join(['%s']*len(hostid))) %tuple(hostid)
            db = self.application.db()
            cur = db.cursor()
            cur.execute(sql)
            db.commit()
            cur.execute(sql1)
            db.commit()
            cur.execute(delete_host_action_history_sql)
            db.commit()
            cur.execute(delete_host_action_sql)
            db.commit()
            cur.close()
            db.commit()
            db.close()
        except:
             data['status']='fail'
        self.write(json.dumps(data))

class HostAllHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        data = {}
        try:
            db = self.application.db()
            cur = db.cursor()
            sql = "SELECT id,HostName,HostIP From Host "
            cur.execute(sql)
            result = list(cur.fetchall())           
            for d in result:
                data[d[0]]=list(d)
        except:
            pass
            
        self.write(json.dumps(data))
        
class GroupManageHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,id=0):
        data={}
        db = self.application.db()
        cur = db.cursor()
        if id==0:
            page = int(self.get_argument('page',1))
            print type(page)
            cur.execute("SELECT * FROM HostGroup limit %s,%s",((page-1)*10,page*10))
        else:
            cur.execute("SELECT * FROM HostGroup WHERE id=%s",id)
        result = list(cur.fetchall())
        db.close()
        for d in result:
            data[d[0]] = list(d)    
        self.write(json.dumps(data))
    
    @tornado.web.authenticated   
    def post(self):
        data={'status':'success'}
        db = self.application.db()
        cur = db.cursor()
        try:
            groupname = self.get_argument('groupname')
            cur.execute("INSERT INTO HostGroup(GroupName) VALUES(%s)",groupname)      
            db.commit()
            db.close()
        except:
            data['status']='fail'
            
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def delete(self):
        data={'status':'success'}
        try:
            groupid = map(lambda x:int(x),json.loads(self.get_argument('id')))
            db = self.application.db()
            cur = db.cursor()
            sql = "DELETE FROM Map_Host_Group WHERE GroupID in (%s)" % ','.join(['%s']*len(groupid))
            sql1 = "DELETE FROM HostGroup WHERE id in (%s)" % ','.join(['%s']*len(groupid))
            cur.execute(sql % tuple(groupid))
            cur.execute(sql1 % tuple(groupid))
            db.commit()
            db.close()
        except:
            data['status']='fail'
        
        self.write(json.dumps(data))
    
    
class GroupUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data={'status':'success'}
        try:
            groupname=str(self.get_argument('groupname'))
            id=int(self.get_argument('id'))
            db = self.application.db()
            cur = db.cursor()
            cur.execute("UPDATE HostGroup SET GroupName=%s WHERE id=%s",(groupname,id))
            cur.close()
            db.commit()
            db.close()
        except:
            data['status']='fail'
            
        self.write(json.dumps(data))

class GroupAllHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data={}
        try:
            db = self.application.db()
            cur = db.cursor()
            cur.execute("SELECT * FROM HostGroup") 
            result = list(cur.fetchall())
            db.close()
            data['data']={}
            for d in result:
                data['data'][d[0]]=list(d)
            data['status']='success'
            print data
        except:
            data['status']='fail'
        self.write(json.dumps(data))
        
class GroupQueryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data={}
        try:
            query = '%'+self.get_argument('query','server')+'%'
            print query
            db = self.application.db()
            cur = db.cursor()
            cur.execute("SELECT * FROM HostGroup where GroupName  like '%s' " % query )
            result = list(cur.fetchall())
            print result
            for d in result:
                data[d[0]] = list(d)
            db.close()
        except:
            pass
        self.write(json.dumps(data))

class GroupMemberHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,gid=0):
        data={}
        if gid != 0:
            try:
                
                db = self.application.db()
                cur = db.cursor()
                cur.execute("select HostName,HostIP FROM Host JOIN Map_Host_Group on Host.id=Map_Host_Group.HostID where Map_Host_Group.GroupID=%s" % int(gid))
                result = list(cur.fetchall())
                for d in result:
                    data[d[0]]=list(d)                    
            except:
                pass
        else:
            pass
        self.write(json.dumps(data))
class HostQueryHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data={}
        try:
            query = '%'+self.get_argument('query','server')+'%'
            db = self.application.db()
            cur = db.cursor()
            sql = "SELECT id,HostName,HostIP FROM Host WHERE HostName like '%s' or HostIP like '%s'" % (query,query)
            cur.execute(sql)
            result = list(cur.fetchall())
            for d in result:
                data[d[0]] = list(d)
            db.close()
        except:
            pass
        self.write(json.dumps(data))

class HostUpdateHandler(BaseHandler):
    @tornado.web.authenticated
    def post(self):
        data={'status':'success'}
        try:
            values=[]
            values.append(str(self.get_argument('hostname')))
            values.append(str(self.get_argument('ipaddr')))
            values.append(str(self.get_argument('htype')))
            values.append(str(self.get_argument('hposition')))
            values.append(int(self.get_argument('id')))
            db = self.application.db()
            sql="UPDATE Host SET HostName='%s',HostIP='%s',HostType='%s',HostPosition='%s' where id=%s" % tuple(values)
            cur = db.cursor()
            cur.execute(sql)
            cur.close()
            db.commit()
            db.close()
        except:
            data['status']='fail'
            
        self.write(json.dumps(data))

class HostGroupHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,hostid):
        data=[];
        try:
            hostid=int(hostid)
            db = self.application.db();
            cur = db.cursor();
            cur.execute("select HostGroup.GroupName from Map_Host_Group join HostGroup ON GroupID=HostGroup.id where HostID=%s",hostid)
            data=map(lambda x:x[0],list(cur.fetchall()))
        except:
            pass
        self.write(json.dumps(data))
    
    @tornado.web.authenticated   
    def post(self,hostid=0):
        #'{'id':'[]'}'
        data={'status':'success'}
        if(hostid != 0):
            try:
                addlist = json.loads(self.get_argument('list'))
                print "%s,%s" %(hostid,addlist)
                db = self.application.db()
                cur = db.cursor()
                try:
                    for d  in addlist:
                       d = str(d)
                       print d
                       cur.execute("SELECT id FROM HostGroup where GroupName='%s'" %d)
                       gid = int(cur.fetchone()[0])
                       print gid
                       inserM_H_G = "INSERT INTO Map_Host_Group(HostID,GroupID) VALUES(%s,%s)" %(hostid,gid)
                       print inserM_H_G
                       cur.execute(inserM_H_G)
                       
                except:
                    db.rollback()
                    data['status']='fail'
                db.commit()
                db.close()
            except:
                data['status']='fail'
        else:
            data['status']='fail'
        self.write(json.dumps(data))
    @tornado.web.authenticated    
    def delete(self,hostid):
        data={'status':'success'}
        if(hostid !=0):
            try:
                rmlist = json.loads(self.get_argument('list'))
                db = self.application.db()
                cur = db.cursor()
                try:
                    
                    for d  in rmlist:
                       d = str(d)
                       cur.execute("SELECT id FROM HostGroup where GroupName='%s'" %d)
                       gid = int(cur.fetchone()[0])
                       cur.execute("DELETE FROM  Map_Host_Group WHERE HostID=%s AND GroupID=%s",(hostid,gid));
                except:
                    db.rollback()
                    data['status']='fail'
                db.commit()
                db.close()
            except:
                data['status']='fail'
        else:
            data['status']='fail'
        self.write(json.dumps(data))

class ConfManagerHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        data={}
        try:
            page = self.get_argument('page')
            db = self.application.db()
            cur = db.cursor()    
            try:
                cur.execute("select * from Template limit %s,%s",(int(page)*10-10,int(page)*10))
                result = list(cur.fetchall())
                for d in result:
                    data[d[0]]=list(d)
            except:
                pass
            db.close()
        except:
            pass
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def post(self):
        data={'status':'success'}
        try:
            name = self.get_argument('name')
            kvlist =json.loads(self.get_argument('value'))
            print "%s,%s" %(name,kvlist)
            db = self.application.db()
            cur = db.cursor()
            try:
                sql ="INSERT INTO Template(Template) VALUES('%s')"
                sql1 = "SELECT id FROM Template WHERE Template='%s'"
                sql2 = "INSERT INTO TemplateKey(tid,keyname,value) VALUES(%s,'%s','%s')"
                cur.execute(sql % name)
                cur.execute(sql1 % name)
                gid  = int(cur.fetchone()[0])
                for kv in kvlist:
                    cur.execute(sql2 %(gid,str(kv[0]),str(kv[1])))
            except:
                db.rollback()
                data['status']='fail'
            db.commit()
            db.close()
        except:
            data['status']='fail'
        self.write(json.dumps(data))
        
    @tornado.web.authenticated
    def delete(self):
        data={'status':'success'}
        try:
            tmplist = map( lambda x: int(x),json.loads(self.get_argument('tmplist')))
            print tmplist
            try:
                db = self.application.db();
                cur = db.cursor()
                try:
                    sql = "DELETE FROM TemplateKey WHERE tid=%s"
                    sql1 = "DELETE FROM Template WHERE id=%s"
                    for tid in tmplist:
                        cur.execute(sql %tid )
                        cur.execute(sql1 %tid)
                    db.commit()
                except:
                    db.rollback()
                    data['status']='fail'
                db.close()
            except:
                data['status']='fail'
        except:
            pass
        self.write(json.dumps(data))
        
class ConfKeyHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self,tid=0):
        data ={}
        try:
            if tid != 0 :
                db = self.application.db()
                cur = db.cursor()
                try:
                    sql = "SELECT keyname,value FROM TemplateKey WHERE tid=%s"
                    cur.execute(sql % tid)
                    result = map(lambda x:list(x),list(cur.fetchall()))
                    data[tid]=result
                except:
                    pass
                db.close()
            else:
                pass
        except:
            pass
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def post(self):
        data={'status':'success'}
        try:
            tid = int(self.get_argument('tid'))
            name = self.get_argument('name')
            kvlist =json.loads(self.get_argument('value'))
            print "%s,%s,%s" %(tid,name,kvlist)
            db = self.application.db()
            cur = db.cursor()
            try:
                sql  = "DELETE FROM TemplateKey WHERE tid=%s"
                sql1 = "INSERT INTO TemplateKey(tid,keyname,value) VALUES(%s,'%s','%s')"
                cur.execute(sql % tid)
                for kv in kvlist:
                    print kv
                    cur.execute(sql1 %(tid,str(kv[0]),str(kv[1])))
                db.commit()
            except:
                db.rollback()
                data['status']='fail'
            
            db.close()
        except:
            data['status']='fail'
        self.write(json.dumps(data))

class ConfAllHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data = {}
        try:
            db = self.application.db()
            cur = db.cursor()
            sql = "SELECT * from Template"
            cur.execute(sql)
            result = list(cur.fetchall())
            for d in result:
                data[d[0]]=list(d)
        except:
            pass
            
        self.write(json.dumps(data))

class ProjectManagerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data={}
        try:
            page = self.get_argument('page')
            db = self.application.db()
            cur = db.cursor()
            try:
                sql = "select Project.id,ProName,ProPath,ProType,Host.HostName,Template.Template,Status  from Project JOIN Host ON Project.HostID=Host.id  JOIN  Template ON Project.TemplateID=Template.id  limit %s,%s" %(int(page)*10-10,int(page)*10)
                cur.execute(sql)
                result = list(cur.fetchall())
                for d in result:
                    data[d[0]]=list(d)
            except:
                pass
            db.close()
        except:
            pass
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def post(self):
        data={'status':'success'}
        value=[]
        try:
            value.append(str(self.get_argument('projectname')))
            
            value.append(str(self.get_argument('projectpath')))
            value.append(str(self.get_argument('contype')))
            value.append(str(self.get_argument('conhost')))
            value.append(str(self.get_argument('conconfig')))
            value.append('uninit')
            db = self.application.db()
            cur = db.cursor()
            try:
                sql = "INSERT INTO Project(ProName,ProPath,ProType,HostID,TemplateID,Status) VALUES('%s','%s','%s',%s,%s,'%s')" % tuple(value)
                cur.execute(sql)
                db.commit()
                print "debug"
            except:
                db.rollback()
                data['status']='fail'
            db.close()
        except:
            data['status']='fail'
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def delete(self):
        data={'status':'success'}
        try:
            rmlist = map(lambda x:int(x),json.loads(self.get_argument('rmlist')))
            db = self.application.db()
            cur = db.cursor()
            try:
                sql = "DELETE FROM Project where id in(%s)" % ','.join(['%s']*len(rmlist))
                cur.execute(sql % tuple(rmlist))
                db.commit()
            except:
                db.rollback()
                data['status']='fail'
            db.close()
        except:
            data['status']='fail'
            
        self.write(json.dumps(data))

class ProServiceHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,pid=0):
        data={}
        if pid != 0:
            try:
                db = self.application.db()
                cur = db.cursor()
                #sql = "select Sid,Service.name,status,servicePID from Map_Pro_Service JOIN Service ON Sid=Service.id where Pid=%s"
                sql = "select id,name,'uninit','0' from Service where type=(select ProType FROM Project where id=%s) and id not in (select Sid from  Map_Pro_Service where Pid=%s)"
                sql1 = "select Service.id,Service.name,status,servicePID FROM Map_Pro_Service JOIN Service on Map_Pro_Service.Sid=Service.id where Pid=%s"
                cur.execute(sql % (int(pid),int(pid)))
                result = list(cur.fetchall())
                cur.execute(sql1 % int(pid))
                result1 = list(cur.fetchall())
                result.extend(result1)
                for d in result:
                    data[d[0]]=list(d)
            except:
                pass
        else:
            pass
            
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def post(self):
        data={'status':'success'}
        playbooks={
            'start':'/data/ansible-playbook/demoyml/demo1.yml',
            'stop':'/data/ansible-playbook/demoyml/demo1.yml',
            'restart':'/data/ansible-playbook/demoyml/demo1.yml',
            'deploy':'/data/ansible-playbook/demoyml/demo1.yml',
            'unline':'/data/ansible-playbook/demoyml/demo1.yml',
        }
        pid = self.get_argument('pid')
        serviceid = self.get_argument('sid')
        action = self.get_argument('action')
        playbook = playbooks[action]
        try:
            params = {}
            sql="select ProName,ProPath,ServiceRoot from Project where id=%s"
            sql1="select name,DirName from Service where id=%s"
            db = self.application.db()
            cur = db.cursor()
            cur.execute(sql % int(pid))
            result = cur.fetchone()
            cur.execute(sql1 % int(sid))
            result1 = cur.fetchone()
            params['ProjectName']=result[0]
            params['ProjectPath']=result[1]
            params['ServiceRoot']=result[2]
            params['service']=result1[0]
            params['ServiceDir']=result[1]
            print params
            pass
            #pl = ansibleapi.AnsiblePlayBook(playbook,params)
        except:
            pass
        self.write(json.dumps(data))
    
class InitProjectHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self):
        pl = ansibleapi.AnsiblePlayBook('/data/ansible-playbook/demoyml/demo1.yml',{'host':'172.17.92.168'})
        pl.execute()
        print type(pl.get_result())
        self.write(json.dumps(pl.get_result()))
        
    @tornado.web.authenticated   
    def post(self):
        data={'status':'success'}
        params = {}
        #playbook = '/data/ansible-playbook/demoyml/demo1.yml'
        playbook = '/data/web/playbook/initProject.yml'
        try:
            projectid = self.get_argument('pid')
            db = self.application.db()
            cur = db.cursor()
            try:
                sql = "select Host.HostIP,ServiceRoot,Status FROM Project JOIN Host ON Project.HostID=Host.id where Project.id=%s"
                sql1 = "select keyname,value from Project join TemplateKey on Project.TemplateID=TemplateKey.tid where Project.id=%s"
                cur.execute(sql % projectid)
                result = cur.fetchone()
                if result[2] == 'uninit':
                    params['hosts']=result[0]
                    params['ServiceRoot']=result[1]
                    cur.execute(sql1 % projectid)
                    result = cur.fetchall()
                    for d in result:
                        params[d[0]]=d[1]
                    
                    try:
                        pl = ansibleapi.AnsiblePlayBook(playbook,params)
                        print params
                        pl.execute()
                        result = pl.get_result()
                        data['result']=result
                        print result
                        if result[params['hosts']]['failures'] == 0 and result[params['hosts']]['unreachable'] == 0:
                            #print "success"
                            data['info']=result
                            sql2 = "UPDATE Project SET Status='init' where id=%s"
                            cur.execute(sql2 % int(projectid))
                            db.commit()
                        else:
                            data['status']='fail'
                    except:
                        db.rollback()
                        data['status']='fail'
                else:
                    print "Project had init"
                    data['status']='fail'
            except:
                data['status']='fail'
            db.close()
        except:
            print "fail"
            pass
        self.write(json.dumps(data))
        
class ServiceManage(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        print "debug"
        data = {'status':'success'}
        pid = 7
        sid = 1
        action = 'start'
        
        db = self.application.db()
        servicepl = subhandlers.serviceHandlerFactor(action,pid,sid,db).createPlaybook()
        print servicepl.get_playbook()
        servicepl.execute()
        data = servicepl.get_result()
        print data
        db.close()
        self.write(json.dumps(data))
    @tornado.web.authenticated   
    def post(self):
        print "debug1"
        pid = self.get_argument('pid')
        sid = self.get_argument('sid')
        action = self.get_argument('action')
        print pid,sid,action
        
        db = self.application.db()
        servicepl = subhandlers.serviceHandlerFactor(action,pid,sid,db).createPlaybook()
        print servicepl.get_playbook()
        servicepl.execute()
        data = servicepl.get_result()
        print data
        db.close()
        self.write(json.dumps(data))


#******************Manager THe playbook and Action line************************#
class PlayBookManagerHandler(BaseHandler):

    @tornado.web.authenticated
    def getmap(self):
        self.table = {
            'actionname':'actionName',
            'playbook':'playbook',
            'comment':'note',
            'author':'author',
            'type':'actiontype',
        }
        '''
        CREATE TABLE Playbook(
        id int NOT NULL AUTO_INCREMENT,
        actionName varchar(255) NOT NULL,
        playbook varchar(2000) NOT NULL,
        filepath varchar(255),
        note varchar(500),
        uploadtime datetime,
        updatetime datetime,
        author varchar(30),
        md5 varchar(30),
        actiontype varchar(30) default 'UNGROUP',
        PRIMARY KEY(id)
        );
        '''
    
    @tornado.web.authenticated
    def get(self,type='id',id=None):
        self.getmap()
        data = {}
        if type == 'id':
            #sql = "select id,actionName,note,author,updatetime from Playbook where id=%s" %id
            sql = "select id,actionName,actiontype,author,note,updatetime,playbook from Playbook where id=%s" %id
        elif type == 'page':
            sql = "select id,actionName,actiontype,author,note,updatetime,playbook from Playbook limit %s,%s" %(int(id)*10-10,int(id)*10)
        elif type == 'all':
            sql = "select id,actionName,actiontype,author,note,updatetime,playbook from Playbook"
        else:
            raise tornado.web.HTTPError(400)
        
        try:
            db = self.application.db()
            cur = db.cursor()
            cur.execute(sql)
            result = cur.fetchall()
            db.commit()
            db.close()
            data['status']='success'
            data['data']={}
            for r in result:
                r=map(lambda x: str(x).replace('\"','"'),list(r))
                print r
                data['data'][str(r[0])]=r
            #print data
        except:
            data['status'] = 'fail'
        
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def post(self,type='id',id=None):
        self.getmap()
        data = {}
        try:
            values = []
            keys = []
            
            for key in self.request.body_arguments.keys():
                if key in self.table.keys():
                    keys.append(self.table[key])
                    values.append(self.get_argument(key).replace('"','\\"'))
            
            keys.append('uploadtime')
            keys.append('updatetime')
            values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
            values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
            
            #Storate the playbook to server 
            filename=self.get_argument('actionname').replace(' ','_')+str(int(time.time()))+'.yml'
            path = os.path.join(self.application.playbookpath,filename)
            #python execute mysql sql and storage the playbook yml file
            try:
                with open(path,'w') as f:
                    f.write(self.get_argument('playbook'))
                keys.append('filepath')
                values.append(path)
                try:
                    sql = ("INSERT INTO Playbook(%s)" %('%s,'*len(keys))[:-1])%tuple(keys) + ("VALUES(%s)" %('"%s",'*len(keys))[:-1])%tuple(values)
                    db = self.application.db()
                    cur = db.cursor()
                    cur.execute(sql)
                    db.commit()
                    db.close()
                except:
                    data['status']='fail'
            except:
                data['status']='fail'
                
            data['status']='success'
        except:
            data['status']='fail'
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def delete(self,type='id',id=None):
        data={}
        if type == 'id' and id is not None:
            sql = "DELETE FROM Playbook where id=%s" %id
            #deleteActionhis = "DELETE FROM Actionhistory where id in (select id from Action where Playid=%s)" %id
            #deleteaction = "DELETE FROM Action where Playid=%s" %id
            try:
                db = self.application.db()
                cur = db.cursor()
                print sql
                cur.execute(sql)
                db.commit()
                db.close()
            except:
                data['status']='fail'
                data['data'] = "Cannot delete or update a parent row: a foreign key constraint fails."
        else:
            data['status'] = 'fail'
        
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def put(self,type='id',id=None):
        self.getmap()
        data = {}
        print "DEBUG PUT%s" %id 
        if id is not None and isinstance(int(id),int):
            try:
            
                values = []
                keys = []
                for key in self.request.body_arguments.keys():
                    if key in self.table.keys():
                        keys.append(self.table[key])
                        values.append(self.get_argument(key).replace('"','\\"'))
                keys.append('updatetime')
                values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
                #Storate the playbook to server 
                filename=self.get_argument('actionname').replace(' ','_')+str(int(time.time()))+'.yml'
                path = os.path.join(self.application.playbookpath,filename)
                #python execute mysql sql and storage the playbook yml file
                try:
                    with open(path,'w') as f:
                        f.write(self.get_argument('playbook'))
                    keys.append('filepath')
                    values.append(path)
                    try:
                        sql = ("UPDATE Playbook SET %s" %(','.join(map(lambda x:x+'="%s"',keys))) + "where id=%s" %id) %tuple(values)
                        print sql
                        db = self.application.db()
                        cur = db.cursor()
                        cur.execute(sql)
                        db.commit()
                        db.close()
                    except:
                        data['status']='fail'
                        data['code']='mysql execute fail'
                except:
                    data['status']='fail'
                    data['code']='can not storage data'
                data['status']='success'
            except:
                data['status']='fail'
                data['code'] = 'Get request argument fial'
        else:
            data['status']='fail'
            data['code'] = 'id is not int'
        self.write(json.dumps(data))

def get_key_from_content(content):
    keyset = set()
    excludekey=['hosts','items']
    if isinstance(content,list):
        contentlist = content
    else:
        contentlist = str(content).split('\n')
    keylist = [re.split('{{|}}',line)[1::2] for line in contentlist if '{{' in line ]
    for key in keylist:
        keyset = keyset.union(set(key))
    result = list(keyset.difference(set(excludekey)))
    return result
    
class PlayBookKeyHandler(BaseHandler):
    
    @tornado.web.authenticated
    def get(self,id=None):
        data={}
        if id is not None and isinstance(int(id),int):
            sql = "SELECT playbook from Playbook where id=%s" %id
            try:
                db = self.application.db()
                cur = db.cursor()
                cur.execute(sql)
                result = cur.fetchone()
                print result[0]
                keylist = get_key_from_content(result[0])
                db.commit()
                db.close()
                data['status'] = 'success'
                data['data'] = ','.join(keylist)
            except:
                data['status'] = 'fail'
                data['code'] = 'mysql query fail'
        else:
            data['status'] = 'fail'
            data['code'] = 'id is not int'
        self.write(json.dumps(data))
        
#******************Manager the argument template ******************************#
    
class ArgumentHandler(BaseHandler):
    def getmap(self):
        '''
        CREATE TABLE Argument(
        id int NOT NULL AUTO_INCREMENT,
        name varchar(255) NOT NULL,
        note varchar(500),
        dependence varchar(20),
        keyvalue varchar(1000),
        author varchar(30),
        updatetime datetime,
        PRIMARY KEY(id),
        UNIQUE(name)
        );
        '''
        self.table= {
            'name':'name',
            'note':'note',
            'dependence':'dependence',
            'value':'keyvalue',
            'author':'author',
        }
    
    @tornado.web.authenticated
    def get(self,type="id",id=None):
        data = {}
        
        if type == 'id' and id is not None and isinstance(int(id),int):
            sql = "SELECT id,name,note,author,keyvalue,dependence,updatetime FROM Argument where id=%s" %id
        elif type == 'page' and id is not None and isinstance(int(id),int):
            sql = "select id,name,note,author,keyvalue,dependence,updatetime FROM Argument limit %s,%s" %(int(id)*10-10,int(id)*10)
        elif type == "all":
            sql = "select id,name,note,author,keyvalue,dependence,updatetime FROM Argument "
        try:
            db = self.application.db()
            cur = db.cursor()
            #print sql
            cur.execute(sql)
            result = cur.fetchall()
            print result
            #print result
            data['data']={}
            for r in result:
                r=list(r)
                #r=map(lambda x: str(x).replace('\"','"'),list(r))
                r[6] = str(r[6])
                data['data'][r[0]]=r
            db.commit()
            db.close()
            data['status']='success'
            
        except:
            data['status']='fail'
        print data
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def post(self,type='id',id=None):
        self.getmap()
        keys=[]
        values=[]
        data ={}
        for key in self.request.body_arguments.keys():
            if key in self.table.keys():
                keys.append(self.table[key])
                values.append(self.get_argument(key).replace('"',''))
        keys.append('updatetime')
        values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        sql = ('INSERT INTO Argument (%s)' %('%s,'*len(keys))[:-1])%tuple(keys) + ("VALUES(%s)" %('"%s",'*len(keys))[:-1])%tuple(values)
        print "debug",values,keys,sql
        try:
            db = self.application.db()
            print "debug1"
            cur = db.cursor()
            cur.execute(sql)
            print "debug2"
            db.commit()
            db.close()
            data['status']='success'
            print "debug3"
        except:
            data['status']='fail'
        
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def delete(self,type='id',id=None):
        data ={}
        if id is not None and isinstance(int(id),int):
            sql = "DELETE FROM Argument where id=%s" %id
            try:
                db = self.application.db()
                cur = db.cursor()
                #print sql
                cur.execute(sql)
                db.commit()
                db.close()
                data['status'] = 'success'
            except:
                data['status'] = 'fail'
        else:
            ata['status'] = 'fail'
        self.write(json.dumps(data))
    
    @tornado.web.authenticated
    def put(self,type='id',id=None):
        self.getmap()
        keys=[]
        values=[]
        data ={}
        if id is not None and isinstance(int(id),int):
            for key in self.request.body_arguments.keys():
                if key in self.table.keys():
                    keys.append(self.table[key])
                    values.append(self.get_argument(key).replace('"','\\"'))
            values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
            keys.append('updatetime')
            sql = "UPDATE Argument SET %s,%s,%s,%s,%s,%s" %tuple(map(lambda x:x+'=\'%s\'',keys))+" where id=%s" %id
            sql = sql %tuple(values)
            try:
                #print sql
                db = self.application.db()
                cur = db.cursor()
                cur.execute(sql)
                db.commit()
                db.close()
                data['status'] = 'success'
            except:
                data['status'] = 'fail'
        else:
            ata['status'] = 'fail'
        self.write(json.dumps(data)) 
    
#******************Host create the action *************************************#
class ActionHandler(BaseHandler):
    def getmap(self):
        '''
        CREATE TABLE Action(
        id int NOT NULL AUTO_INCREMENT,
        executename varchar(50),
        objecttype varchar(15),
        objectid varchar(15),
        Playid int NOT NULL,
        Arguid int NOT NULL,
        FOREIGN KEY(Playid) REFERENCES Playbook(id),
        FOREIGN KEY(Arguid) REFERENCES Argument(id),
        author varchar(50),
        updatetime datetime,
        PRIMARY KEY(id)
        );
        '''
        self.table={
            'name':'executename',
            'ojtype':'objecttype',
            'ojid':'objectid',
            'playid':'Playid',
            'argumid':'Arguid',
            'author':'author',
        }
        pass
        
    @tornado.web.authenticated    
    def get(self,type='id',id=None):
        data={}
        objectTable ={
            'host':{'table':'Host','field':'HostName'},
            'hostgroup':{'table':'HostGroup','field':'GroupName'},
        }
        keys = "id,name,objecttype,objectid,playbook,arguname,author,updatetime"
        sql = "select Action.id,executename as name,objecttype,objectid,actionName as playbook,Argument.name as argname,Action.author,Action.updatetime from Action join Playbook on Action.Playid = Playbook.id join Argument on Action.Arguid = Argument.id"
        if type == "id" and id is not None and isinstance(int(id),int):
            sql = sql + ' where Action.id=%s' %id
        else:
            sql = sql + ' limit %s,%s' %(int(id)*10-10,int(id)*10)
        try:
            #print sql
            db = self.application.db()
            cur = db.cursor()
            data['data'] = {}
            cur.execute(sql)
            result = cur.fetchall()
            tmpdata={}
            for r in result:
                r = map(lambda x:str(x),list(r))
                keylist = keys.split(',')
                tmpdata[r[0]] = dict(zip(keylist,r))
            for raw in tmpdata:
                sql = "select %s from %s where id=%s" %(objectTable[tmpdata[raw]['objecttype']]['field'],objectTable[tmpdata[raw]['objecttype']]['table'],tmpdata[raw]['objectid'])
                cur.execute(sql)
                result = cur.fetchone()
                tmpdata[raw]['objectname']=result[0]
            data['data'] = tmpdata
            db.commit()
            db.close()
            data['status']='success'
        except:
            data['status']='fail'
        self.write(json.dumps(data))
        
    @tornado.web.authenticated
    def post(self,type='id',id=None):
        print "DEBUG ACTION POST"
        self.getmap()
        keys=[]
        values=[]
        data ={}
        for key in self.request.body_arguments.keys():
            if key in self.table.keys():
                keys.append(self.table[key])
                values.append(self.get_argument(key))
        keys.append('updatetime')
        values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
        sql = ('INSERT INTO Action(%s)'%('%s,'*keys.__len__())[:-1]) %tuple(keys) + ("VALUES(%s)" %(('"%s",'*len(keys))[:-1]))%tuple(values)
        try:
            db = self.application.db()
            cur = db.cursor()
            cur.execute(sql)
            db.commit()
            db.close()
            data['status']='success'
        except:
            data['status']='fail'
        self.write(json.dumps(data))
    @tornado.web.authenticated    
    def put(self,type='id',id=None):
        self.getmap()
        keys=[]
        values=[]
        data={}
        if id is not None and isinstance(int(id),int):
            for key in self.request.body_arguments.keys():
                if key in self.table.keys():
                    keys.append(self.table[key])
                    values.append(self.get_argument(key))
            keys.append('updatetime')
            values.append(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()))
            sql = ('UPDATE Action SET %s'%(','.join(map(lambda x:'%s='%x+'"%s"',keys))))%tuple(values)+" where id=%s" %id
            try:
                db = self.application.db()
                cur = db.cursor()
                #print sql
                cur.execute(sql)
                db.commit()
                db.close()
                data['status']='success'
            except:
                data['status']='fail'
        else:
            data['status']='fail'
        self.write(json.dumps(data))
    @tornado.web.authenticated    
    def delete(self,type='id',id=None):
        if id is not None and isinstance(int(id),int):
            sql1 = "DELETE FROM Actionhistory where actionid=%s" %id
            sql2 = "DELETE FROM Action where id=%s" %id
        data = {}
        try:
            db = self.application.db()
            cur = db.cursor()
            cur.execute(sql1)
            cur.execute(sql2)
            db.commit()
            db.close()
            data['status']='success'
        except:
            data['status']='fail'
        self.write(json.dumps(data))

class ActionOwnerHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,type="host",id=None):
        data = {}
        objectTable ={
            'host':{'table':'Host','field':'HostName'},
            'hostgroup':{'table':'HostGroup','field':'GroupName'},
        }
        keys = "id,name,author"
        #print type
        if objectTable.has_key(type):
            sqllist =[]
            sql = 'select id,executename,author from Action where objecttype="%s" and objectid=%s' %(type,id)
            sqllist.append(sql)
            if type =="host":
                hostgroup = "select id,executename,author from Action where objecttype='hostgroup' and objectid in (select GroupID from Map_Host_Group where HostID=%s)" %id
                sqllist.append(hostgroup)
            try:
                db = self.application.db()
                #print sql
                cur = db.cursor()
                data['data'] = {}
                for sql in sqllist:
                    cur.execute(sql)
                    result = cur.fetchall()
                    tmpdata = {}
                    for r in result:
                        r = map(lambda x:str(x),list(r))
                        keylist = keys.split(',')
                        tmpdata[r[0]] = dict(zip(keylist,r))
                    data['data'].update(tmpdata)
                data['status'] = 'success'
            except:
                data['status'] = 'fail'
        else:
            data['status'] = 'fail'
        self.write(json.dumps(data))
        
#***************** Run the action with server use AnsibleAPI ******************#

class ActionRunHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,type='host',id=None):
        #playbook = '/data/web/testplaybook/TestCopyFile.yml'
        #params = {'hosts':['106.75.197.241','172.17.92.23'],'ProjectPath':'/data/m4/app'}
        #pl = ansibleapi.AnsiblePlayBook(playbook,params)
        #pl = ansibleapi.AnsiblePlayBook('/data/web/testplaybook/TestCopyFile.yml',{'host':'106.75.197.241','ProjectPath':'/data/m4/app'})
        #pl.execute()
        #print type(pl)
        # pl.execute()
        # print type(pl.get_result())
        self.write('1')
    @tornado.web.authenticated
    def post(self,id=None):
        data={}
        if "action" in self.request.body_arguments.keys() and id is not None:
            action = self.get_argument('action')
            print action
            if action == "run":
                #***** Get the host ip and playbook and argument 
                objectTable = {
                    'Host':{
                        'table':'Host',
                        'GetIP':'select HostIP from Host where id=%s'
                    },
                    'Hostgroup':{
                        'table':'HostGroup',
                        'GetIP':'select HostIP from Host where id in ( select HostID from Map_Host_Group where Groupid=%s)'
                    },
                }
                try:
                    db = self.application.db()
                    cur = db.cursor()
                    # Get action raw 
                    getaction = "select id,executename,objecttype,objectid,Playid,Arguid from Action where id=%s" %id
                    cur.execute(getaction)
                    action = cur.fetchone()
                    playbookid = action[4]
                    argumid = action[5]
                    objecttype = self.get_argument("objecttype")
                    objectid = self.get_argument("objectid")
                    #objecttype = action[2]
                    #objectid = action[3]
                    
                    # Get Host IP list
                    cur.execute(objectTable[objecttype]['GetIP'] %objectid)
                    hostresult = cur.fetchall()
                    hostlist = [ h[0] for h in hostresult ]
                    #print hostlist 
                    
                    # Get playbook filepath
                    getplaybook = "select filepath from Playbook where id=%s" %playbookid
                    cur.execute(getplaybook)
                    playbook = cur.fetchone()[0]
                    #print playbook
                    
                    # Get argumen object
                    getargument = "select keyvalue from Argument where id=%s" %argumid
                    cur.execute(getargument)
                    args = ast.literal_eval(cur.fetchone()[0])
                    data['status']='success'
                    
                    try:
                        
                        logfile = 'ansible_action_'+id+'_'+str(int(time.time()))+'.log'
                        logfile = os.path.join(self.application.actionlogpath,logfile)
                        args['hosts']=hostlist
                        print args,logfile,playbook
                     
                        pl = ansibleapi.AnsiblePlayBook(playbook,args,logfile)
                        pl.execute()
                        result = pl.get_result()
                        data['status'] = "sueccess"
                        data['result']=str(result)
                        #print result
                        try:
                            runtime = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                            inserlog = "INSERT INTO Actionhistory(actionid,runlog,runtime)VALUES('%s','%s','%s')" %(id,logfile,runtime)
                            cur.execute(inserlog)
                        except:
                            data['result'] = "Can't update the action log info."
                            print "Can't update the action log info."
                    except:
                        data['status'] = 'fail'
                        data['result'] = "Can't run the playbook. Pls to check the playbook format is yml."
                    finally:
                        db.commit()
                        db.close()
                    
                except:
                    data['status'] = 'fail'
                    data['result'] = "Can't get the action info from the database."
            else:
                data['status'] = "fail"
                data['result'] = "The action is nodefine"
        else:
            data['status'] = "fail"
            data['result'] = "The action is nodefine"
            
        self.write(json.dumps(data))
        
class ActionRunHistory(BaseHandler):
    @tornado.web.authenticated
    def get(self,id=None):
        data = {}
        if id is not None and isinstance(int(id),int):
            try:
                sql = "select * from Actionhistory where actionid=%s ORDER BY runtime DESC limit 1" %id
                db = self.application.db()
                cur = db.cursor()
                cur.execute(sql)
                result = cur.fetchone()
                logfile = str(result[-1])
                if os.path.exists(logfile):
                    log = open(logfile,'r')
                    lins = log.readlines()
                    log.close()
                    data['status'] = 'success'
                    data['data'] = lins
                else:
                    data['status'] = 'fail'
                    data['data'] = 'Action history log file is not exist %s.' %logfile
                #lines = log.readlines()
                #og.close() 
            except:
                data['status'] = 'fail'
                data['data']  = "Can' get the action history log."
        else:
            data['status'] = 'fail'
            data['data'] = {}
        self.write(json.dumps(data))
        
#*******************  Handler  End *************************#

#*******************  Authenticate *************************#
class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html",next=self.get_argument("next","/"))
    
    def authenticate(self,username,password):
        if username and password:
            try:
                mkhash = hashlib.md5()
                mkhash.update(password)
                pdhs = mkhash.hexdigest()
                
                #Get passwd form database
                auth = False
                try:
                    AUTH_STATUS={
                        'OK':'OK',
                        'LOCK':'LOCK',
                    }
                    LIMITTIME=10
                    INTEVAL=600
                    
                    keys = ('id','username','password','failtime','status','logintime')
                    sql = "select id,username,password,failtime,status,logintime from deltauser where username='%s'" %username
                    
                    db = self.application.db()
                    cur = db.cursor()
                    #print sql
                    cur.execute(sql)
                    result = cur.fetchone()
                    result = dict(zip(keys,result))
                    now = int(time.time())
                   
                    #sql
                    uptimesql = "UPDATE deltauser SET logintime='%s' where id=%s" %(now,result['id'])
                    resetFailsql = "UPDATE deltauser SET failtime=0 where id=%s" %result['id']
                    addFailsql = "UPDATE deltauser SET failtime=%s where id=%s" 
                    lockusersql = "UPDATE deltauser SET status='LOCK' where id =%s" %result['id']
                    
                    print result['password']
                    print pdhs
                    #User login ok
                    if result['status'] == AUTH_STATUS['OK'] and pdhs == result['password']:
                        cur.execute(uptimesql)
                        cur.execute(resetFailsql)
                        auth = True
                        
                    #Password error time is over and maybe try is too frequently. 
                    elif result['status']  == AUTH_STATUS['LOCK'] and (now - int(result['logintime'])) < INTEVAL:
                        auth = False
                    
                    #Normal password error
                    elif result['status'] == AUTH_STATUS['OK'] and pdhs != result['password'] and result['failtime'] < LIMITTIME:
                        
                        sql = addFailsql %(int(result['failtime'])+1,result['id'])
                        cur.execute(sql)
                        cur.execute(uptimesql)
                        auth=False
                        
                    #Normal password error time is over and status is UNLOCK need to update status.
                    elif result['status'] == AUTH_STATUS['OK'] and pdhs != result['password'] and result['failtime'] >= LIMITTIME:
                        sql = addFailsql %(int(result['failtime'])+1,result['id'])
                        cur.execute(lockusersql)
                        cur.execute(uptimesql)
                        auth=False
                    
                    #Any other unkonw kind.
                    else:
                        auth=False
                        
                except:
                    auth = False
                finally:
                    db.commit()
                    db.close()
                    return auth
            except:
                return False
        else:
            return False
    
    def set_current_user(self,user):
        if user:
            self.set_cookie("username",user)
            print "debug"
            #self.set_secure_cookie("username",user)
            #self.set_cookie("username",user)
        else:
            self.clear_cookie("username")
            
    def post(self):
        print self.request.body_arguments.keys()
        username = self.get_argument("username","")
        password = self.get_argument("password","")
        #The authenticate method should match a username and password 
        #to a username and password hash in the database users table.
        #Implementation left as an exercise for the reader
        print username
        print password
        auth = self.authenticate(username,password)
        if auth:
            self.set_current_user(username)
            self.redirect(self.get_argument("next",u"/"))
        else:
            error_msg = u"?error=" + tornado.escape.url_escape("Login incorrect")
            self.redirect(u"/login"+error_msg)
            
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie("username")
        self.redirect("/login")
#******************* End *************************************#

#*************       
class Application(tornado.web.Application):
    def __init__(self):
        self.pageNum = 10
        handlers=[
            (r"/index",IndexHandler),
            (r"/",HostHandler),
            (r"/host",HostHandler),
            (r"/host/get",HostManageHandler),
            (r"/host/all",HostAllHandler),
            (r"/host/get/(\w+)",HostManageHandler),
            (r"/host/del/(\w+)",HostManageHandler),
            (r"/host/del",HostManageHandler),
            (r"/host/post",HostManageHandler),
            (r"/host/query/",HostQueryHandler),
            (r"/host/update/",HostUpdateHandler),
            (r"/host/group/(\d+)",HostGroupHandler),
            (r"/test",TestHandler),
            
            (r"/group",GroupHandler),
            (r"/group/",GroupManageHandler),
            (r"/group/all",GroupAllHandler),
            (r"/group/get/(\w+)",GroupManageHandler),
            (r"/group/query/",GroupQueryHandler),
            (r"/group/member/(\d+)",GroupMemberHandler),
            (r"/group/update",GroupUpdateHandler),
            
            (r"/project",ProjectHandler),
            (r"/project/",ProjectManagerHandler),
            (r"/project/service/(\w+)",ProServiceHandler),
            (r"/project/init/",InitProjectHandler),
            
            #***********  V0.0.2 Playbook  manager ********** 
            (r"/addplaybook",AddPlayBookHandler),
            (r"/playbookmanager/(\w+)/(\d*)",PlayBookManagerHandler),
            (r"/playbookmanager/key/(\d*)",PlayBookKeyHandler),
            #**
            
            #********* V0.0.2 Argument template *************
            
            (r"/argument",ArgumentIndexHandler),
            (r"/argument/(\w+)/(\d*)",ArgumentHandler),
            #**
            
            #********* V0.0.2 Action manager ************#
            (r"/action",ActionIndexHandler),
            (r"/actionmanager/(id)/(\d*)",ActionHandler),
            (r"/actionmanager/(page)/(\d*)",ActionHandler),
            (r"/actionmanager/owner/(host)/(\d*)",ActionOwnerHandler),
            (r"/actionmanager/owner/(hostgroup)/(\d*)",ActionOwnerHandler),
            (r"/actionmanager/run/(\d*)",ActionRunHandler),
            (r"/actionmanager/history/(\d*)",ActionRunHistory),
            #**
            
            #********* V0.0.2 Authticate ***************#
            (r"/login",LoginHandler),
            (r"/logout",LogoutHandler),
            #**
            #********* V0.0.2 Remote Login *************#
            (r"/ws", WSHandler),
            (r"/test", TestHandler),
            #**
            (r"/conftmp",ConfHandler),
            (r"/conftmp/",ConfManagerHandler),
            (r"/conftmp/all",ConfAllHandler),
            (r"/conftmp/key/(\w+)",ConfKeyHandler),
            (r"/conftmp/key/",ConfKeyHandler),
            
            (r"/servicemange",ServiceManage),

            (r"/deploycode",DeployCodeHandler),
        ]
        settings = {
            "cookie_secret":"bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
            "template_path":os.path.join(os.path.dirname(__file__),"template"),
            'static_path':os.path.join(os.path.dirname(__file__), "static"),
            'debug':True,
            'login_url':'/login',
        }
        self.playbookQ  = []
        self.actionlogpath = "/tmp/ansible-action-log/"
        self.playbookpath = '/data/web/testplaybook'
        self.db = lambda : MySQLdb.connect(host='127.0.0.1',user='root',passwd='root',db='deltaOPS',charset='utf8')
        tornado.web.Application.__init__(self, handlers,**settings)
        
if __name__ == "__main__":
   
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    IOLoop.instance().start()
    tornado.ioloop.IOLoop.instance().start()
    
    
