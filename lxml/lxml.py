import lxml
from lxml import html
from lxml import etree

from bs4 import BeautifulSoup

f = open('jd.com_2131674.html', 'r')
content = f.read()

tree = etree.HTML(content.decode('utf-8'))

print '--------------------------------------------'
print '# different quote //*[@class="p-price J-p-2131674"'
print '--------------------------------------------'
print tree.xpath(u"//*[@class='p-price J-p-2131674']")
print ''

print '--------------------------------------------'
print '# partial match ' + "//*[@class='J-p-2131674']"
print '--------------------------------------------'
print tree.xpath(u"//*[@class='J-p-2131674']")
print ''

print '--------------------------------------------'
print '# exactly match class string ' + '//*[@class="p-price J-p-2131674"]'
print '--------------------------------------------'
print tree.xpath(u'//*[@class="p-price J-p-2131674"]')
print ''

print '--------------------------------------------'
print '# use contain ' + "//*[contains(@class, 'J-p-2131674')]"
print '--------------------------------------------'
print tree.xpath(u"//*[contains(@class, 'J-p-2131674')]")
print ''


print '--------------------------------------------'
print '# specify tag name ' + "//strong[contains(@class, 'J-p-2131674')]"
print '--------------------------------------------'
print tree.xpath(u"//strong[contains(@class, 'J-p-2131674')]")
print ''

print '--------------------------------------------'
print '# css selector with tag' + "cssselect('strong.J-p-2131674')"
print '--------------------------------------------'
htree = lxml.html.fromstring(content)
print htree.cssselect('strong.J-p-2131674')
print ''

print '--------------------------------------------'
print '# css selector without tag, partial match' + "cssselect('.J-p-2131674')"
print '--------------------------------------------'
htree = lxml.html.fromstring(content)
elements = htree.cssselect('.J-p-2131674')
print elements
print ''

print '--------------------------------------------'
print '# attrib and text'
print '--------------------------------------------'
for element in tree.xpath(u"//strong[contains(@class, 'J-p-2131674')]"):
    print element.text
    print element.attrib
print ''

print '--------------------------------------------'
print '########## use BeautifulSoup ##############'
print '--------------------------------------------'
print '# loading content to BeautifulSoup'
soup = BeautifulSoup(content, 'html.parser')
print '# loaded, show result'
print soup.find(attrs={'class':'J-p-2131674'}).text

f.close()
