# -*- coding: utf-8 -*-

import urllib2
import re
from HtmlRetrival import HtmlRetrival

from goose import Goose
from goose.text import StopWordsChinese
g = Goose({'stopwords_class': StopWordsChinese})

url = 'http://bbs.qyer.com/thread-2571140-1.html'

html_retrieval = HtmlRetrival(url)
content = html_retrieval.get_content()

article = g.extract(raw_html=content)

f = open('pythongoose.txt', 'wb+')
f.write(article.cleaned_text.encode('utf-8'))
f.close()