# -*- coding: utf-8 -*-

from HtmlRetrival import HtmlRetrival
from lxml import etree

html_re = HtmlRetrival('http://bbs.qyer.com/thread-2631045-1.html')
content = html_re.get_content()

# 定义正文的tag
tags = {
    'title': '//h3[@class="b_tle"]',
    'content': '//td[@class="editor bbsDetailContainer"]//*[self::p or self::span or self::h1]'
}

tr = etree.HTML(content)
info = {}

f = open('template.txt', 'wb')

for tag in tags:
    info[tag] = []
    f.write('\r\n\r\n' + tag + '\r\n\r\n')
    eles = tr.xpath(tags[tag])
    for ele in eles:
        if ele is None or ele.text is None:
            continue
        info[tag].append(ele.text)
        f.write(ele.text.encode('utf-8') + '\r\n')

f.close()