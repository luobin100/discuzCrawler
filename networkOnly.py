#coding:utf-8
import sys, os

import gevent
from gevent import monkey, pool; monkey.patch_all()

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

def Main():

    # 从第一页开始爬
    pageNum = 1

    ses = ref.Login()
    p = pool.Pool(20)
    jobs = [p.spawn(CrawlPage, ses, threadid, pageNum) for threadid in range(conf.tid_range['start'],conf.tid_range['end'],conf.tid_range['step'])]
    gevent.joinall(jobs, 60)
    # CrawlPage(ses, 1876842, pageNum)


def CrawlPage(ses, threadid, pageNum):
    ref.FramePrint('tid %d page %d  start at: %s' %
                   (threadid, pageNum, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    cache = redis.StrictRedis(conf.redis['server'], conf.redis['port'])

    try:
        tsoup = Browser(ses, threadid, pageNum)
    except:
        # 出错将该页push 到 error队列
        key = 'error'
        value = {'threadid': threadid,
                 'pageNum': pageNum}
        cache.lpush(key, value)
        ref.FramePrint('this tid %d error! page %d' % (threadid, pageNum))
        traceback.print_exc()
    else:
        # 成功完成将该页push到page列表等待后续的parseHtml等工序
        key = 'page'
        value = {'threadid': threadid,
                 'pageNum': pageNum,
                 'tsoup': tsoup}
        cache.lpush(key, value)

        ref.FramePrint('tid %d page %d  end at: %s'
                   % (threadid,
                    pageNum,
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    del cache



def Browser(ses, threadid, pageNum):

    link = 'https://www.hi-pda.com/forum/viewthread.php?tid=%s&page=%s' % (str(threadid),str(pageNum))

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    resp = ses.get(link, headers=headers)
    tsoup = resp.content

    del resp

    return tsoup


if __name__ == '__main__':
    Main()
