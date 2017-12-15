import lxml
from lxml import html
import urllib2

def parse_form(html):
    """extract all input properties from the form
    """
    tree = lxml.html.fromstring(html)
    data = {}
    for e in tree.cssselect('form input'):
        if e.get('name'):
            data[e.get('name')] = e.get('value')
    return data

url = "http://jc.lo/dev/login/login.php"

headers = {
    'host': "jc.lo",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6",
    'postman-token': "dab3b5d5-2237-27e9-93bf-ad9ec0a451ac"
}

request = urllib2.Request(url, headers=headers)
response = urllib2.urlopen(request)
html = response.read()
data = parse_form(html)

print response.info().keys()