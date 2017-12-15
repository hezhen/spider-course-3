# -*- coding: utf-8 -*-

import re

from lxml import etree
from HtmlRetrival import HtmlRetrival
from lxml.html import clean
import pylab
import sys

# req = urllib2.Request('http://www.mafengwo.cn/i/750387.html')
# req = urllib2.Request('http://news.sina.com.cn/china/xlxw/2017-03-12/doc-ifychhuq4136971.shtml')
# req = urllib2.Request('http://bbs.qyer.com/thread-2703424-1.html')

# response = urllib2.urlopen(req)
# content = response.read()
#
# f = open('sina_ifych.html', 'wb+')
# f.write(content)
# f.close()

html_retrieval = HtmlRetrival('http://news.sina.com.cn/w/zx/2017-03-25/doc-ifycstww1059968.shtml')
content = html_retrieval.get_content()

#
# tr = etree.HTML(content)
#
# for bad in tr.xpath("//script"):
#     bad.getparent().remove(bad)
#
# for bad in tr.xpath("//style"):
#     bad.getparent().remove(bad)

cleaner = clean.Cleaner(style=True, scripts=True, comments=True, javascript=True, page_structure=False, safe_attrs_only=False)
content = cleaner.clean_html(content.decode('utf-8')).encode('utf-8')


reg = re.compile("<[^>]*>")
content = reg.sub('', content)

f = open('cleaned.txt', 'wb+')
f.write(content)
f.close()

lines = content.split('\n')
indexes = range(0, len(lines))
counts = []
for line in lines:
    counts.append(len(line))

pylab.plot(indexes, counts,linewidth=1.0)
pylab.savefig('word_count.png')
pylab.show()