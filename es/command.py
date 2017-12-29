# -*- coding: utf-8 -*-
#
import urllib2
import json

base_url = 'http://localhost:9200'

query_url = base_url + '/htmlcontent/_search?pretty'
reindex_url = base_url + '/_reindex?pretty'

data = {
    "query": {
        "term":{"content":"塞舌尔"}
    },
    "from": 0,
    "size": 10
}

reindex = {
    "source":{
        "index":"html"
    },
    "dest":{
        "index":"htmlnew"
    }
}

req = urllib2.Request(reindex_url, data=json.dumps(reindex))
response = urllib2.urlopen(req)
print response.read()