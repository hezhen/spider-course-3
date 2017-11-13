# spider-course-3

------------------------------------------------------------------------------------
# Install Phantomjs
------------------------------------------------------------------------------------
# Install NodeJS first
yum install nodejs

# change NPM to use taobao repository
$ npm install -g cnpm --registry=https://registry.npm.taobao.org

# Using Node's package manager install phantomjs: 
npm -g install phantomjs-prebuilt

# Install selenium (in your virtualenv, if you are using that)
pip install selenium

# add PhantomJS home to PATH
vim ~/.profile
PHANTOMJS_HOME=/path/to/phantomjs
PATH=PHANTOMJS_HOME/bin:$PATH

# After installation, you may use phantom as simple as:

from selenium import webdriver

driver = webdriver.PhantomJS() # or add to your PATH
driver.set_window_size(1024, 768) # optional
driver.get('https://google.com/')
driver.save_screenshot('screen.png') # save a screenshot to disk
sbtn = driver.find_element_by_css_selector('button.gbqfba')
sbtn.click()

If your system path environment variable isn't set correctly, you'll need to specify the exact path as an argument to webdriver.PhantomJS(). Replace this:

driver = webdriver.PhantomJS() # or add to your PATH
... with the following:

driver = webdriver.PhantomJS(executable_path='/usr/local/lib/node_modules/phantomjs/lib/phantom/bin/phantomjs')
References:

http://selenium-python.readthedocs.org/en/latest/api.html
How do I set a proxy for phantomjs/ghostdriver in python webdriver?
http://python.dzone.com/articles/python-testing-phantomjs

------------------------------------------------------------------------------------
# HBASE
------------------------------------------------------------------------------------

hbase download
http://mirror.bit.edu.cn/apache/hbase/1.3.0/hbase-1.3.0-bin.tar.gz

hadoop
http://mirror.bit.edu.cn/apache/hadoop/common/hadoop-2.7.3/hadoop-2.7.3.tar.gz

hbase thrift start

------------------------------------------------------------------------------------
# Install Bloom Filter
------------------------------------------------------------------------------------
git clone https://github.com/axiak/pybloomfiltermmap.git
python setup.py install

------------------------------------------------------------------------------------
# Install Murmurhash Bitarray lxml
------------------------------------------------------------------------------------
pip install murmurhash3 bitarray lxml