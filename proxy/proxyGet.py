#!/usr/bin/env python
#coding=utf-8
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''
import urllib2
import re
import sys
import threading
import time
from pyquery import PyQuery as pq

reload(sys)
sys.setdefaultencoding('utf-8')

rawProxyList = []
checkedProxyList = []

#八个目标网站
targets = ['http://www.proxy360.cn/default.aspx']

#获取代理的类
class ProxyGet(threading.Thread):
    def __init__(self,target):
        threading.Thread.__init__(self)
        self.target = target

    def getProxy(self):
        def _check_page_right(self, page):
            pass

        def _perser(i):
            node = pq(this)
            #import pdb; pdb.set_trace()
            ip = node.find('.tbBottomLine:first').html().strip()
            port = node.find('.tbBottomLine:first').next().html().strip()
            proxy = [ip,port]
            rawProxyList.append(proxy)
            
        print u"目标网站:  " + self.target
        right = False; tries = 0
        while not right and tries <= 20:
            try:
                req = urllib2.urlopen(self.target)
                page = req.read()
                right = True
            except Exception:
                right = False
                time.sleep(3)
            tries += 1
        if right:
            doc = pq(page)
            div = doc('div').find('.proxylistitem')
            div.each(_perser)
        else:
            print self.target+' read error'

    def run(self):
        self.getProxy()

#检验代理的类
class ProxyCheck(threading.Thread):
    def __init__(self,proxyList):
        threading.Thread.__init__(self)
        self.proxyList = proxyList
        self.timeout = 5
        self.testUrl = "http://www.baidu.com/"
        self.testStr = "030173"

    def checkProxy(self):
        cookies = urllib2.HTTPCookieProcessor()
        for proxy in self.proxyList:
            proxyHandler = urllib2.ProxyHandler({"http" : r'http://%s:%s' %(proxy[0],proxy[1])})
            #print r'http://%s:%s' %(proxy[0],proxy[1])
            opener = urllib2.build_opener(cookies,proxyHandler)
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:15.0) Gecko/20100101 Firefox/15.0.1')]
            #urllib2.install_opener(opener)
            t1 = time.time()

            try:
                #req = urllib2.urlopen("http://www.baidu.com", timeout=self.timeout)
                req = opener.open(self.testUrl, timeout=self.timeout)
                #print "urlopen is ok...."
                result = req.read()
                #print "read html...."
                timeused = time.time() - t1
                pos = result.find(self.testStr)
                #print "pos is %s" %pos

                if (pos > -1):
                    checkedProxyList.append((proxy[0],proxy[1],timeused))
                    #print "ok ip: %s %s %s %s" %(proxy[0],proxy[1],proxy[2],timeused)
                else:
                    continue
            except Exception,e:
                #print e.message
                continue

    def sort(self):
        sorted(checkedProxyList,cmp=lambda x,y:cmp(x[2],y[2]))

    def run(self):
        self.checkProxy()
        self.sort()

if __name__ == "__main__":
    getThreads = []
    checkThreads = []

    #对每个目标网站开启一个线程负责抓取代理
    for i in range(len(targets)):
        t = ProxyGet(targets[i])
        getThreads.append(t)

    for i in range(len(getThreads)):
        getThreads[i].start()

    for i in range(len(getThreads)):
        getThreads[i].join()

    print u".......................总共抓取了%s个代理......................." %len(rawProxyList)

    #开启20个线程负责校验，将抓取到的代理分成20份，每个线程校验一份
    for i in range(20):
        t = ProxyCheck(rawProxyList[((len(rawProxyList)+19)/20) * i:((len(rawProxyList)+19)/20) * (i+1)])
        checkThreads.append(t)

    for i in range(len(checkThreads)):
        checkThreads[i].start()

    for i in range(len(checkThreads)):
        checkThreads[i].join()

    print u".......................总共有%s个代理通过校验......................." %len(checkedProxyList)

    #持久化
    f= open("t1.txt",'a')
    for proxy in checkedProxyList:
        print "checked proxy is: %s:%s\t%s\n" %(proxy[0],proxy[1],proxy[2])
        f.write("%s:%s\t%s\n"%(proxy[0],proxy[1],proxy[2]))
    f.close()