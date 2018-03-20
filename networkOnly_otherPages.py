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
import networkOnly as networkOnly
import config as conf

def Main():
    cache = redis.StrictRedis(conf.redis['server'], conf.redis['port'])
    ses = ref.Login()
    p = pool.Pool(10)
    while(1):

        # when blocked before got element,
        # the return value will be a tuple.
        page = cache.brpop('wait',)
        if type(page) == tuple:
            page = page[1]
        page = eval(page)

        p.spawn(networkOnly.CrawlPage, ses, page['threadid'], page['pageNum'])

if __name__ == '__main__':
    Main()




