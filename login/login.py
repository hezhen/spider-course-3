import urllib
import urllib2
import glob
import sqlite3
import os
import cookielib


url="http://localhost/xiaoxiang/login.php"

headers = {
    'host': "jc.lo",
    'connection': "keep-alive",
    'cache-control': "no-cache",
    'content-type': "application/x-www-form-urlencoded",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit" \
                  "/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6",
}

if __name__ == '__main__':
    data = {'name':'caca', "password":'c'}
    payload = urllib.urlencode(data)

    # use cookiejar
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    request = urllib2.Request(url, payload, headers=headers)
    response = opener.open(request)
    print response.info()
    print response.read()
    for cookie in cj:
        print cookie.name, cookie.value, cookie.domain