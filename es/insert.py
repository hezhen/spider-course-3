# -*- coding: utf-8 -*-
#
import urllib2

from goose import Goose
from goose.text import StopWordsChinese
import json

from HtmlRetrival import HtmlRetrival

g = Goose({'stopwords_class': StopWordsChinese})

url = 'http://bbs.qyer.com/thread-2571140-1.html'

html_retrieval = HtmlRetrival(url)
content = html_retrieval.get_content()

article = g.extract(raw_html=content)

base_url = 'http://localhost:9200'

data = {
    'title':article.title.encode('utf-8'),
    'content':article.cleaned_text.encode('utf-8')
}

req = urllib2.Request(base_url + '/html/travel/', data=json.dumps(data))
response = urllib2.urlopen(req)
print response.read()

