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


class CrawlBSF:
    request_headers = {
        'host': "www.mafengwo.cn",
        'connection': "keep-alive",
        'cache-control': "no-cache",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
    }

    cur_level = 0
    max_level = 5
    dir_name = 'iterate/'
    iter_width = 50
    downloaded_urls = []

    du_md5_file_name = dir_name + 'download.txt'
    du_url_file_name = dir_name + 'urls.txt'

    bloom_downloaded_urls = BloomFilter(1024 * 1024 * 16, 0.01)
    bloom_url_queue = BloomFilter(1024 * 1024 * 16, 0.01)

    cur_queue = deque()
    child_queue = deque()

    def __init__(self, url):
        self.root_url = url
        self.cur_queue.append(url)
        self.du_file = open(self.du_url_file_name, 'a+')
        try:
            self.dumd5_file = open(self.du_md5_file_name, 'r')
            self.downloaded_urls = self.dumd5_file.readlines()
            self.dumd5_file.close()
            for urlmd5 in self.downloaded_urls:
                self.bloom_downloaded_urls.add(urlmd5[:-2])
        except IOError:
            print "File not found"
        finally:
            self.dumd5_file = open(self.du_md5_file_name, 'a+')

    def enqueueUrl(self, url):
        if url not in self.bloom_url_queue and hashlib.md5(url).hexdigest() not in crawler.bloom_downloaded_urls:
            self.child_queue.append(url)
            self.bloom_url_queue.add(url)

    def dequeuUrl(self):
        try:
            url = self.cur_queue.popleft()
            return url
        except IndexError:
            return None

    def close(self):
        self.dumd5_file.close()
        self.du_file.close()


num_downloaded_pages = 0


#download the page content
def get_page_content(cur_url):
    global num_downloaded_pages
    print "downloading %s at level %d" % (cur_url, crawler.cur_level)
    try:
        req = urllib2.Request(cur_url, headers=crawler.request_headers)
        response = urllib2.urlopen(req)
        html_page = response.read()
        filename = cur_url[7:].replace('/', '_')
        fo = open("%s%s.html" % (crawler.dir_name, filename), 'wb+')
        fo.write(html_page)
        fo.close()
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

    # save page and set bloomfilter
    dumd5 = hashlib.md5(cur_url).hexdigest()
    crawler.downloaded_urls.append(dumd5)
    crawler.dumd5_file.write(dumd5 + '\r\n')
    crawler.du_file.write(cur_url + '\r\n')
    crawler.bloom_downloaded_urls.add(dumd5)
    num_downloaded_pages += 1

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
                # if hashlib.md5(val).hexdigest() not in self.downloaded_urls:
                crawler.enqueueUrl(val)
                # else:
                    # print 'Skip %s' % (val)
        except ValueError:
            continue


crawler = CrawlBSF("http://www.mafengwo.cn")
start_time = time.time()

# if it's the first page (start url), if true, crawl it in main thread in sync(blocking) mode
# 如果是第一个抓取页面的话，在主线程用同步（阻塞）的模式下载，后续的页面会通过创建子线程的方式异步爬取
is_root_page = True
threads = []
max_threads = 10

CRAWL_DELAY = 0.6

while True:
    url = crawler.dequeuUrl()
    # Go on next level, before that, needs to wait all current level crawling done
    if url is None:
        crawler.cur_level += 1
        for t in threads:
            t.join()
        if crawler.cur_level == crawler.max_level:
            break
        if len(crawler.child_queue) == 0:
            break
        crawler.cur_queue = crawler.child_queue
        crawler.child_queue = deque()
        continue


    # looking for an empty thread from pool to crawl

    if is_root_page is True:
        get_page_content(url)
        is_root_page = False
    else:
        while True:    
            # first remove all finished running threads
            for t in threads:
                if not t.is_alive():
                    threads.remove(t)
            if len(threads) >= max_threads:
                time.sleep(CRAWL_DELAY)
                continue
            try:
                t = threading.Thread(target=get_page_content, name=None, args=(url,))
                threads.append(t)
                # set daemon so main thread can exit when receives ctrl-c
                t.setDaemon(True)
                t.start()
                time.sleep(CRAWL_DELAY)
                break
            except Exception:
                print "Error: unable to start thread"

print '%d pages downloaded, time cost %0.2f seconds' % (num_downloaded_pages, time.time()-start_time)
