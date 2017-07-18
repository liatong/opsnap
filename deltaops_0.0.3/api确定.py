

接口数据：

gorup/get/    get获取所有组   { id:['id','groupName'],id:['id','groupName'],id:['id','groupName']  }
group/get/id  get获取指定组   { id:['id','groupName'] }
group/     post添加组     JSON:{ 'groupname':'groupanemvalue','groupname':'groupanemvalue'}
group/del  删除主机组     POST: {'id':'[]'}
group/update  更新主机组  {'id':''}  仅提供更新一个而已
host/update/   post更新主机  {'id':'1','hostname','ip':'1.1.1.1','type':'cloud','position':'xm'}
host/query?query=%xmserver%   {id:[id,name],id:[id,name]}
group/add/host/               {id:[11,23,44,55],id,:[12,12,12]}
项目:
project/    get获取所有project
project/id  get获取某个project

project/del/  post删除project  {'id':'['1','2']'}, {'id':'[1]'}
project/add/  post添加project  {'id':''}
project/update/  post 更新 {'id':'1','name':'name','type':'vidagrid',}


代码管理 


