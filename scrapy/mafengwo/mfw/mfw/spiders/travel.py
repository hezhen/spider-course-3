# -*- coding: utf-8 -*-
import scrapy

from lxml import html
from lxml import etree

import re

from scrapy.selector import Selector

class TravelSpider(scrapy.Spider):
    name = "travel"
    allowed_domains = ["www.mafengwo.cn"]
    start_urls = ['http://www.mafengwo.cn/']

    def parse(self, response):
        # title = Selector(response=response).xpath('//head/title').extract_first()

        content = response.body
        tree = etree.HTML(content.decode('utf-8'))
        title = tree.xpath('//head/title')[0].text

        print title

        if len(re.findall('\/i\/\d{5,8}.html', response.url)) > 0:
            print '--------------------------------------------------'
            print 'It\'s a travel note !!!!'
            print '--------------------------------------------------'
            print ''

            yield {
                'title': title,
                'url': response.url
            }

            print ''
            print ''

        for url in response.css('a::attr(href)'):
            yield response.follow(url, callback=self.parse)