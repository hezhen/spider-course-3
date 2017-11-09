# -*- coding: utf-8 -*-
import hashlib
import threading
from collections import deque

from selenium import webdriver
import re
from lxml import etree
import time
from pybloomfilter import BloomFilter

from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

user_agent = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
)

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = user_agent

feeds_crawler = webdriver.PhantomJS(desired_capabilities=dcap)
feeds_crawler.set_window_size(1920, 1200)  # optional
user_crawler = webdriver.PhantomJS(desired_capabilities=dcap)
user_crawler.set_window_size(1920, 1200)  # optional

domain = "weibo.com"
url_home = "http://" + domain

download_bf = BloomFilter(1024*1024*16, 0.01)
cur_queue = deque()

# feeds_crawler.find_element_by_class_name('WB_detail')
# time = feeds_crawler.find_elements_by_xpath('//div[@class="WB_detail"]/div[@class="WB_from S_txt2"]/a[0]').text

seed_user = 'http://weibo.com/yaochen'

min_mblogs_allowed = 100
max_follow_fans_ratio_allowed = 3

def extract_user(users):
    print 'extract user'
    for i in range(0,20):
        for user_element in user_crawler.find_elements_by_xpath('//*[contains(@class, "follow_item")]'):
            tried = 0
            while tried < 3:
                try:
                    user = {}
                    user['follows'] = re.findall('(\d+)', user_element.find_element_by_xpath('.//div[@class="info_connect"]/span').text)[0]
                    user['follows_link'] = user_element.find_element_by_xpath('.//div[@class="info_connect"]/span//a').get_attribute('href')
                    user['fans'] = re.findall('(\d+)', user_element.find_elements_by_xpath('.//div[@class="info_connect"]/span')[1].text)[0]
                    user['fans_link'] = user_element.find_elements_by_xpath('.//div[@class="info_connect"]/span//a')[1].get_attribute('href')
                    user['mblogs'] = re.findall('(\d+)', user_element.find_elements_by_xpath('.//div[@class="info_connect"]/span')[2].text)[0]
                    user_link = user_element.find_element_by_xpath('.//div[contains(@class,"info_name")]/a')
                    user['link'] = re.findall('(.+)\?', user_link.get_attribute('href'))[0]
                    if user['link'][:4] != 'http':
                        user['link'] = domain + user['link']
                    user['name'] = user_link.text
                    user['icon'] = re.findall('/([^/]+)$', user_element.find_element_by_xpath('.//dt[@class="mod_pic"]/a/img').get_attribute('src'))[0]
                    # name = user_element.find_element_by_xpath('.//a[@class="S_txt1"]')

                    print '--------------------'
                    print user['name'] + ' follows: ' + user['follows'] + ' blogs:' + user['mblogs']
                    print user['link']

                    # 如果微博数量少于阈值或者关注数量与粉丝数量比值超过阈值，则跳过
                    if int(user['mblogs']) < min_mblogs_allowed or int(user['follows'])/int(user['fans']) > max_follow_fans_ratio_allowed:
                        break

                    enqueueUrl(user['link'])
                    users.append(user)
                    break
                except Exception:
                    time.sleep(1)
                    tried += 1
        if go_next_page(user_crawler) is False:
            return users

    return users

def extract_feed(feeds):
    for i in range(0,20):
        scroll_to_bottom()
        for element in feeds_crawler.find_elements_by_class_name('WB_detail'):
            tried = 0
            while tried < 3:
                try:
                    feed = {}
                    feed['time'] = element.find_element_by_xpath('.//div[@class="WB_from S_txt2"]').text
                    feed['content'] = element.find_element_by_class_name('WB_text').text
                    feed['image_names'] = []
                    for image in element.find_elements_by_xpath('.//li[contains(@class,"WB_pic")]/img'):
                        feed['image_names'].append(re.findall('/([^/]+)$', image.get_attribute('src')))
                    feeds.append(feed)
                    print '--------------------'
                    print feed['time']
                    print feed['content']
                    break
                except Exception:
                    tried += 1
                    time.sleep(1)
        if go_next_page(feeds_crawler) is False:
            return feeds

