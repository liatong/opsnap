#!/usr/bin/env python
import ansibleapi
import MySQLdb
class serviceHandlerFactor(object):
    def __init__(self,action,project,service,dbcon):
        self.params={}
        self.action = action
        self.params['Pid'] = self.project = int(project) 
        self.params['Sid'] = self.service = int(service) 
        self.dbcon = dbcon
        self.cur = self.dbcon.cursor()
        self.__getparams()
        self.handers = {
            'init':initServiceHandler(self.params,self.dbcon),
            'start':startServiceHandler(self.params,self.dbcon),
            'restart':restartServiceHandler(self.params,self.dbcon),
            'stop':stopServiceHandler(self.params,self.dbcon),
        }
    def __getparams(self):
        self.__get_pjpath_sql = "select HostIP,ProName,ProPath,ServiceRoot,ProType from Project JOIN Host ON Project.HostID=Host.id where Project.id=%s"
        self.__get_sdir_sql = "select name,DirName from Service where id=%s"
        self.cur.execute(self.__get_pjpath_sql % self.project)
        result = self.cur.fetchone()
        self.cur.execute(self.__get_sdir_sql % self.service)
        result1 = list(self.cur.fetchone())
        self.cur.close()
        self.params['hosts'] = result[0]
        self.params['ProjectName']=result[1]
        self.params['ProjectPath']=result[2]
        self.params['ServiceRoot']=result[3]
        self.params['ProType']= result[4]        
        self.params['service']=result1[0]
        self.params['serviceDir']=result1[1]
        
    def createPlaybook(self):
        return self.handers[self.action]
        
class serviceBaseHandler(object):
    def __init__(self,params,dbcon):
        self.params = params
        self.dbcon = dbcon
        self.data = {'status':'success'}
        
    def get_playbook(self):
        return self._playbook
        
    def get_result(self):
        return self.data
    
    def execute(self):
        try:
            print self.params
            pl = ansibleapi.AnsiblePlayBook(self._playbook,self.params)
            pl.execute()
            plresult = pl.get_result()
            print plresult
            if plresult[self.params['hosts']]['failures'] == 0 and plresult[self.params['hosts']]['unreachable'] == 0 :
                self.updateServicePid()
            else:
                self.data['status'] = 'fail'
                self.data['info'] = "run playbook fail! %s" % self.plresult
        except:
            self.data['status'] = 'fail'
            self.data['info'] = "run service playbook fail!"
            
class initServiceHandler(serviceBaseHandler):
    def __init__(self,params,dbcon):
       self._playbook = '/data/web/playbook/startService.yml'
       super(initServiceHandler,self).__init__(params,dbcon)
    
    def execute(self):
        try:
            #print "debug ----%s:playbook%s" %(self.params,self._playbook)
            # print "debug+" + self.params
            pl = ansibleapi.AnsiblePlayBook(self._playbook,self.params)
            pl.execute()
            plresult = pl.get_result()
            print plresult[self.params['hosts']]
            if plresult[self.params['hosts']]['failures'] == 0 and plresult[self.params['hosts']]['unreachable'] == 0 :
                try:
                    sql = "INSERT INTO Map_Pro_Service(Pid,ProType,Sid,status,servicePID) VALUES(%s,%s,%s,'init',0)"
                    sql1 = "UPDATE Map_Pro_Service set status='init' where  Pid=%s and ProType='%s'  and Sid=%s"
                    cur = self.dbcon.cursor()
                    try:
                        cur.execute(sql %(self.params['Pid'],self.params['ProType'],self.params['Sid']))
                    except:
                        cur.execute(sql1 %(self.params['Pid'],self.params['ProType'],self.params['Sid']))
                    self.dbcon.commit()
                    self.data['info'] = "success! %s " % plresult
                except:
                    self.dbcon.rollback()
                    self.data['status']='fail'
                    self.data['info'] = "update service status fail!"
            else:
                self.data['status'] = 'fail'
                self.data['info'] = "run initplaybook fail! %s" % plresult
        except:
            self.data['status'] = 'fail'
            self.data['info'] = "get initplaybook fail!"
            
            
