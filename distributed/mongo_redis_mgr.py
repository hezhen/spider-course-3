import mysql.connector
import httplib
import hashlib
import time 
from datetime import datetime
from datetime import timedelta

import redis
from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING


class MongoRedisUrlManager:

    def __init__(self, sever_ip='localhost', client=None, expires=timedelta(days=30)):
        """
        client: mongo database client
        expires: timedelta of amount of time before a cache entry is considered expired
        """
        # if a client object is not passed 
        # then try connecting to mongodb at the default localhost port 
        self.client = MongoClient(server_ip, 27017) if client is None else client
        self.redis_client = redis.StrictRedis(host=server_ip, port=6379, db=0) 
        #create collection to store cached webpages,
        # which is the equivalent of a table in a relational database
        self.db = self.client.spider

        # create index if db is empty
        if self.db.mfw.count() is 0:
            self.db.mfw.create_index([("status", ASCENDING), 
                ("pr", DESCENDING)])


    def dequeueUrl(self):
        record = self.db.mfw.find_one_and_update(
            { 'status': 'new'}, 
            { '$set': { 'status' : 'downloading'} }, 
                upsert=False, 
                sort=[('pr', DESCENDING)], # sort by pr in descending 
                returnNewDocument= False
        )
        if record:
            return record
        else:
            return None

    def enqueuUrl(self, url, status, depth):
        num = self.redis_client.get(url) 
        if num is not None:
            self.redis_client.set(url, int(num) + 1 )
            return
        self.redis_client.set(url, 1)
        self.db.mfw.insert({
            '_id': hashlib.md5(url).hexdigest(), 
            'url': url, 
            'status': status, 
            'queue_time': datetime.utcnow(), 
            'depth': depth,
            'pr': 0
        })

    def finishUrl(self, url):
        record = {'status': 'done', 'done_time': datetime.utcnow()}
        self.db.mfw.update({'_id': hashlib.md5(url).hexdigest()}, {'$set': record}, upsert=False)

    def set_url_links(self, url, links):
        self.db.urlpr.insert({
            '_id': hashlib.md5(url).hexdigest(), 
            'url': url, 
            'links': links
        })

    def clear(self):
        self.db.mfw.drop()