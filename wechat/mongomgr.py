from pymongo import MongoClient


class MongoManager:
    def __init__(self, SERVER_IP = 'localhost', port=27017, client=None):
        # if a client object is not passed 
        # then try connecting to mongodb at the default localhost port 
        self.client = MongoClient(SERVER_IP, port) if client is None else client
        #create collection to store cached webpages,
        # which is the equivalent of a table in a relational database
        self.db = self.client.wx

    def enqueue_data(self, msg_id, biz, msg):
        try:
            self.db.msg.insert({'_id': msg_id, 'biz': biz, 'msg': msg})
        except Exception as e:
            print(e)

    def clear(self):
        self.db.wx.drop()