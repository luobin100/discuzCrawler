#coding:utf-8

# 设置redis连接
redis = dict(
    server = '127.0.0.1',
    port = '6379'
)

# 设置mysql连接
mysql = dict(
    host = 'localhost',
    user = 'root',
    password = '123',
    db = 'HipdaScr'
)

# 设置论坛登陆的用户名密码
forum = dict(
    username = 'xxxxx',
    password = 'xxxxx'
)

# 设置需要抓取的tid（帖子ID）段。
tid_range = dict(
    start = 2282246,  # 开始tid
    end = 2205717,    # 结束tid (不包含本身)
    step = -1         # 每次递增的数值
)