#!/usr/bin/env python
#coding=utf-8
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''

import threading
from parsers import WeiboParser, InfoParser, RelationshipParser
from log import logger

class UserCrawler(threading.Thread):
    def __init__(self, user, callbacks=None, storage=None):
        super(UserCrawler, self).__init__()

        logger.info('fetch user: %s' % user)
        self.uid = user
        if self.uid is not None:
            self.weibo_start = 'http://weibo.cn/u/%s' % self.uid

        self.storage = storage
        self.callbacks = callbacks

        self.info_start = 'http://weibo.cn/%s/info' % self.uid   
        self.follow_start = 'http://weibo.cn/%s/follow' % self.uid
        self.fan_start = 'http://weibo.cn/%s/fans' % self.uid
    
    def crawl_weibos(self):
        weibo = WeiboParser(self.weibo_start, self.uid, self.storage)
        weibo.parse()
        return True

    def crawl_info(self):
        info = InfoParser(self.info_start, self.uid, self.storage)
        info.parse()
        return True
            
    def crawl_follow(self):
        relation = RelationshipParser(self.follow_start, self.uid, self.storage)
        relation.parse()
        return True
            
    # def crawl_fans(self):
    #     RelationshipParser(self.fan_start)
    #     return True
            
    def crawl(self):
        print "start to fetch %s's follows" % self.uid
        flag_follow = self.crawl_follow()
        print "start to fetch %s's info" % self.uid
        flag_info = self.crawl_info()
        print "start to fetch %s's weibo" % self.uid
        flag_weibo = self.crawl_weibos()
        
        if flag_follow and flag_info and flag_weibo:
        # Add to completes when finished
            self.storage.complete()
            self.callbacks()

    def run(self):
        assert self.storage is not None
        try:
            self.crawl()
        except Exception, e:
            # raise e
            logger.info('error when crawl: %s' % self.uid)
            logger.exception(e)
        finally:
            if hasattr(self.storage, 'close'):
                self.storage.close()

