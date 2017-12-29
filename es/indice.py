# -*- coding: utf-8 -*-
#
import urllib2
import json

base_url = 'http://localhost:9200'

data = {
    "mappings":{
        "travel":{
            "properties":{
                "title":{
                    "type":"string",
                    "analyzer": "ik_smart"
                },
                "content": {
                    "type":"string",
                    "analyzer": "ik_smart"
                }
            }
        }
    }
}

opener = urllib2.build_opener(urllib2.HTTPHandler)
req = urllib2.Request(base_url + '/html?pretty', data=json.dumps(data))
req.get_method= lambda: 'PUT'
print opener.open(req)