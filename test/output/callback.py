#!/usr/bin/env python
#coding=utf-8
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''
import time
import threading

class UserCrawler(threading.Thread):
    def __init__(self, callbacks=None):
        super(UserCrawler, self).__init__()
        self.callbacks = callbacks
            
    def crawl(self):
        #print self.threadId
        time.sleep(5)
        print 'hello'
        self.callbacks()

    def run(self):
        self.crawl()
        
