# -*- coding: utf-8 -*-
#    > File Name: main.py
#    > Author: Twotiger
#    > Mail: dgl0518@gmail.com
#    > Created Time: 2015/11/2 19:17:06

import os
import gevent
from gevent.wsgi import WSGIServer
import smartqq
from mydict.titian import Titian
from mydict.getweather import Weather


titian = Titian()
weather = Weather()



def producer():
    # 返回数据及headers
    if os.path.exists('image.jpg'):
        data_source = 'runing...'
        headers =[
        ('Content-Type', 'text/xml')
        ]
        return [data_source, headers]
    else:
        qq = smartqq.Smartqq()
        qq.installdic([titian, weather])
        y = qq.downloadjpg()
        data_source = y
        gevent.spawn(qq.run)
        headers = [
        ('Content-Type', 'image/jpeg')
        ]
        return [data_source, headers]


def ajax_endpoint(environ, start_response):
    # 主函数
    data_source, headers = producer()
    print environ
    print  'start_response=', start_response
    status = '200 OK'
    #  yield data_source.get(timeout=5)
    start_response(status, headers)
    try:
        datum = data_source
    except:
        return 'Empty'
    return datum


WSGIServer(('', 8000), ajax_endpoint).serve_forever()
