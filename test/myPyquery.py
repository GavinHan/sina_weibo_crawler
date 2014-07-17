#coding: utf-8
import re
from pyquery import PyQuery as pq
from lxml import etree

page = '''

'''

doc = pq(page)


def get_url():
    pg = doc.find('div#pagelist.pa')
    url_right = pq(pg.find('a')[0]).attr('href')
    print re.findall('.*?page=(\d*)',url_right)[0]

def get_pages():
    div = doc('div#pagelist.pa')
    print div('div input:first').attr('value')

def parse_weibo(i):
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
    print weibo

def retweet():
    divs = doc('div.c').each(parse_weibo)

get_pages()


#print d('p') #返回<p>test 1</p><p>test 2</p>
#print d('p').html() #返回test 1
#print d('p').eq(1).html() #返回test 2