#!/usr/bin/env python
#coding=utf-8
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''

import re
import urllib,urllib2
import random, time
from datetime import datetime, timedelta
from threading import Lock
from pyquery import PyQuery as pq

class GetPage(object):
    def __init__(self, url, span = True):
        self.url = url
        if span:
            time.sleep(random.uniform(0,40))
        
    def fetch(self):
        print self.url
        headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        tries = 0
        while tries <= 6:
            try:    
                req = urllib2.Request(url= self.url, data=urllib.urlencode({}), headers=headers)
                result = urllib2.urlopen(req)  
                html = result.read()
                break
            except Exception, e:
                sec = 10 * (tries + 1) if tries <= 2 else (600 * (tries - 2) if tries < 6 else 3600)
                time.sleep(sec)
                tries += 1
        if tries > 6:
            return None
        else:
            return html

class WeiboParser(object):
    strptime_lock = Lock()
    def __init__(self, url_start, user, storage):
        self.uid = user
        self.storage = storage
        self.url = url_start
        
    def _strptime(self, string, format_):
        self.strptime_lock.acquire()
        try:
            return datetime.strptime(string, format_)
        finally:
            self.strptime_lock.release()
        
    def parse_datetime(self, dt_str):
        dt = None
        if u'秒' in dt_str:
            sec = int(dt_str.split(u'秒', 1)[0].strip())
            dt = datetime.now() - timedelta(seconds=sec)
        elif u'分钟' in dt_str:
            sec = int(dt_str.split(u'分钟', 1)[0].strip()) * 60
            dt = datetime.now() - timedelta(seconds=sec)
        elif u'今天' in dt_str:
            dt_str = dt_str.replace(u'今天', datetime.now().strftime('%Y-%m-%d'))
            # dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M')
            dt = self._strptime(dt_str, '%Y-%m-%d %H:%M')
        elif u'月' in dt_str and u'日' in dt_str:
            this_year = datetime.now().year
            # dt = datetime.strptime('%s %s' % (this_year, dt_str), '%Y %m月%d日 %H:%M')
            dt = self._strptime('%s %s' % (this_year, dt_str), '%Y %m月%d日 %H:%M')
        else:
            # dt = datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
            dt = self._strptime(dt_str, '%Y-%m-%d %H:%M:%S')
        return time.mktime(dt.timetuple())
        
    def parse(self):
        def _parse_weibo(i):
            node = pq(this)
            
            if node.attr('id') is None:
                return
            
            n = 0
            divs = node.children('div')
            for div in divs:
                if len(pq(div).find('img.ib')) == 0:
                    n += 1
            if n == 0:
                return
            
            weibo = {}
            is_forward = True if len(divs) == 2 else False
            content = pq(divs[0]).children('span.ctt').text()
            if is_forward:
                weibo['forward'] = content
            else:
                weibo['content'] = content
            if is_forward:
                div = pq(divs[-1])
                weibo['content'] = div.text().split(u'赞')[0].strip(u'转发理由:').strip()
            # get weibo's datetime
            dt_str = pq(divs[-1]).children('span.ct').text()
            if dt_str is not None:
                dt_str = dt_str.replace('&nbsp;', ' ').split(u'来自', 1)[0].strip()
            weibo['ts'] = int(self.parse_datetime(dt_str))
            self.storage.save_weibo(weibo)
        
        page = GetPage(self.url)
        html = page.fetch()
        doc = pq(html)
        try:
            div = doc('div#pagelist.pa')
            pages = int(div('div input:first').attr('value'))
            doc.find('div.c').each(_parse_weibo)
        except:
            pages = 1
            pass
        
        if pages > 500:
            pages = 500
        for i in range(2,pages+1):
            self.url = 'http://weibo.cn/'+str(self.uid)+'/profile?page='+str(i)
            page = GetPage(self.url)
            html = page.fetch()
            doc = pq(html)
            doc.find('div.c').each(_parse_weibo)

class InfoParser(object):
    def __init__(self, url_start, user, storage):
        self.url = url_start
        self.user = user
        self.storage = storage
    def parse(self):
        page = GetPage(self.url)
        html = page.fetch()
        doc = pq(html)
        divAll = doc.find('div.tip').next('div.c')
        if divAll is None:
            return
        tip = doc.find('div.tip')
        i = 0
        info = {u'经历':[]}
        for div in divAll('.c'):
            if tip.eq(i).html() != '其他信息':
                #print tip.eq(i).html()
                i += 1
                div = pq(div).html()
                div = div.replace('\n', '').replace('<br />', '<br/>').replace('·','')
                for itm in div.split('<br/>'):
                    if len(itm.strip()) == 0:
                        continue
                    kv = tuple(itm.split(':', 1))
                    if len(kv) != 2:
                        info[u'经历'].append(kv[0].strip())
                    else:
                        k, v = kv[0], pq(kv[1]).text().strip('更多>>').strip()
                        info[k] = v
        
            else:
                break
        self.storage.save_info(info)

class RelationshipParser(object):
    def __init__(self, url_start, user, storage):
        self.url = url_start
        self.uid = user
        self.storage = storage

    def parse(self):
        def _parse_user(i):
            node = pq(this)
            if len(node.children('img')) > 0:
                return
            self.storage.save_user((self.uids[self.j],node.text(), ))
            self.j += 1
            # self.storage.save_user((node.attr('href'), self.user, ))
        def _parse_uid(i):
            node = pq(this)
            # self.storage.save_user((node.attr('href'), node.text(), ))
            if node.attr('name') == 'uidList':
                self.uids = node.attr('value').split(',')
                self.j = 0

        page = GetPage(self.url)
        html = page.fetch()
        doc = pq(html)
        try:
            div = doc('div#pagelist.pa')
            pages = int(div('div input:first').attr('value'))
            doc('.c div input').each(_parse_uid)
            doc.find('table tr td a:first').each(_parse_user)
        except:
            pages = 1
            pass
        if pages > 500:
            pages = 500
        for i in range(2,pages+1):
            self.url = 'http://weibo.cn/'+str(self.uid)+'/follow?page='+str(i)
            page = GetPage(self.url)
            html = page.fetch()
            doc = pq(html)
            doc('.c div input').each(_parse_uid)
            doc.find('table tr td a:first').each(_parse_user)

