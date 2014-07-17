#coding: utf-8
import re
from pyquery import PyQuery as pq
from lxml import etree

page = '''


'''


def perser(i):
    node = pq(this)
    #import pdb; pdb.set_trace()
    ip = node.find('.tbBottomLine:first').html().strip()
    port = node.find('.tbBottomLine:first').next().html().strip()
    print ('%s:%s %s')%(ip, port)

doc = pq(page)
div = doc('div').find('.proxylistitem')
div.each(perser)


#print d('p') #返回<p>test 1</p><p>test 2</p>
#print d('p').html() #返回test 1
#print d('p').eq(1).html() #返回test 2