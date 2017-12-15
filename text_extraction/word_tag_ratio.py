# -*- coding: utf-8 -*-
import gzip
import re

import urllib2

from StringIO import StringIO
from lxml.html import clean
import pylab
from sklearn.cluster import KMeans
import numpy as np

request_headers = {
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6",
    'accept-charset ': 'utf-8'
}

url = 'http://bbs.qyer.com/thread-2571140-1.html'
# url = 'http://news.sina.com.cn/c/gat/2017-03-13/doc-ifychhuq4322931.shtml'
# url = 'http://www.mafengwo.cn/i/6161801.html'

filename = re.findall('/([^/]+)$', url)[0]

try:
    f = open(filename, 'rb')
    content = f.read()
    f.close()
except Exception:
    req = urllib2.Request(url, headers=request_headers)
    response = urllib2.urlopen(req)
    if response.info().get('Content-Encoding') == 'gzip':
        buf = StringIO(response.read())
        fzip = gzip.GzipFile(fileobj=buf)
        content = fzip.read()
    else:
        content = response.read()

    f = open(filename, 'wb+')
    f.write(content)
    f.close()

# remove all javascript and css
cleaner = clean.Cleaner(style=True, scripts=True, comments=True, javascript=True, page_structure=False, safe_attrs_only=False)
content = cleaner.clean_html(content.decode('utf-8')).encode('utf-8')

# text only re
reg = re.compile("<[^>]*>")

lines = content.split('\n')
cleaned_lines = []
counts = []
tags = []
ratios = []

for line in lines:
    # get tags count
    tag = len(re.findall("<[^>]*>", line))
    # get text from a html line
    line = reg.sub('', line)
    cleaned_lines.append(line)
    if tag == 0:
        tag = 1
    counts.append(len(line))
    tags.append(tag)
    ratios.append(len(line)/tag)


# f = open('cleaned.txt', 'wb+')
# f.write(content)
# f.close()

# smooth the ratio, get average ratio of near 5 lines
# 对最近的5个取平均值，以排除噪声
r = 2
ratio_smoth = [0,0]
for k in range( r, len(ratios) - r ):
    ratio_smoth.append(sum(ratios[k-r:k+r+1])/(2*r+1))

# 转化为 二维的数组
# reshape 讲一个数组改变为任意 m * n 维度 的数组
# m 为 -1 的时候，数组的数量由总数和每个数组的元素来确定
feature = np.array(ratio_smoth).reshape(-1,1)

result_list = []

# 得到均值与均方差
mean = np.mean(ratio_smoth)
std = np.std(ratio_smoth)

print mean
print std


for k in range(1,4):

    # 聚合，预测每个元素所处的聚类，设置k = 2
    kmeans = KMeans(k).fit(feature)
    labels = kmeans.predict(feature)

    # 找出聚合中心点
    centers = kmeans.cluster_centers_

    print centers

    # 根据聚类的结果来分类
    clusters = {}
    n = 0
    for item in labels:
        if item in clusters:
            clusters[item].append(n)
        else:
            clusters[item] = [n]
        n +=1

    index = 0
    for i in centers:
        if i[0] > std:
            result_list += clusters[index]
        index += 1

result_set = sorted(set(result_list))

f = open('test.txt', 'wb+')
index = 0

print result_set

# 将大于标准差的一类识别为正文，进行输出
for i in result_set:
    f.write(cleaned_lines[i])

f.close()

# pylab.plot(ratios, 'g-', linewidth=1.0)
# # pylab.plot(counts, 'r-', linewidth=1.0)
# pylab.savefig('word_count.png')
# pylab.show()