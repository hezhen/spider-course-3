# -*- coding: utf-8 -*-
#
import urllib2
import json

base_url = 'http://localhost:9200'

data = {
    "query": {
        "term":{"content":"塞舌尔"}
    },
    "from": 0,
    "size": 10,
    "sort":{ "_score": "desc"}
}


match_data = {
    "query": {
        "match":{"content":"塞舌尔 自驾"}
    },
    "from": 0,
    "size": 10,
    "sort":{ "_score": "desc"}
}


req = urllib2.Request(base_url + '/html/_search?pretty', data=json.dumps(data))
response = urllib2.urlopen(req)
print response.read()