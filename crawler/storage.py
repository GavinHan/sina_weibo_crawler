#!/usr/bin/env python
#coding=utf-8
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''

import os
import re

from pymongo import Connection

from conf.config import mongo_host, mongo_port

class Storage(object):
    def __init__(self, uid, user=None):
        self.uid = uid
        self.user = user
        
    def save_weibo(self, weibo):
        raise NotImplementedError
    
    def save_weibos(self, weibos):
        raise NotImplementedError
    
    def save_info(self, info):
        raise NotImplementedError
    
    def save_user(self, user):
        raise NotImplementedError
    
    def save_users(self, users):
        raise NotImplementedError
    
    def crawle_queue(self):
        raise NotImplementedError

    def complete(self):
        raise NotImplementedError
    
    def error(self):
        raise NotImplementedError
    
class FileStorage(Storage):
    def __init__(self, uid, folder, create=True, user=None):
        super(FileStorage, self).__init__(uid, user=user)
        self.path = os.path.join(folder, str(uid))
        import pdb; pdb.set_trace()
        self.crawled = os.path.exists(self.path)
        if create is True and not os.path.exists(self.path):
            os.makedirs(self.path)
        self.f_path = os.path.join(self.path, 'weibos.txt')
        self.f = open(self.f_path, 'w+')
        self.info_f_path = os.path.join(self.path, 'info.txt')
        self.info_f = open(self.info_f_path, 'w')
        self.users_f_path = os.path.join(self.path, 'users.txt')
        self.users_f = open(self.users_f_path, 'w+')
        
    def save_weibo(self, weibo):
        result = unicode(weibo['content'])
        if 'forward' in weibo:
            result += '// %s' % weibo['forward']
        self.f.write(result + ' ' + str(weibo['ts']) + '\n')
        
    def save_weibos(self, weibos):
        for weibo in weibos:
            self.save_weibo(weibo)
            
    def save_info(self, info):
        for k, v in info.iteritems():
            self.info_f.write('%s：%s\n' % (k, v))
            
    def save_user(self, user_tuple):
        self.users_f.write('%s：%s' % user_tuple + '\n')
        
    def save_users(self, user_tuples):
        for user_tuple in user_tuples:
            self.save_user(user_tuple)
            
    def error(self):
        f = open(os.path.join(self.path, 'errors.txt'), 'w+')
        try:
            f.write(str(self.uid) + '\n')
        finally:
            f.close()
      
    def crawle_queue():
        pass      

    def complete(self):
        f = open(os.path.join(self.path, 'completes.txt'), 'w+')
        try:
            f.write(str(self.uid) + '\n')
        finally:
            f.close()
        
    def close(self):
        self.f.close()
        self.info_f.close()
        self.users_f.close()
        
class MongoStorage(Storage):
    def __init__(self, uid, follow=None, user=None):
        self.uid = uid
        self.user = user
        self.follow = follow
        if mongo_host is not None or mongo_port is not None:
            self.connection = Connection(mongo_host, mongo_port)
        else:
            self.connection = Connection()
        self.db = self.connection.sina
        
        self.info_data = self.db.info
        self.weibo_data = self.db.weibo
        self.relation_data = self.db.relation
        self.wait_crawled = self.db.wait_crawled
        self.completes = self.db.completes
        self.errors_data = self.db.errors
        
        data = self.weibo_data.find_one({'uid': self.uid})
        self.crawled = data is not None
        
        if data is None and follow is None:
            self.weibo_data.insert({'uid': self.uid})
        elif follow is not None:
            self.weibo_data.update({'uid': self.uid}, {'$addToSet': {'follows': follow}}, upsert=True)
        
        self.replace_reg = re.compile('(http://t.cn/\\S+)|(@\\S+)')
        
        
    def save_weibo(self, weibo):
#        content = weibo['content'].replace('http://', '!#$%&')\
#                    .split('//')[0].replace('!#$%&', 'http://')\
#                    .strip()
        content = self.replace_reg.sub('', weibo['content'])\
                    .split('//', 1)[0].strip()
        if len(content) == 0:
            return
        self.weibo_data.update({'uid': self.uid}, {'$push': { 'weibos':
            {'content': content, 'ts': weibo['ts']}
        }})
        
    def save_weibos(self, weibos):
        for weibo in weibos:
            self.save_weibo(weibo)
            
    def save_info(self, info):
        user_info = {
            u'昵称': u'nickname',
            u'达人': u'interests',
            u'性别': u'gender',
            u'简介': u'intro',
            u'地区': u'location',
            u'标签': u'tags',
            u'经历': u'experence',
        }
        mongo_info = {}
        for item in info:
            if item in user_info:
                mongo_info[user_info[item]] = info[item]
        if not self.info_data.find_one({'uid': self.uid}):
            self.info_data.insert({'uid': self.uid, 'info': mongo_info})
        
    def save_user(self, user_tuple):
        followId, nickname = user_tuple
        self.relation_data.update({'uid': self.uid}, {'$addToSet': {'follows': followId}}, upsert=True)
        
    def save_users(self, user_tuples):
        for user_tuple in user_tuples:
            self.save_user(user_tuple)
            
    def error(self):
        errors = self.db.errors
        error = {'uid': self.uid}
        if self.follow is not None:
            error['follow'] = self.follow
        errors.insert(error)
        self.completes.remove({'uid': self.user if self.user is not None else self.uid})
        self.weibo_data.remove({'uid': self.uid})
    
    def crawle_queue(self, uix):
        if not self.completes.find_one({'uid': uix}):
            self.wait_crawled.insert({'uid': uix})

    def crawle_queues(self, uidlist):
        for uix in uidlist:
            self.crawle_queue(uix)

    def complete(self):
        if self.follow is None and not self.completes.find_one({'uid': self.uid}):
            self.completes.insert({'uid': self.uid})
            #self.wait_crawled.remove({'uid': self.uid})
        else:
            self.completes.update({'uid': self.uid}, {'$addToSet': 
                {'follows': self.follow}}, upsert=True)
        # If errors contains this uid, remove it.
        err_objs = self.errors_data.find({'uid': self.uid})
        for err_obj in err_objs:
            if 'follow' in err_obj:
                self.completes.update(
                    {'uid': self.uid}, 
                    {'$addToSet': {'follows': err_obj['follow']}}
                )
            self.errors_data.remove({'uid': self.uid})
            
    def close(self):
        self.connection.close()
        