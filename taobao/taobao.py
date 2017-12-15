# -*- coding: utf-8 -*-
import hashlib
from collections import deque

from selenium import webdriver
import re
from lxml import etree
import time
from pybloomfilter import BloomFilter

# custom header
headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Charset': 'utf-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0',
    'Connection': 'keep-alive'
}

# set custom headers
for key, value in headers.iteritems():
    webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = value

# another way to set custome header
webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.settings.userAgent'] = \
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'

start_url = "https://detail.tmall.com/item.htm?id=540212526343"
driver = webdriver.PhantomJS(service_args=['--ignore-ssl-errors=true', '--load-images=false'])
driver.set_window_size(1280, 2400)  # optional

download_bf = BloomFilter(1024*1024*16, 0.01)
cur_queue = deque()

def enqueueUrl(url):
    try:
        md5v = hashlib.md5(url).hexdigest()
        if md5v not in download_bf:
            cur_queue.append(url)
            download_bf.add(md5v)
        # else:
            # print 'Skip %s' % (url)
    except ValueError:
        pass

def dequeuUrl():
    return cur_queue.popleft()

def crawl(url):
    print 'crawling ' + url
    # ignore ssl error, optionally can set phantomjs path
    driver.get(url)


    time.sleep(5)

    content = driver.page_source

    with open('tmall_cat.html', 'w+') as f:
        f.write(content.encode('utf-8'))

    # 使用 (pattern) 进行获取匹配
    # +? 使用非贪婪模式
    # [^>\"\'\s] 匹配任意不为 > " ' 空格 制表符 的字符
    tmall_links = re.findall('href=[\"\']{1}(//detail.tmall.com/item.htm[^>\"\'\s]+?)"', content)
    taobao_links = re.findall('href=[\"\']{1}(//detail.taobao.com/item.htm[^>\"\'\s]+?)"', content)

    etr = etree.HTML(content)
    item_price_list = etr.xpath('//span[@class="tm-price"]')
    if len(item_price_list) == 0:
        real_price = 0
    elif len(item_price_list) == 1:
        real_price = item_price_list[0].text
    else:
        real_price = etr.xpath('//dl[contains(@class, "tm-promo-cur")]//span[@class="tm-price"]')[0].text

    title = etr.xpath('//*[@class="tb-detail-hd"]/h1')[0].text
    # 正则表达式，贪婪模式匹配所有非空格字符
    # title = re.findall('([^\s]*)', title)

    # 直接去除首尾空格
    title = title.strip()

    print '+++++++++++++++++++++++++++'
    print title
    print real_price
    print '---------------------------'

    # for link in tmall_links:
    #     print link
    # for link in taobao_links:
    #     print link

    for href in tmall_links + taobao_links:
        href = "https:" + href
        enqueueUrl(href)

    crawl(dequeuUrl())


if __name__ == '__main__':
    crawl(start_url)
    driver.close()
