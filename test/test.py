#!/usr/bin/env python
#coding=utf-8
'''
 Created on 2014-7-10
 Author: Gavin_Han
 Email: muyaohan@gmail.com
'''
import datetime
from output.callback import UserCrawler

mythreads = range(3)

def callback(threadId):
    def inner():
        if threadId not in mythreads:
            mythreads.append(threadId)
    return inner

def main():
    times = 1
    end = datetime.datetime.now()
    while times < 10:
        begin = datetime.datetime.now()
        interval = (begin - end).seconds
        while mythreads:
            end = datetime.datetime.now()
            if interval > 3:
                print interval
            threadId = mythreads.pop()
            print times, threadId 
            cb = callback(threadId)
            crawler = UserCrawler(callbacks=cb)
            crawler.setName(threadId)
            crawler.start()
            times += 1
            #print mythreads

if __name__ == "__main__":
    main()