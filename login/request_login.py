import requests

url = "http://localhost/xiaoxiang/login.php"

payload = "name=caca&password=c"
headers = {
    'connection': "keep-alive",
    'content-length': "20",
    'cache-control': "no-cache",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    'referer': "http://jc.lo/dev/login/login.php",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6",
    'cookie': "PHPSESSID=3lmb913ueivn9tp5f0l6ma4fu2",
    'postman-token': "37902aaa-c33e-b963-5240-13aadd2eb405"
    }

response = requests.request("POST", url, data=payload, headers=headers)

print(response.text)