def scroll_to_bottom():
    # 最多尝试 20 次滚屏
    print 'scroll down'
    for i in range(0,50):
        # print 'scrolling for the %d time' % (i)
        feeds_crawler.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        html = feeds_crawler.page_source
        tr = etree.HTML(html)
        next_page_url = tr.xpath('//a[contains(@class,"page next")]')
        if len(next_page_url) > 0:
            return next_page_url[0].get('href')
        if len(re.findall('点击重新载入', html)) > 0:
            print 'scrolling failed, reload it'
            feeds_crawler.find_element_by_link_text('点击重新载入').click()
        time.sleep(1)

def go_next_page(cur_driver):
    try:
        next_page = cur_driver.find_element_by_xpath('//a[contains(@class, "page next")]').get_attribute('href')
        print 'next page is ' + next_page
        cur_driver.get(next_page)
        time.sleep(3)
        return True
    except Exception:
        print 'next page is not found'
        return False

def fetch_user(user_link):
    print 'downloading ' + user_link
    feeds_crawler.get(user_link)
    time.sleep(5)
    
    # 提取用户姓名
    account_name = get_element_by_xpath(feeds_crawler, '//h1')[0].text

    photo = get_element_by_xpath(feeds_crawler, '//p[@class="photo_wrap"]/img')[0].get('src')

    account_photo = re.findall('/([^/]+)$', photo)

    # 提取他的关注主页
    follows_link = get_element_by_xpath(feeds_crawler, '//a[@class="t_link S_txt1"]')[0].get('href')

    print 'account: ' + account_name
    print 'follows link is ' + follows_link

    user_crawler.get( follows_link )

    feeds = []
    users = []

    t_feeds = threading.Thread(target=extract_feed, name=None, args=(feeds,))
    # t_users = threading.Thread(target=extract_user, name=None, args=(users,))

    t_feeds.setDaemon(True)
    # t_users.setDaemon(True)

    t_feeds.start()
    # t_users.start()

    t_feeds.join()
    # t_users.join()

def get_element_by_xpath(cur_driver, path):
    tried = 0
    while tried < 6:
        html = cur_driver.page_source
        tr = etree.HTML(html)
        elements = tr.xpath(path)
        if len(elements) == 0:
            time.sleep(1)
            continue
        return elements

def login(username, password):
    print 'Login'
    feeds_crawler.get(url_home)
    user_crawler.get(url_home)

    time.sleep(8)

    print 'find click button to login'
    feeds_crawler.find_element_by_id('loginname').send_keys(username)
    feeds_crawler.find_element_by_name('password').send_keys(password)
    # 执行 click()
    feeds_crawler.find_element_by_xpath('//div[contains(@class,"login_btn")][1]/a').click()

    # 也可以使用 execute_script 来执行一段 javascript
    # feeds_crawler.execute_script('document.getElementsByClassName("W_btn_a btn_32px")[0].click()')
    #
    user_crawler.find_element_by_id('loginname').send_keys(username)
    user_crawler.find_element_by_name('password').send_keys(password)
    # # 执行 click()
    user_crawler.find_element_by_xpath('//div[contains(@class,"login_btn")][1]/a').click()

    # for cookie in feeds_crawler.get_cookies():
    #     user_crawler.add_cookie(cookie)

def enqueueUrl(url):
    try:
        md5v = hashlib.md5(url).hexdigest()
        if md5v not in download_bf:
            print url + ' is added to queue'
            cur_queue.append(url)
            download_bf.add(md5v)
        # else:
            # print 'Skip %s' % (url)
    except ValueError:
        pass

def dequeuUrl():
    return cur_queue.popleft()

def crawl():
    while True:
        url = dequeuUrl()
        fetch_user(url)

if __name__ == '__main__':
    enqueueUrl(seed_user)
    login('18600663368', 'B69-FNw-Crq-BmT')
    crawl()
    feeds_crawler.close()
    user_crawler.close()