class startServiceHandler(serviceBaseHandler):
    def __init__(self,params,dbcon):
       self._playbook = '/data/web/playbook/startService.yml'
       super(startServiceHandler,self).__init__(params,dbcon)
       
    def updateServicePid(self):
        rt = 1
        hosts = self.params['hosts']
        module = "shell"
        args = " cd %s/%s && ./%s/run show" % (self.params['ProjectPath'],self.params['ServiceRoot'],self.params['serviceDir'])
        asmodule = ansibleapi.AnsibleModle(module,args,hosts)
        asresult = asmodule.run()
        
        if asresult['contacted'][hosts]['stderr'] == "" and asresult['contacted'][hosts]['rc'] == 0:
            servicePID = int(asresult['contacted'][hosts]['stdout'].split()[0])
            sql = " UPDATE Map_Pro_Service set status='running',servicePID=%s where Pid=%s and Sid=%s"
            cur = self.dbcon.cursor()
            try:
                print "Service Pid:%s" % servicePID
                self.data['pid']=servicePID
                cur.execute(sql % (servicePID,self.params['Pid'],self.params['Sid']))
                self.dbcon.commit()
            except:
                self.dbcon.rollback()
                self.data['status'] = 'fail'
                self.data['info'] = "update service pid   fail! %s"
                rt = 0 
        else:
            self.data['status'] = 'fail'
            self.data['info'] = "get service pid  fail! %s" % asresult
            rt = 0
        print "rt:%d" %rt
        return rt 
        
class restartServiceHandler(serviceBaseHandler):
    def __init__(self,params,dbcon):
       self._playbook = '/data/test.yml'
       super(restartServiceHandler,self).__init__(params,dbcon)
    
class stopServiceHandler(serviceBaseHandler):
    def __init__(self,params,dbcon):
       self._playbook = '/data/web/playbook/stopService.yml'
       super(stopServiceHandler,self).__init__(params,dbcon)
    
    def updateServicePid(self):
        rt = 1
        print "stop update"
        try:
            servicePID = int(asresult['contacted'][host]['stdout'].split(" ")[0])
            sql = " UPDATE Map_Pro_Service set status='stop',servicePID='0' where Pid=%s and Sid=%s"
            cur = self.dbcon.cursor()
            try:
                cur.execute(sql % (self.params['Pid'],self.params['Sid']))
                self.dbcon.commit()
            except:
                rt = 0 
                self.dbcon.rollback()
                self.data['status'] = 'fail'
                self.data['pid']='0'
                self.data['info'] = "update service pid   fail! %s"
        except:
            rt = 0
            self.data['status'] = 'fail'
            self.data['pid']=0
            self.data['info'] = "update service pid   fail! %s"
        return rt
class test(object):
    def __init__(self,name,passwd):
        self.name = name
        self.passwd = passwd
    def say(self):
        print "name:%s,passwd:%s" %(self.name,self.passwd)
        
class test2(test):
    def __init__(self,name,passwd):
        super(test2,self).__init__(name,passwd)
        
if __name__=='__main__':
    db = MySQLdb.connect(host='127.0.0.1',user='root',passwd='root',db='deltaOPS')
    playbook = serviceHandlerFactor('start','7','1',db).createPlaybook()
    playbook.execute()
    plresult = playbook.get_result()
    print plresult
    #print playbook.get_playbook()
    # params = {'service': 'lbs', 'ProType': 'vidagrid', 'ProjectPath': '/data/app', 'Sid': 1, 'Pid': 7, 'ServiceRoot': 'm4server', 'serviceDir': 'lbserver', 'hosts': '172.17.92.168', 'ProjectName': 'xmserver-xm-server'}
    # playbook = '/data/web/playbook/startService.yml'
    # pl = ansibleapi.AnsiblePlayBook(playbook,params)
    # pl.execute()
    # plresult = pl.get_result()
    # print plresult
    # print plresult
    # t2 = test2('wt','123')
    # t2.say()
    
 
    
