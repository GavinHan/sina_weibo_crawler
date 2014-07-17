#!/usr/bin/env python  
# -*- coding: utf-8 -*-
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''

import urllib2
import urllib
import cookielib

import lxml.html as HTML

class WeiboLogin(object):
    def __init__(self, username=None, pwd=None, cookie_filename=None, enableProxy = False):
        #获取一个保存cookie的对象
        self.cj = cookielib.LWPCookieJar()
        if cookie_filename is not None:
            self.cj.load(cookie_filename)
        #将一个保存cookie对象，和一个HTTP的cookie的处理器绑定
        self.cookie_processor = urllib2.HTTPCookieProcessor(self.cj)

        if enableProxy:
            proxy_support = urllib2.ProxyHandler({'http':'202.106.16.36:3128'})#使用代理
            self.opener = urllib2.build_opener(proxy_support, self.cookie_processor, urllib2.HTTPHandler)
            print "Proxy enabled"
        else:
            self.opener = urllib2.build_opener(self.cookie_processor, urllib2.HTTPHandler)
            
        #将包含了cookie、http处理器、http的handler的资源和urllib2对象绑定在一起
        urllib2.install_opener(self.opener)

        self.username = username
        self.pwd = pwd
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; rv:14.0) Gecko/20100101 Firefox/14.0.1',
                        'Referer':'','Content-Type':'application/x-www-form-urlencoded'}

    def get_rand(self, url):
        headers = {'User-Agent':'Mozilla/5.0 (Windows;U;Windows NT 5.1;zh-CN;rv:1.9.2.9)Gecko/20100824 Firefox/3.6.9',
                   'Referer':''}
        req = urllib2.Request(url ,"", headers)
        login_page = urllib2.urlopen(req).read()
        rand = HTML.fromstring(login_page).xpath("//form/@action")[0]
        passwd = HTML.fromstring(login_page).xpath("//input[@type='password']/@name")[0]
        vk = HTML.fromstring(login_page).xpath("//input[@name='vk']/@value")[0]
        return rand, passwd, vk

    def login(self, username=None, pwd=None, cookie_filename=None):
        if self.username is None or self.pwd is None:
            self.username = username
            self.pwd = pwd
        assert self.username is not None and self.pwd is not None

        url = 'http://3g.sina.com.cn/prog/wapsite/sso/login.php?ns=1&revalid=2&backURL=http%3A%2F%2Fweibo.cn%2F&backTitle=%D0%C2%C0%CB%CE%A2%B2%A9&vt='
        # 获取随机数rand、password的name和vk
        rand, passwd, vk = self.get_rand(url)
        data = urllib.urlencode({'mobile': self.username,
                                 passwd: self.pwd,
                                 'remember': 'on',
                                 'backURL': 'http://weibo.cn/',
                                 'backTitle': '新浪微博',
                                 'vk': vk,
                                 'submit': '登录',
                                 'encoding': 'utf-8'})
        url = 'http://3g.sina.com.cn/prog/wapsite/sso/' + rand

        # 模拟提交登陆
        page =self.fetch(url,data)
        link = HTML.fromstring(page).xpath("//a/@href")[0]
        if not link.startswith('http://'): link = 'http://weibo.cn/%s' % link

        # 手动跳转到微薄页面
        self.fetch(link,"")

        # 保存cookie
        if cookie_filename is not None:
            self.cj.save(filename=cookie_filename)
        elif self.cj.filename is not None:
            self.cj.save()
        print '%s login success!'%self.username

    def fetch(self, url,data):
        req = urllib2.Request(url,data, headers=self.headers)
        return urllib2.urlopen(req).read()
