# -*- coding: utf-8 -*-

import requests
import threading
from mysql_db_manager import CrawlDatabaseManager
from mongo_db_manager import FeedsMongoManager
import time
import re
import json

CRAWL_DELAY = 2

MAX_PAGE = 5

class FeedsCrawler:

    url_format = "https://m.weibo.cn/api/container/getIndex?uid=%s&type=uid&value=%s&containerid=107603%s&page=%d"

    querystring = {"version":"v4"}

    payload = "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\nContent-Disposition: form-data; name=\"version\"\r\n\r\nv4\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--"
    headers = {
        'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
        'host': "m.weibo.cn",
        'connection': "keep-alive",
        'cache-control': "no-cache",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        'accept-encoding': "gzip, deflate, sdch, br",
        'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6",
        'cookie': "SCF=AlTf48qNezF12LbNvCHGGee_Nymdun-Sp9kGATl9gjhJAPPkj2QBT2-Y2MECfIjqy1QjvcBbdVr9HWi6hgbgnTQ.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WhEEfKT6-E_qQ8I2HTu2.Vu5JpX5o2p5NHD95Qp1hq4She41K-pWs4DqcjGC2Hkg.y8Kntt; SUB=_2A250CvjnDeRhGeBP7FoW9SvEwjiIHXVX9JivrDV6PUJbkdANLUvGkW1966OJJxi88Ah66us23Spcr23Dpw..; SUHB=0cSXjt5Dqq_ieZ; _T_WM=e0f6480701da87741a5b948440f9d665; SSOLoginState=1495508844; ALF=1498100844; H5_INDEX=0_all; H5_INDEX_TITLE=%E4%BD%A0%E5%B7%B2%E7%BB%8F%E8%A2%AB%E7%A7%BB%E9%99%A4%E7%BE%A4%E8%81%8A; M_WEIBOCN_PARAMS=featurecode%3D20000320%26oid%3D4110491498745329%26luicode%3D10000011%26lfid%3D231051_-_followers_-_5979396421",
        'postman-token': "0b85ea3b-073b-a799-4593-61095e4ed01a"
    }

    db_manager = CrawlDatabaseManager(10)

    feeds_db_manager = FeedsMongoManager()

    threads = []

    run = False

    def __init__(self):
        pass

    def get_time(self, created_time):
        print created_time
        # created_time = created_time.replace(' ', '')
        if u'秒前' in created_time:
            return time.time()
        mins = re.findall(u'(.*)分钟', created_time)
        if len(mins) > 0:
            return time.time() - int(mins[0])*60
        today_time = re.findall(u'今天.?(\d\d:\d\d)', created_time)
        if len(today_time) > 0:
            ct = time.strftime(u'%Y/%m/%d ') + today_time[0]
            return time.mktime(time.strptime(ct, u'%Y/%m/%d %H:%M'))

        str_time = re.findall(u'.*\d\d:\d\d', created_time)[0]

        if u'月' in str_time:
            return time.mktime(time.strptime(time.strftime(u'%Y-') + str_time, u'%Y-%m月%d日 %H:%M'))
        else:
            try:
                return time.mktime(time.strptime(str_time, u'%Y-%m-%d %H:%M'))
            except Exception:
                return time.mktime(time.strptime(time.strftime(u'%Y-') + str_time, u'%Y-%m-%d %H:%M'))

    def get_feeds(self, uid, page):
        url = (self.url_format)%(uid, uid, uid, page)
        return requests.request("GET", url, data=self.payload, headers=self.headers, params=self.querystring)

    def get_uid(self):
        uid = self.db_manager.dequeue_user()
        if uid is None:
            return None
        return uid['user_id']

    def start(self):
        self.run = True
        t = threading.Thread(target=self.crawl_feeds, name=None)
        self.threads.append(t)
        # set daemon so main thread can exit when receives ctrl-c
        t.setDaemon(True)
        t.start()

    def crawl_feeds(self):
        self.run = True

        while self.run:
            uid = self.get_uid()
            if uid is None:
                self.run = False
                break
            page = 1
            while page < MAX_PAGE:
                feeds_str = self.get_feeds(uid, page)
                page += 1
                feeds = json.loads(feeds_str.text)
                for feed in feeds['cards']:
                    if feed['card_type'] != 9:
                        continue
                    if feed.has_key('mblog'):
                        self.feeds_db_manager.insert_feed(feed, self.get_time(feed['mblog']['created_at']))
                        print '--------\n' + feed['mblog']['user']['screen_name'] + '\n--------\n' + feed['mblog']['text']

                    # item_id = feed['itemid']
                    # scheme = feed['scheme']
                    # uid = feed['mblog']['user']['id']
                    # name = feed['mblog']['user']['screen_name']
                    # profile_image_url = feed['mblog']['user']['profile_image_url']
                    # created_at = feed['mblog']['created_at']
                    # text = feed['mblog']['text']
                    # feed_id = feed['mblog']['id']
                    # reposts_count = feed['mblog']['reposts_count']
                    # comments_count = feed['mblog']['comments_count']
                    # attitudes_count = feed['mblog']['attitudes_count']
                    # page_info = feed['mblog']['page_info']
                    # pics = feed['mblog']['pics']

            time.sleep(CRAWL_DELAY)
            print feeds

if __name__ == '__main__':
    feeds_crawler = FeedsCrawler()
    feeds_crawler.crawl_feeds()