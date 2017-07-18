#!/usr/bin/env python
import sys
import ansible.playbook
from ansible import callbacks
from ansible import utils
import ansible.runner

class AnsiblePlayBook(object):
    def __init__(self,playbook,params={}):
        self.playbook = playbook
        self.params = params
        self.stats = callbacks.AggregateStats()
        self.playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        self.runner_cb = callbacks.PlaybookRunnerCallbacks(self.stats, verbose=utils.VERBOSITY)
        self.pb = ansible.playbook.PlayBook(
            playbook = self.playbook,
            stats = self.stats,
            callbacks = self.playbook_cb,
            runner_callbacks = self.runner_cb,
            check=False,
            extra_vars = self.params
        )
    def execute(self):
        try:
            self.result = self.pb.run()
        except:
            self.result = {'status':'fail','info':'Run AnsiblePlayBook FAIL!'}
            
    def get_result(self):
        return self.result
        
class AnsibleModle(object):
    def __init__(self,module,args,host):
        self.module = module
        self.args = args
        self.pattern = host
        self.runner = ansible.runner.Runner(
            module_name = self.module,
            module_args = self.args,
            pattern = self.pattern
        )
        
    def run(self):
        self.result = self.runner.run()
        return self.result
        
    def get_result(self):
        return self.result
        
if __name__=='__main__':
   #args = {'service': 'lbs', 'ProType': 'vidagrid', 'ProjectPath': '/data/app', 'Sid': 1, 'Pid': 7, 'ServiceRoot': 'm4server', 'serviceDir': 'lbserver', 'hosts': '172.17.92.168', 'ProjectName': 'xmserver-xm-server'}
   plbook = '/data/web/testplaybook/TestCopyFile.yml'
   args = {'hosts':'test01','ProjectPath':'/data/M4-Product/app'}
   p1 = AnsiblePlayBook(plbook,args)
   print "ad"
   p1.execute()
   r = p1.get_result()
   print r
   # pl = RunPlayBook(sys.argv[1],eval(sys.argv[2]))
   # cd ${project}/${serviceroot} && ./$1/run show
   # pl.execute()
   module = 'shell'
   # args = 'cd /data/M4-Product/app/server && ./vlns/run show'
   # host = '183.131.153.137'
   # asmodule = AnsibleModle(module,args,host)
   # result = asmodule.run()
   # print int(result['contacted'][host]['stdout'].split(" ")[0])
   # print result['contacted'][host]['stderr']
   # print result['contacted'][host]['rc']

  
  
   
