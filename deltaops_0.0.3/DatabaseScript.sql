
'''
主机:
    主机管理表 host： Id,HostName,HostIp,HostType,HostPosition
    主机组 HostGroup: id,GroupName
    主机组&主机关联表 Map_Host_Group： id,HostID,GroupID
    log: id,action,objectid,objectname,time,
    
项目：
    项目管理： Id,ProjectName,ProjectPath,HostID,TemplateID,Type,Status

配置模板：
    模板表： Id,Template_Name,detail,
    模板key对应表： Id, Tid,key,value
    ##模板&项目关联表：  Id,ProId,TemplateId
    
代码管理：
    Git仓库：  Id,RepositoryName,GitServer,CommitID,CommitTime,Detail
    项目&仓库管理表：id,ProID,Repo,CommitID,CommitTime,GitRepoId,Detail,
    发布记录:  Id,ProName,Host,ProPath,DestRepo,SourceGit,CommitId,CommitTime,DeployTime,Detail
    
    
Service 管理表
    service表： id,name,DirName,
    service&Project 表：id,Pid,ProType,sid,status,servicePID
   
playbook 管理表
    playbook表： id,actionName,playbook,note,UploadTime,UpdateTime,Author,MD5,  主键为ID:
    
'''

'***** palybook 管理表 V0.0.2 ****'
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

'**** argument template 参数模板表 V0.0.2'
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

'*****　action table 管理表，所有action关联的主机，playbook,参数模板 v0.0.2'
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
'****** Action 动作执行日志 **************'
CREATE TABLE Actionhistory(
id int NOT NULL AUTO_INCREMENT,
actionid int NOT NULL,
runtime datetime,
status varchar(50),
runlog varchar(2000),
FOREIGN KEY(actionid) REFERENCES Action(id),
PRIMARY KEY(id)
);


CREATE TABLE TmpHistory(
id int NOT NULL AUTO_INCREMENT,
actionid int ,
logcomment varchar(5000),
PRIMARY KEY(id)
);
'********** Authenticate 用户验证管理 ****************'
CREATE TABLE  deltauser(
id int NOT NULL AUTO_INCREMENT,
username varchar(50) NOT NULL,
password varchar(50) NOT NULL,
failtime int,
status varchar(20),
logintime varchar(30),
PRIMARY KEY(id)
);



'****** END V0.0.02******'


CREATE TABLE Service(
id int NOT NULL AUTO_INCREMENT,
stype varchar(30) NOT NULL,
name varchar(30) NOT NULL,
DirName varchar(30) NOT NULL,
PRIMARY KEY (id)
);



CREATE TABLE Map_Pro_Service(
id int NOT NULL AUTO_INCREMENT,
Pid int NOT NULL,
ProType varchar(30) NOT NULL,
Sid int NOT NULL,
status varchar(30) DEFAULT 'uninit',
servicePID int DEFAULT 0,
FOREIGN KEY(Pid) REFERENCES Project(id),
FOREIGN KEY(Sid) REFERENCES Service(id),
CONSTRAINT uc_pidsid UNIQUE(Pid,Sid),
PRIMARY KEY(id)
);

CREATE TABLE  Host 
(
id int NOT NULL AUTO_INCREMENT,
HostName varchar(255) NOT NULL,
HostIP varchar(255) NOT NULL,
HostType varchar(255),
HostPosition varchar(255),
CONSTRAINT uc_hostip UNIQUE(HostName,HostIP),
PRIMARY KEY (id)
);

CREATE TABLE HostGroup
(
id int NOT NULL AUTO_INCREMENT,
GroupName varchar(255) NOT NULL,
CONSTRAINT uc_groupname UNIQUE (GroupName),
PRIMARY KEY(id)
);

CREATE TABLE Map_Host_Group
(
id int NOT NULL AUTO_INCREMENT,
HostID int,
GroupID int,
PRIMARY KEY(id),
FOREIGN KEY (HostID) REFERENCES Host(id),
FOREIGN KEY (GroupID) REFERENCES HostGroup(id)
);

CREATE TABLE Template
(
id int NOT NULL AUTO_INCREMENT,
Template varchar(255) NOT NULL,
UNIQUE(Template),
PRIMARY KEY (id)
);


CREATE TABLE TemplateKey
(
id int NOT NULL AUTO_INCREMENT,
tid int NOT NULL,
keyname varchar(255) NOT NULL,
value varchar(255) NOT NULL,
CONSTRAINT uc_keyvalue UNIQUE (tid,keyname,value),
PRIMARY KEY(id)
);

CREATE TABLE Project 
(
id int NOT NULL,
ProName varchar(255) NOT NULL,
ProPath varchar(255) NOT NULL,
ProType varchar(255) NOT NULL,
HostID int,
TemplateID int,
FOREIGN KEY (HostID) REFERENCES Host(id),
FOREIGN KEY (TemplateID) REFERENCES Template(id),
Status varchar(255) DEFAULT 'UNINIT',
PRIMARY KEY (id)
);

'Git仓库：  Id,RepositoryName,GitServer,CommitID,CommitTime,Detail'

CREATE TABLE gitRepo
(
id int NOT NULL AUTO_INCREMENT,
RepoName varchar(255) NOT NULL,
Server varchar(255) NOT NULL,
CommitID varchar(255),
CommitTime varchar(255),
Detail varchar(255),
PRIMARY KEY (id)
);

'项目&仓库管理表：id,ProID,Repo,CommitID,CommitTime,GitRepoId,Detail,'

CREATE TABLE ProjectRepo
(
id int NOT NULL AUTO_INCREMENT,
ProID int NOT NULL,
Repo varchar(50) NOT NULL,
CommitID int,
CommitTime varchar(255),
GitRepoId int,
Detail varchar(255),
FOREIGN KEY (ProID) REFERENCES Project(id),
FOREIGN KEY (GitRepoId) REFERENCES gitRepo(id),
CONSTRAINT uc_projectRepo UNIQUE (ProID,Repo),
PRIMARY KEY (id)
);

'发布记录:  Id,ProName,Host,ProPath,DestRepo,SourceGit,CommitId,CommitTime,DeployTime,Detail'
CREATE TABLE DeployLog
(
id int NOT NULL,
ProName varchar(50) NOT NULL,
Host varchar(50),
ProPath varchar(255),
DestRepo varchar(255),
SourceGit varchar(255),
CommitID varchar(20),
CommitTime varchar(255),
DeployTime varchar(255),
Detail varchar(255),
PRIMARY KEY (id)
);

