# -*- coding: utf-8 -*-
"""
示例词库,执行`开头的表达式,调用eval函数的返回值
出现错误请联系dgl0518@gmail.com
欢迎进QQ群讨论172965579
"""
__author__ = "认的你"
from baseclass import BaseDict
from math import *
base = BaseDict()

class RunEval(BaseDict):
    """
    命令: `<表达式> (`是键盘1左边的那个键) --认的你
        `100*100
        `[for i in range(10)] 
"""

    @base.mydecorator
    def keyIn(self,content):
        """
        content 是一个列表,如果接收到的是群信息那么
        [ 'group_message',      群的uin ,   用户发送的文本     ,     群qq]
        我们只需要处理 content[2]

        """
        a = content[2].strip()
        try:
            if a[0] == '`':
                script = a[1:]
                try:
                    txt = str(eval(script))
                except:
                    txt = u"运行出错"
                if content[0] == "group_message":
                    return '@' + str(content[-1]) + " : "+ txt
                else:
                    return txt
            else:
                return None
        except IndexError:
            return None

    def getinfo():
        return  """命令: `<表达式> (`是键盘1左边的那个键) --认的你
        `100*100
        `[for i in range(10)] 
"""
