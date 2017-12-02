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

    logger.write('request post data 1\r\n')

    // post the data
    post_req.write(post_data);

    logger.write('request post data 2\r\n')
    post_req.end();
}

module.exports = {
    summary: 'a rule to modify response',
    * beforeSendResponse(requestDetail, responseDetail) {

        if (/mp\/profile_ext\?action=home/i.test(requestDetail.url)) {
            logger.write('matched: ' + requestDetail.url + '\r\n');
            if (responseDetail.response.toString() !== "") {
                return new Promise(function (resolve, reject) {
                    try { //防止报错退出程序
                        var post_data = JSON.stringify({
                            'url': requestDetail.url,
                            'body': responseDetail.response.body.toString()
                        });
                        logger.write("post data to server -- home\r\n");
                        postData(post_data, 'historyhome', function (chunk) {
                            logger.write('response is ' + chunk + '\r\n');
                            logger.write('hack response!\r\n')
                            if(chunk == "NULL"){
                                logger.write('resolve 0\r\n')
                                resolve({
                                    response: responseDetail.response
                                })
                            } else {
                                const newResponse = responseDetail.response;
                                hack_string = "<script>setTimeout(function(){window.location.href='" + chunk + "';},2000);</script>";
                                newResponse.body += hack_string;
                                newResponse.statusCode = 200
                                logger.write('resolve 1\r\n')
                                resolve({
                                    response: newResponse
                                })
                            }
                        });
                        logger.write("post data to server -- home done\r\n");
                    } catch (e) {
                        logger.write('Error' + e);
                    }
                });
            }
        } else if (/mp\/profile_ext\?action=getmsg/i.test(requestDetail.url)) {
            logger.write('matched: ' + requestDetail.url + '\r\n');
            if (responseDetail.response.toString() !== "") {
                logger.write(responseDetail.response.body.toString());
                var post_data = JSON.stringify({
                    'url': requestDetail.url,
                    'body': responseDetail.response.body.toString()
                });
                logger.write("post data to server -- ext");
                postData(post_data, 'msgext', function (chunk) {

                });
            }
        }
    },
};