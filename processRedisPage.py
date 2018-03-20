#coding:utf-8
import sys, os

from datetime import datetime
import time
import pymysql, gc, redis


from timeit import default_timer as timer


import gevent
from gevent import monkey, pool;

monkey.patch_all()

from bs4 import BeautifulSoup

import re

import pymysql.cursors
import redis
from datetime import datetime

import timeit
import requests
import gc
import traceback

# 导入当前文件夹下的refactor.py
sys.path.append(os.getcwd())
import refactor as ref
import config as conf

from multiprocessing import Process


def Main():
    for i in range(3):
        proc = Process(target=Crawl, args=())
        proc.start()
    # Crawl()


def Crawl():
    cache = redis.StrictRedis(conf.redis['server'], conf.redis['port'])

    while(1):

        # when blocked before got element,
        # the return value will be a tuple.
        page = cache.brpop('page')
        if type(page) == tuple:
            page = page[1]
        page = eval(page)

        threadid =page['threadid']
        pageNum = page['pageNum']

        try:
            str_html = page['tsoup'].decode('gb18030')   # 虽然html源文件里写的是gbk 但用gbk会出错，提示gbk不能decode

            tsoup = BeautifulSoup(str_html, 'lxml')

            threadData = ref.ParseHtml(tsoup, threadid, pageNum)

            if pageNum == 1:

                # if there are follow pages, push those pages to redis
                if threadData['pagesCount'] > 1:

                    key = 'wait'
                    value = {'threadid': threadid,
                             'pageNum': None}
                    for pageNum_OtherPage in range(2, threadData['pagesCount'] + 1):
                        value['pageNum'] = pageNum_OtherPage
                        cache.lpush(key, value)

                # only when first page, insert title table
                ref.AddThreadTitle(threadData['threadid'],
                               threadData['threadTitle'],
                               threadData['boardName'],
                               threadData['errormsg'])


            ref.AddThreadPost(threadData['postList'])

            del page, str_html, tsoup, threadData

        except:
            # 出错将该页push 到 error队列
            key = 'error'
            value = {'threadid': threadid,
                     'pageNum': pageNum}
            cache.lpush(key, value)
            ref.FramePrint('this tid %d error! page %d' % (threadid, pageNum))
            traceback.print_exc()
        else:
            # 成功完成将该页push到redis done列表去
            key = 'done'
            value = {'threadid': threadid,
                     'pageNum': pageNum}
            cache.lpush(key, value)
            ref.FramePrint('tid %d page %d done. %s' %
                           (threadid, pageNum, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


if __name__ == '__main__':
    Main()




