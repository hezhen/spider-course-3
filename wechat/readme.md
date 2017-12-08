# Install AnyProxy
### Install NodeJS first
Linux:       $ yum install nodejs 

Windows:  https://nodejs.org/dist/v9.0.0/node-v9.0.0-x86.msi

### Change NPM to use taobao repository
$ npm install -g cnpm --registry=https://registry.npm.taobao.org

### Install AnyPorxy
npm install -g anyproxy@beta

### Generate root certificate and trust it
anyproxy-ca

### Start AnyProxy ( -i means parse https )
Use --rule to specify rule defined by javascript
anyproxy -i --rule wxrule.js


# Files
-- wxrule.js 指定了抓取微信公众号的规则，用来上报HOME消息和更多的历史消息

-- biz_collect_rule.js 用来协助收集微信公众号的 __biz 

-- mysqlmgr.py MySQL数据库代码，需要修改数据库的地址、用户名和密码

-- mongomgr.py MongoDB 数据库代码，用来存储抓取的微信公众号历史消息

-- webservice.py 后台的web服务，基于 python3，可以通过 http://127.0.0.1:9999 来访问