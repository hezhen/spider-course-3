import datetime
from datetime import datetime
from pymongo import MongoClient


class FeedsMongoManager:
    def __init__(self, SERVER_IP = 'localhost', port=27017, client=None):
        # if a client object is not passed
        # then try connecting to mongodb at the default localhost port
        self.client = MongoClient(SERVER_IP, port) if client is None else client
        #create collection to store cached webpages,
        # which is the equivalent of a table in a relational database
        self.db = self.client.spider

    def get_feed_by_user(self, uid, offset, size):
        record = self.db.weibo.find_one(
            {'status': 'new'}
        )
        if record:
            return record
        else:
            return None

    def insert_feed(self, feed, time):
        try:
            self.db.weibo.insert({'uid':feed['mblog']['user']['id'],
                                  'itemid':feed['itemid'],
                                  'scheme':feed['scheme'],
                                  'created_at':feed['mblog']['created_at'],
                                  'feed': feed})
        except Exception, Arguments:
            pass

    def clear(self):
        self.db.mfw.drop()