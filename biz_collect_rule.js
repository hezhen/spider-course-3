var logMap = {}
var fs = require('fs');
var logger = fs.createWriteStream('/Users/hezhen/Sites/dev/wechat/urlLog.log', {
    flags: 'a' // 'a' means appending (old data will be preserved)
})

function logPageFile(url) {
    if (!logMap[url]) {
        logMap[url] = true;
        logger.write(url + '\r\n');
    }
}

function postData(post_data, path, cb) {
    // // Build the post string from an object
    // var post_data = JSON.stringify({
    //     'data': data
    // });

    // An object of options to indicate where to post to
    var post_options = {
        host: 'localhost',
        port: '9999',
        path: '/' + path,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(post_data)
        }
    };

    var http = require('http');
    // Set up the request
    var post_req = http.request(post_options, function (res) {
        res.setEncoding('utf8');
        res.on('data', cb);
    });

    // post the data
    post_req.write(post_data);
    post_req.end();
}

module.exports = {
    summary: 'a rule to modify response',
    * beforeSendResponse(requestDetail, responseDetail) {

        if (/mp.weixin.qq.com/i.test(requestDetail.url)) {
            try { //防止报错退出程序
                logger.write('report url' + requestDetail.url + '\r\n');
                var post_data = JSON.stringify({
                    'url': requestDetail.url
                });
                postData(post_data, 'url', function (chunk) {
                    logger.write("return from server\r\n")
                });
            } catch (e) {
                logger.write('Error' + e + '\r\n');
            }

        }
    },
};