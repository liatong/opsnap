#!/usr/bin/env python 

class Pizza(object):
   def prepare(self):
      print "prepare"
   def bake(self):
      print "bake"
   def cut(self):
      print "cut"
   def box(self):
      print "box"

class chessPizza(Pizza):
   def prepare(self):
       print " need 2 chess"

class lnPizza(Pizza):
   def prepare(self):
       print " need 3 liu liang"

#--- havn't use any design moder ---#

class PizzaStore(object):
   
    def orderPizza(self,style):
       if style = 'chess'：
          pizza = chessPizza()
       else if style = 'ln':
          pizza = lnPizza()
       else if style = 'xc':
          pizza = xcPizza()

       pizza.prepare()
       pizza.bake()
       pizza.box()

#---- user simplet factory design moder---#


class PizzaStore(object):
    def __init__(self,factory):
       self.factory = factory 

    def oderPizza(self,style):
       pizza = self.factory.createPizza(style)
       pizza.prepare()
       pizza.bake()
       pizza.cur()
       pizza.box()
       return pizza

class simpletPizzaFactory(object):
    def createPizza(self,style):
       if style = 'chess'：
          pizza = chessPizza()
       else if style = 'ln':
          pizza = lnPizza()
       else if style = 'xc':
          pizza = xcPizza()

#------if need more define style pizza store ------#
'''
   we need deffied a factory method in our super class
   and realize it at sun class(different style)
'''
class PizzaStore(object):
   def oderPizza(self,style):
       pizza = self.createPizza(style)
       pizza.prepare()
       pizza.bake()
       pizza.cur()
       pizza.box()
   
   def createPizza(self,style):
   # this is a factory method : like a simplet factory #
       pass

#----??? why  not use this ??----#
class NYPizzaStore(PizzaStore):
   def createPizza(self,style):
      factory = NYPizzaFactory()
      pizza = factory.createPizza(style)

class NYPizzaStory(PizzaStory):
   def __init__(self):
      factory = NYPizzaFactory()
   def createPizza(self,style):
      pizza = factory.createPizza(style)

class NYPizzaFactory(simpletPizzaFactory):
   def createPizza(style):
       if style = 'chess'：
          pizza = NYchessPizza()
       else if style = 'ln':
          pizza = NYlnPizza()
       else if style = 'xc':
          pizza = NYxcPizza()
#---
nyFactory = NYPizzaFactory()
nypizzaStory = PizzaStory(nyFactory)
'''
? it's not good? if you need 10 pizzastory, you need 10 nyFactory 
so if you have NYPizzaStore() you just need  nyps = NYPizzaStore()
'''

#--- !! use this !!-----------#
class NYPizzaStore(PizzaStore):
   def create Pizza(self,style):
       if style = 'chess'：
          pizza = NYchessPizza()
       else if style = 'ln':
          pizza = NYlnPizza()
       else if style = 'xc':
          pizza = NYxcPizza()

class NYchessPizza(Pizza):
   def prepare(self):
      print " need 4 chess"
   def cut(self):
      print " cut cut "

#------------------------------#




