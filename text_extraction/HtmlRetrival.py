import gzip
import re
import urllib2

from StringIO import StringIO

class HtmlRetrival:

    dir_name = 'files'

    def __init__(self, url):
        self.url = url

    def get_content(self):
        request_headers = {
            'connection': "keep-alive",
            'cache-control': "no-cache",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            'accept-language': "zh-CN,en-US;q=0.8,en;q=0.6",
            'accept-charset ': 'utf-8'
        }

        filename = self.dir_name + '/' + re.findall('/([^/]+)$', self.url)[0]

        try:
            f = open(filename, 'rb')
            content = f.read()
            f.close()
        except Exception:
            req = urllib2.Request(self.url, headers=request_headers)
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

        return content