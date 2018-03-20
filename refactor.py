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
import config as conf

def AddThreadPost(postList):
    try:

        cnn = pymysql.connect(host= conf.mysql['host'],
                                     user= conf.mysql['user'],
                                     password= conf.mysql['password'],
                                     db= conf.mysql['db'],
                                     charset='utf8',
                                     cursorclass=pymysql.cursors.DictCursor)

        cur = cnn.cursor()

        # print("insert==========================")
        sql = """INSERT INTO TB_Posts(postid, tid, userId, userName,
               postsCount, points, accountCreatedDate,
               postDateTime, floorNum,
               postStatus, postMessage, locked)
                    VALUES (%s, %s, %s, %s,
               %s, %s, %s,
               %s, %s,
               %s, %s, %s)"""


        cur.executemany(sql, postList)
        cnn.commit()

        cur.close()
        cnn.close()
        del cur, cnn

    except (pymysql.Error) as e:
        print (e)
        print (e.args[1])
    except Exception, e:
        print (e)
        FramePrint('encountered error at AddThreadPost() tid %d' % (postList[0][1]))



def AddThreadTitle(tid, threadTitle, boardName, errormsg):
    try:

        cnn = pymysql.connect(host=conf.mysql['host'],
                              user=conf.mysql['user'],
                              password=conf.mysql['password'],
                              db=conf.mysql['db'],
                              charset='utf8',
                              cursorclass=pymysql.cursors.DictCursor)

        cur = cnn.cursor()

        # print("insert==========================")
        sql = """INSERT INTO TB_Titles(tid, title, board, errormsg)
                    VALUES (%s, %s, %s, %s)"""
        cur.execute(sql, (tid, threadTitle, boardName, errormsg))
        cnn.commit()

        cur.close()
        cnn.close()
        del cur, cnn


    except (pymysql.Error) as e:
        print(e)
        print(e.args[1])
    except Exception, e:
        print(e)
        FramePrint('encountered error at AddThreadTitle() tid %d' % tid)



