import urllib2
from collections import deque
import json
from lxml import etree
import httplib
import hashlib
from pybloomfilter import BloomFilter
import thread
import threading
import time
from dbmanager import CrawlDatabaseManager

from mysql.connector import errorcode
import mysql.connector

request_headers = {
    'host': "www.mafengwo.cn",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
}

def get_page_content(cur_url, index, depth):
    print "downloading %s at level %d" % (cur_url, depth)
    try:
        req = urllib2.Request(cur_url, headers=request_headers)
        response = urllib2.urlopen(req)
        html_page = response.read()
        filename = cur_url[7:].replace('/', '_')
        fo = open("%s%s.html" % (dir_name, filename), 'wb+')
        fo.write(html_page)
        fo.close()
        dbmanager.finishUrl(index)
    except urllib2.HTTPError, Arguments:
        print Arguments
        return
    except httplib.BadStatusLine, Arguments:
        print Arguments
        return
    except IOError, Arguments:
        print Arguments
        return
    except Exception, Arguments:
        print Arguments
        return
    # print 'add ' + hashlib.md5(cur_url).hexdigest() + ' to list'

    html = etree.HTML(html_page.lower().decode('utf-8'))
    hrefs = html.xpath(u"//a")

    for href in hrefs:
        try:
            if 'href' in href.attrib:
                val = href.attrib['href']
                if val.find('javascript:') != -1:
                    continue
                if val.startswith('http://') is False:
                    if val.startswith('/'):
                        val = 'http://www.mafengwo.cn' + val
                    else:
                        continue
                if val[-1] == '/':
                    val = val[0:-1]
                dbmanager.enqueueUrl(val, depth + 1)

        except ValueError:
            continue


max_num_thread = 5

# create instance of Mysql database manager, which is used as a queue for crawling
dbmanager = CrawlDatabaseManager(max_num_thread)

# dir for saving HTML files
dir_name = 'dir_process/'

# put first page into queue
dbmanager.enqueueUrl("http://www.mafengwo.cn", 0)
start_time = time.time()
is_root_page = True
threads = []

# time delay before a new crawling thread is created
# use a delay to control the crawling rate, avoiding visiting target website too frequently
# 设置超时，控制下载的速率，避免太过频繁访问目标网站
CRAWL_DELAY = 0.6


while True:
    curtask = dbmanager.dequeueUrl()
    # Go on next level, before that, needs to wait all current level crawling done
    if curtask is None:
        for t in threads:
            t.join()
        break

    # looking for an empty thread from pool to crawl

    if is_root_page is True:
        get_page_content(curtask['url'], curtask['index'], curtask['depth'])
        is_root_page = False
    else:
        while True:    
            # first remove all finished running threads
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)
            if len(threads) >= max_num_thread:
                time.sleep(CRAWL_DELAY)
                continue
            try:
                t = threading.Thread(target=get_page_content, name=None, args=(curtask['url'], curtask['index'], curtask['depth']))
                threads.append(t)
                # set daemon so main thread can exit when receives ctrl-c
                t.setDaemon(True)
                t.start()
                time.sleep(CRAWL_DELAY)
                break
            except Exception:
                print "Error: unable to start thread"

cursor.close()
cnx.close()
