#!/usr/bin/env python3
"""Example for aiohttp.web basic server
"""

import asyncio
import re
import textwrap

import threading

import time

from mysqlmgr import MysqlMgr
from mongomgr import MongoManager
from subprocess import call

from aiohttp.web import Application, Response, StreamResponse, run_app
import json

mysql_mgr = MysqlMgr(10)
mongo_mgr = MongoManager()

biz_arr = mysql_mgr.all_biz()

if biz_arr is not None:
    bizs = set(biz_arr)
else:
    bizs = set([])

STATE_RUNNING = 1

STATE_IN_TRANSACTION = 2

running_state = 0

run_swipe = True

last_history_time = time.clock()

# A thread to save data to database in background
def insert_to_database(biz, msglist):
    try:
        for msg in msglist:
            print(biz)
            print(msg['comm_msg_info']['id'])
            mongo_mgr.enqueue_data(msg['comm_msg_info']['id'], biz, msg )
    except Exception as e:
        print(e)

def save_data(biz, msglist_str):
    save_thread = threading.Thread(target=insert_to_database, args=(biz, msglist_str,))
    save_thread.setDaemon(True)
    save_thread.start()

def swipe_for_next_page():
    while run_swipe:
        time.sleep(5)
        if time.clock() - last_history_time > 120:
            if running_state == STATE_RUNNING:
                reenter()
            continue
        call(["adb", "shell", "input", "swipe", "400", "1000", "400", "200"])

def reenter():
    global running_state
    running_state = STATE_IN_TRANSACTION
    # 模拟侧滑实现返回上一页
    call(["adb", "shell", "input", "swipe", "0", "400", "400", "400"])
    time.sleep(2)
    # 点击"进入历史消息"，每个手机的位置不一样，需要单独设置 X  和 Y
    call(["adb", "shell", "input", "tap", "200", "1200"])
    time.sleep(2)

async def report_msg_home(request):
    resp = StreamResponse()
    data = await request.json()
    global running_state
    global last_history_time
    print("report_msg_home: " + data['url'])
    # print(data['body'])
    last_history_time = time.clock()
    msglist_str = re.findall('var msgList = \'(\{.*?\})\'\;', data['body'])
    if len(msglist_str) > 0:
        msglist_str = msglist_str[0]
        msglist_str = msglist_str.replace('&quot;','"').replace('\\', '')

        biz_arr = re.findall('__biz=(.*?)\&', data['url'])
        if len(biz_arr) > 0:
            biz = biz_arr[0]
        else:
            biz = ''

        msglist = json.loads(msglist_str)
        save_data(biz, msglist['list'])

    resp.content_type = 'text/plain'
    await resp.prepare(request)
    if running_state == STATE_IN_TRANSACTION:
        # inject javascript code so that it redirects to a new Wechat Account Home
        running_state = STATE_RUNNING
        resp.write(("https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=" + bizs.pop() + "&scene=124#wechat_redirect").encode('utf8'))
    else:
        resp.write("NULL".encode('utf8'))
    await resp.write_eof()
    return resp

async def report_msg_ext(request):
    resp = StreamResponse()
    data = await request.json()
    global last_history_time
    print("report_msg_ext called")
    msg_data = json.loads(data['body'])
    msglist_str = msg_data['general_msg_list'].replace('\\', '')
    biz_arr = re.findall('__biz=(.*?)\&', data['url'])
    if len(biz_arr) > 0:
        biz = biz_arr[0]
    else:
        biz = ''
    msglist = json.loads(msglist_str)
    save_data(biz, msglist['list'])

    last_history_time = time.clock()
    resp.content_type = 'text/plain'
    await resp.prepare(request)
    await resp.write_eof()
    return resp

async def report_url(request):
    resp = StreamResponse()
    data = await request.json()
    url = data['url']
    # print("url reported: " + url)
    biz = re.findall('__biz=(.*?)\&', url)
    if len(biz) == 0:
        await resp.prepare(request)
        return resp
    biz = biz[0]
    print('----------------\r\n'+ biz + '\r\n----------------\r\n')
    mysql_mgr.enqueue_biz(biz, '')
    bizs.add(biz)
    biz = biz.encode('utf8')
    resp.content_type = 'text/plain'
    await resp.prepare(request)
    resp.write(biz)
    await resp.write_eof()
    return resp


async def intro(request):
    txt = textwrap.dedent("""\
        Type {url}/hello/John  {url}/simple or {url}/change_body
        in browser url bar
    """).format(url='127.0.0.1:8080')
    binary = txt.encode('utf8')
    resp = StreamResponse()
    resp.content_length = len(binary)
    resp.content_type = 'text/plain'
    await resp.prepare(request)
    resp.write(binary)
    return resp

async def simple(request):
    return Response(text="Simple answer")

async def change_body(request):
    resp = Response()
    resp.body = b"Body changed"
    resp.content_type = 'text/plain'
    return resp

async def init(loop):
    app = Application()
    app.router.add_get('/', intro)
    app.router.add_post('/url', report_url)
    app.router.add_post('/historyhome', report_msg_home)
    app.router.add_post('/msgext', report_msg_ext)
    return app

def start_swipe_thread():
    try:
        t = threading.Thread(
            target=swipe_for_next_page, name='swipe')
        # set daemon so main thread can exit when receives ctrl-c
        t.setDaemon(True)
        t.start()
    except Exception:
        print("Error: unable to start thread")

# start_swipe_thread()
loop = asyncio.get_event_loop()
app = loop.run_until_complete(init(loop))
run_app(app, host='127.0.0.1', port=9999)