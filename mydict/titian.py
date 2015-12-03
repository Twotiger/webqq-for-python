# -*- coding: utf-8 -*-
"""
一个示例词库,展示如何提问及提取答案.
出现错误请联系dgl0518@gmail.com
欢迎进QQ群讨论172965579
"""


import xml.dom.minidom
import random
from baseclass import BaseDict
base = BaseDict()

__author__ = "认的你"

"""I am Robot Titian"""
class Titian(BaseDict):

    def __init__(self):
        self.faq = self.openxml("mydict/base.xml")


    def openxml(self,xmlfile):
        """返回所有问题"""
        dom = xml.dom.minidom.parse(xmlfile)
        root = dom.documentElement
        faq = root.getElementsByTagName('faq')
        return faq


    def findq(self, word):
        """返回答案"""
        for i in self.faq:
            q = i.getElementsByTagName('q')
            for j in q:
                if j.firstChild.data == word:
                    a = i.getElementsByTagName('a')
                    return random.choice(a).firstChild.data
        else:
            return None


    @base.mydecorator
    def keyIn(self, content):
        
        # 传递的文字后面有空格
        try:
            print content
            ans = self.findq(content[2].strip())
        except Exception,e:
            return None
            #return 'error at titian %s'%e
        if ans :
            return ans
        else:
            return None
            
    def getinfo(self):
        return ''


if __name__ == "__main__":
    titian = Titian()
    print titian.keyIn(u'我有一个问题')
