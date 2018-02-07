#!/usr/bin/python
# _*_ coding: UTF-8 _*_

import sys
import time
sys.path.append("..")
from Channel import *

def pushMsgToSingleDevice(channel_id, msg, opts):

    c = Channel()
    try:
        ret = c.pushMsgToSingleDevice(channel_id, msg, opts)
    except ChannelException as e:
        print e.getLastErrorMsg()
  
    
        
def pushMsgToAll(msg, opts):

    c = Channel()
    try:
        ret = c.pushMsgToAll(msg, opts)
    except ChannelException as e:
        print e.getLastErrorMsg()
        
def pushMsgToTag(tagName,msg,type,opts):
    

    c = Channel()
    try:
        ret = c.pushMsgToTag(tagName, msg, type, opts)
    except ChannelException as e:
        print e.getLastErrorMsg() 
        
def pushBatchUniMsg(channel_ids, msg, opts):  
    c = Channel()
    try:
        ret = c.pushBatchUniMsg(channel_ids, msg, opts)
    except ChannelException as e:
        print e.getLastErrorMsg() 