def ParseHtml(tsoup, threadid, pageNum):

    # the return value
    threadData = {}

    if pageNum == 1:

        # detect if this thread id is valid.
        div_nav = tsoup.find("div", {"id": "nav"})
        if div_nav.text == u'Hi!PDA » 提示信息':
            div_alert_error = tsoup.find("div", {"class" : "alert_error"})
            if div_alert_error is not None:
                errormsg = div_alert_error.find("p").text
                threadData = {
                    'threadid': threadid,
                    'threadTitle': None,
                    'boardName': None,
                    'errormsg': errormsg,
                    'pagesCount': None,
                    'postList': None
                }
                return threadData

        # get thread title and board name.
        threadTitle = div_nav.contents[4].replace(u" » ", "")
        boardName = div_nav.contents[3].text

        # get pages count
        div_forumcontrol = tsoup.find("div", {"class", "forumcontrol"})
        div_page = div_forumcontrol.find("div", {"class", "pages"})

        if div_page is not None:
            pagesCount = len(div_page.contents) - 1
        else:
            pagesCount = 1

    divs_post = tsoup.find("div",{"id" : "postlist"}).findAll("div", {"id" : re.compile('post_[0-9]{8}')})

    postList = []

    for div_post in divs_post:

        # get post id
        postid = div_post.attrs["id"].replace("post_", "")

        # get user info
        userName = div_post.find("td", {"class", "postauthor"}) \
                    .find("div", {"class", "postinfo"}) \
                    .find("a").text


        dds_userinfo = div_post.find("td", {"class", "postauthor"}) \
                        .find("dl", {"class", "profile s_clear"}) \
                        .findAll("dd")

        userId = dds_userinfo[0].text.rstrip()
        postsCount = dds_userinfo[1].text.rstrip()
        points = dds_userinfo[2].text.rstrip()
        accountCreatedDate  = dds_userinfo[3].text.rstrip()


        # get post content
        td_postcontent = div_post.find("td", {"class", "postcontent"})

        postDateTime = td_postcontent.find("div", {"class", "authorinfo"}) \
                      .find("em").text.replace(u"发表于 ", "")

        floorNum = td_postcontent.find("div", {"class", "postinfo"}) \
                   .find("em").text


        div_postMessage = td_postcontent.find("div", {"class", "postmessage"})

        # is this user be locked
        div_locked = div_postMessage.find("div", {"class", "locked"})
        if div_locked is not None:
            locked = u"提示: 作者被禁止或删除 内容自动屏蔽"
            postStatus = None
            postMessage = None
        else:
            locked = None

            td_msgfont = div_postMessage.find("td", {"class", "t_msgfont"})

            # is this post be edited
            i_postStatus = td_msgfont.find("i", {"class", "pstatus"})
            if i_postStatus is not None:
                postStatus = i_postStatus.text

                # remove postStatus
                # cause i need the pure post message
                i_postStatus.extract()
            else:
                postStatus = None

            # get text of post message
            postMessage = td_msgfont.text

            # get images of post message
            imgs = td_msgfont.findAll('img')
            if len(imgs) > 0:
                for img in imgs:
                    # 有onmouseover属性的才是真实的论坛用户上传图片
                    if img.has_attr('onmouseover'):
                        if img.attrs['onmouseover'] == "showMenu({'ctrlid':this.id,'pos':'12'})":
                            if img.has_attr('onclick'):
                                # 老的帖子和新点的帖子图片的结构不同，现在知道有下面这两种。
                                if img.attrs['onclick'] == 'zoom(this, this.src)':
                                    imgLink = "<img src='%s'>" % img.attrs['file']
                                else:
                                    imgLink = "<img src='%s'>" % img.attrs['onclick'].replace("zoom(this, '","").replace("')", "")
                            else:
                                imgLink = "<img src='%s'>" % img.attrs['file'] # 当是小图片（不需要缩放就能全部显示出来的情况）
                        postMessage = postMessage + imgLink + '<br> \n'

        # append a post
        postList.append([postid, threadid, userId, userName,
               postsCount, points, accountCreatedDate,
               postDateTime, floorNum,
               postStatus, postMessage, locked])

    if pageNum == 1:
        threadData = {
            'threadid': threadid,
            'threadTitle': threadTitle,
            'boardName': boardName,
            'errormsg': None,
            'pagesCount': pagesCount,
            'postList': postList
        }
    else:
        threadData = {
            'threadid': threadid,
            'threadTitle': None,
            'boardName': None,
            'errormsg': None,
            'pagesCount': None,
            'postList': postList
        }

    return threadData




def FramePrint(message):
    print('''
/////////////////////////////////
%s
/////////////////////////////////
''' % message)


def Browser(ses, threadid, pageNum):
    FramePrint('tid %d page %d  start at: %s' %
                   (threadid, pageNum, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    link = 'https://www.hi-pda.com/forum/viewthread.php?tid=%s&page=%s' % (str(threadid),str(pageNum))

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br'
    }

    resp = ses.get(link, headers=headers)

    tsoup = BeautifulSoup(resp.content, "lxml")
    del resp

    FramePrint('tid %d page %d  end at: %s'
               % (threadid,
                pageNum,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    return tsoup


def Login():

    login_url = 'https://www.hi-pda.com/forum/logging.php?action=login&loginsubmit=yes'

    payload = {
            "answer":"",
            "password":conf.forum['password'],#这里填密码
            "questionid":"0",
            "referer":"https://www.hi-pda.com/forum/forumdisplay.php?fid=2",
            "username":conf.forum['username'],#这里填登录名
            }

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Connection': 'keep-alive',
        'User-Agent': "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0",
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br'
    }
    ses = requests.Session()

    ses.post(login_url, headers=headers, data=payload)

    return ses

