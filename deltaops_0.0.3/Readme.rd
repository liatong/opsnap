#
# Version Info 
# -----------------------------------
# Author: wentong.li@deltaww.com | wt.li@139.com
# Version:
#        2016-12-06 V0.0.2
#        2016-03-03 V0.0.1
# -----------------------------------
#
# What we to do?
# -----------------------------------
# The DeltaOPS is base on the ansible to run the Action(In fact,it's the ansible playbook)
# We rewrite the ansible api with Playbook and define ourself callback.
# Have four abstract concept:  
#    1.Object:  such as host hostgroup project et.. 
#    2.Operation Script:It's ansible playbook
#    3.Arugment Template: The argument for the playbook,may be same playbook for deferent object need
#      deferent argument template.
#    4.Event(Action):  In fact, it's mean a relationship for object(host),Script(playbook),Argument.
#                   
# You can constrution any Event(Action). It mean you can do any thing that you want to do or any thing 
# that ansible module can do .
# -----------------------------------
#
# The Enviroment
# -----------------------------------
# Ansible Version: ansible 1.9.6
# Python Version: 2.7
# Mysql Version: mysql  Ver 14.14 Distrib 5.5.49, for debian-linux-gnu (x86_64) using readline 6.2
# -----------------------------------
#
  
