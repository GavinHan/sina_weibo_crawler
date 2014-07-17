#!/usr/bin/env python  
# -*- coding: utf-8 -*-  
import urllib
import urllib2  
import sys,re
  
reload(sys)  
sys.setdefaultencoding('utf-8')  
  
class GetWeiboPage:   
    def get_page(self,url):  
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}
        req = urllib2.Request(url= url,  
                                      data=urllib.urlencode({}),  
                                      headers=self.headers)  
        result = urllib2.urlopen(req)  
        myPage = result.read()  
        oneList = re.findall('<table>(.*?)</table>',myPage)
        for item in oneList:
            oneItem = re.findall('<td valign="top"><a href="(.*?)">(.*?)</a>',item)
            #import pdb; pdb.set_trace()
            newUrl = oneItem[0][0]
            nickName = oneItem[0][1]
            
            print newUrl,nickName.encode('gbk')

        #self.writefile('./output/text1',text)         

    def writefile(self,filename,content):  
        fw = file(filename,'w')  
        fw.write(content)  
        fw.close()  