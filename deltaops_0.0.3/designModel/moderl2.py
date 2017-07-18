#!/usr/bin/env python 
#
#
#
#
'''
    观察者模式：获取数据方式observer主动的pull，好处是observer能够决定get哪些数据。
'''
class Subject(object):
    def __init__(self,name):
        self.__name = name
        self.__observers= []
        self.__args = "hello world"
    
    def register(self,observer):
        if self.__observers.__contains__(observer) is False:
            self.__observers.append(observer)

    def unsubscribe (self,observer):
        if self.__observers.__contains__(observer) is True:
            self.__observers.remove(observer)
          
    def set_change(self):
        self.__changeStatus = True
        
    def notification(self):
        if self.__changeStatus is True:
            for observer in self.__observers:
                observer.update(self)
            self.__changeStatus = False
    
    def setArgs(self,args):
        self.__args = args
        self.set_change()
        self.notification()
        
    def getArgs(self):
        return self.__args
        
    def getName(self):
        return self.__name
        
class Observer(object):
    
    def __init__(self,descript):
        self.descript = descript
        
    def update(self,subject):
        self.title = subject.getArgs()
        self.sub = subject.getName()
        self.show()
        
    def show(self):
        print "subject:%s observer:%s ,Title:%s" % (self.sub,self.descript,self.title)
        
if __name__ == "__main__":
    sub1 = Subject('SUB1')
    sub2 = Subject('SUB2')
    ob1 = Observer('test1')
    ob2 = Observer('test2')
    ob3 = Observer('test3')
    sub1.register(ob1)
    sub1.register(ob2)
    sub1.register(ob3)
    sub2.register(ob3)
    sub1.setArgs('Fly sky')
    sub1.setArgs('Yeah all oberver had update')
    sub2.setArgs("sub2 update")
    
