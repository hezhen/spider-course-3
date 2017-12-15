import urllib
import urllib2

url = "http://jc.lo/dev/login/homepage.php"

headers = {
    'host': "jc.lo",
    'connection': "keep-alive",
    'content-length': "20",
    'cache-control': "no-cache",
    'origin': "http://jc.lo",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'referer': "http://jc.lo/dev/login/homepage.php",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6"
}

data = {'name':'caca', "password":'c'}
payload = urllib.urlencode(data)
print payload

request = urllib2.Request(url, payload, headers=headers)
response = urllib2.urlopen(request)
print response.info().items()
print response.read()

# response = requests.request("POST", url, data=payload, headers=headers)

