# -*- coding: utf8-*-
# -*- Author: twotiger
# -*- Created time: 2015-11-25 15:07:28

import re
import os
import json
import urllib
import urllib2
import logging
import cookielib
from time import time, sleep
from random import random, randint
from time import time, sleep
from sendemail import sendemail

# 如果提示ssl证书出错,就取消注释
#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='./log/%s.log'%str(time()),
                filemode='w')

#################################################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s  %(levelname)-8s[line:%(lineno)d] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#################################################################################################

class Smartqq():
    """
    主类
    """
    def __init__(self, dics=[]):
        self.__salt = ''
        self.msgId= randint(10000000,44444444)
        self.status= 'online'
        self.action = 47
        self.ptwebqq = ''
        self.vfwebqq = ''
        self.uid = 0
        self.dics = dics
        self.psessionid = ''
        self.friendsInfo = {}
        self.groupInfo = {}
        self.cookie = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(self.opener)


    def get_cookie_by_name(self, cj, name):
        # 查找 cookie.value 不采用
        return [cookie for cookie in cj if cookie.name == name][0]

    def get_cookie_value(self, name):
        # 查找 cookie.value
        return [cookie for cookie in self.cookie if cookie.name == name][0]

    def getaction(self):
        """
        downloadjpg 在使用
        """
        self.action += 2000
        return self.action


    def downloadjpg(self):
        """下载图片, 用手机扫描
        """
        logging.debug(u'REQUEST & DOWNLOAD  image')
        url = "https://ssl.ptlogin2.qq.com/ptqrshow?appid=501004106&e=0&l=M&s=5&d=72&v=4&t={0}".format(random())
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'ssl.ptlogin2.qq.com'
                }
        request = urllib2.Request(url=url, headers=headers)
        resule = self.opener.open(request)
        jpg = resule.read()
        image = open('image.jpg','wb')
        image.write(jpg)
        #  logging.debug(self.cookie)
        return jpg


    def requestptlogin2qqcom(self):
        """一直请求,看看有没有登录好"""
        while self.action < 48099:
            logging.debug(u'REQUEST ssl.ptlogin2.qq.com/ptqrlogin')
            url = "https://ssl.ptlogin2.qq.com/ptqrlogin?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-0-{0}&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10141&login_sig=&pt_randsalt=0".format(self.getaction())
            headers= {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'ssl.ptlogin2.qq.com'
                    }
            request = urllib2.Request(url=url, headers=headers)
            resule = self.opener.open(request)
            html = resule.read()

            if '登录成功' in html:
                logging.info(html)
                tmp =  re.findall(r"'(.*?)'", html)
                request = urllib2.Request(url=tmp[2])
                self.opener.open(request)           #  此处返回大量cookie
                self.ptwebqq = self.get_cookie_value("ptwebqq").value
                logging.info(self.ptwebqq)
                break
            logging.debug(html)
            sleep(2)

        else:
            # 登录失败
            exit()

    def requestweb2qq(self):
        """
        得到 vfwebqq
        """
        logging.debug(u'REQUEST web2.qq.com')
        url = "http://s.web2.qq.com/api/getvfwebqq?ptwebqq={0}&clientid=53999199&psessionid=&t={1}".format(self.ptwebqq, int(time()*1000))
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'s.web2.qq.com',
                    'Referer':'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1' # 等待检测
                }
        request = urllib2.Request(url=url, headers=headers)
        result = self.opener.open(request)
        html = result.read()
        jsonData = json.loads(html)
        self.vfwebqq = jsonData['result']['vfwebqq']
        logging.debug(self.vfwebqq)

    def requestdweb2qq(self):
        """
        """
        logging.debug(u'REQUEST d.web2qq.com')
        url = "http://d.web2.qq.com/channel/login2"
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'d.web2.qq.com',
                    'Origin':'http://d.web2.qq.com',
                    'Referer':'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2' # 等待检测
                }
        data = {'ptwebqq':self.ptwebqq,
                'clientid':53999199,
                'psessionid':'',
                'status': self.status
        }
        postdata = urllib.urlencode({'r':json.dumps(data)})
        request = urllib2.Request(url=url, data=postdata, headers=headers)
        html = self.opener.open(request).read()
        jsonData = json.loads(html)

        self.psessionid = jsonData['result']['psessionid']
        self.uid = jsonData['result']['uin']

        logging.info('**********Success**********')


    def gethash(self, uin, ptwebqq):
        uin += ""
        N=[0,0,0,0]
        for T in range(len(ptwebqq)):
            N[T%4]=N[T%4]^ord(ptwebqq[T])

        U=["EC","OK"]
        V=[0, 0, 0, 0]
        V[0]=int(uin) >> 24 & 255 ^ ord(U[0][0])
        V[1]=int(uin) >> 16 & 255 ^ ord(U[0][1])
        V[2]=int(uin) >>  8 & 255 ^ ord(U[1][0])
        V[3]=int(uin)       & 255 ^ ord(U[1][1])

        U=[0,0,0,0,0,0,0,0]
        U[0]=N[0];
        U[1]=V[0];
        U[2]=N[1];
        U[3]=V[1];
        U[4]=N[2];
        U[5]=V[2];
        U[6]=N[3];
        U[7]=V[3];

        N=["0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F"];
        V="";
        for T in range(len(U)):
            V+= N[ U[T]>>4 & 15]
            V+= N[ U[T]    & 15]

        return V

    def get_user_friends2(self):
        """
        用户好友信息
        """
        url = 'http://s.web2.qq.com/api/get_user_friends2'
        data = {'vfwebqq': self.vfwebqq, 'hash':self.gethash(str(self.uid), self.ptwebqq)}
        postdata = urllib.urlencode({'r':json.dumps(data)})
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'s.web2.qq.com',
                    'Origin':'http://s.web2.qq.com',
                    'Referer':'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1' # 等待检测
                }

        request = urllib2.Request(url, postdata, headers)
        html = self.opener.open(request).read()
        jsonData = json.loads(html)
        try:
            for dic in jsonData['result']['info']:
                self.friendsInfo[dic['uin']] = dic['nick']

            logging.debug('{0}'.format(self.friendsInfo))
        except Exception,e:
            logging.warning('{0}'.format(e))

    def get_group_name(self):
        """
        用户群信息
        """
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        data = {'vfwebqq': self.vfwebqq, 'hash':self.gethash(str(self.uid), self.ptwebqq)}
        postdata = urllib.urlencode({'r':json.dumps(data)})
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'s.web2.qq.com',
                    'Origin':'http://s.web2.qq.com',
                    'Referer':'http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1' # 等待检测
                }

        request = urllib2.Request(url, postdata, headers)
        html = self.opener.open(request).read()
        jsonData = json.loads(html)
        try:
            for info in jsonData['result']['gnamelist']:
                self.groupInfo[info['gid']] = info['name']
            logging.debug('{0}'.format(self.groupInfo))
        except Exception,e:
            logging.warning('{0}'.format(e))

    def get_self_info(self):
        #得到自己的信息
        url = 'http://s.web2.qq.com/api/get_self_info2?t={0}'.format(int(time()*1000))


    def installdic(self, arg):
        self.dics = arg

    def poll2(self):
        url = 'http://d.web2.qq.com/channel/poll2'
        data = {"ptwebqq":self.ptwebqq,"clientid":53999199,"psessionid":self.psessionid,"key":""}
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'d.web2.qq.com',
                    'Origin':'http://d.web2.qq.com',
                    'Referer':'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2' # 等待检测
                }
        postdata = urllib.urlencode({'r':json.dumps(data)})

        request = urllib2.Request(url=url, data=postdata, headers=headers)
        #logging.info('send to poll msg_id')
        try:
            html = self.opener.open(request).read()
        except urllib2.HTTPError, e:
            logging.warning('{0}'.format(e))
            return None
        jsonData = json.loads(html)
        logging.debug(html)
        retcode = jsonData.get('retcode')
        if retcode == 0 :
            try:
                if jsonData['result'][0]['poll_type'] == 'group_message': # 如果接受的消息是群信息
                    content = jsonData['result'][0]['value']['content'][1]
                    fromuin = jsonData['result'][0]['value']['from_uin']
                    #senduin = jsonData['result'][0]['value']['send_uin']    # 发送者的uin
                    value = ['group_message', fromuin, content, jsonData['result'][0]['value']['info_seq']]
                    #               群      群的uin    文本          群qq
                    #print 'value',value
                    return value
            except Exception, e:
                logging.error('Error {0}'.format(e))

        if retcode == 116:
            self.ptwebqq = jsonData.get('p')
        elif retcode == 121:
            logging.error(u'程序出现未知错误,可能断网,账号在别处登录(这是一个调试语句,请反馈)')
            os.remove('image.jpg')
            sendemail('121错误', u'121错误')
            exit()
        elif retcode == 103:
            logging.error(u'程序出现未知错误, 代码103')
            sendemail('103错误', u'103错误')

    def send_qun(self, group_uin, content):
        """发送群消息
        send_qun(群的uin不是群号码,要说的内容)
        """
        #r:{"to":3497160265,"content":"[\"44\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]","face":0,
        # "clientid":53999199,"msg_id":80120003,"psessionid":""}\
        url = 'http://d.web2.qq.com/channel/send_qun_msg2'
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'d.web2.qq.com',
                    'Origin':'http://d.web2.qq.com',
                    'Referer':'http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2'
                }
        try:
            data = {"group_uin":group_uin,"content":content,"face":30027,"clientid":53999199,
                    "msg_id":self.msgId,"psessionid": self.psessionid}
        except:
            print(u'这个无法识别.')
            return False

        self.msgId += 1
        postdata = urllib.urlencode({'r':json.dumps(data)})

        request = urllib2.Request(url=url,data=postdata,headers=headers)
        resule = self.opener.open(request).read()
        try:
            print resule
        except Exception, e:
            print e
        #print '发送群消息完成',resule
        return True

    def send_buddy_msg2(self):
        """发送好友信息
        """
        url = 'http://d.web2.qq.com/channel/send_buddy_msg2'


    def requestwqqcom(self):
        """暂时没作用"""
        logging.debug(u'REQUEST w.qq.com')
        url = "http://w.qq.com/"
        headers={'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
                    'Host':'w.qq.com'
                }
        request = urllib2.Request(url=url, headers=headers)
        resule = self.opener.open(request)
        logging.debug(self.cookie)


    def run(self):
        self.requestwqqcom()
        self.requestptlogin2qqcom() # 维持
        self.requestweb2qq()
        self.requestdweb2qq() # d.web2.qq
        self.get_user_friends2()
        self.get_group_name()
        while 1:
            data = self.poll2()
            if data: # 如果有数据，去找字典
                logging.info('{0}'.format(data))
                if not isinstance(data[2], unicode):
                    continue
                if data[2].strip() == '-h': # 如果接受-h 那么返回词库信息
                    gdata = ''
                    try:
                        for dic in self.dics:
                            gdata += dic.getinfo().replace("\n","\\n")
                        else:
                            if gdata:
                                world = "[\""+ gdata+"\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]"
                                self.send_qun(data[1], world)
                            continue
                    except Exception, e:
                        logging.error('解析getinfo出错 {0}'.format(e))

                for dic in self.dics:
                    content = dic.keyIn(data)
                    print 'content=',content
                    if content: # 如果有返回信息
                        if isinstance(content, unicode):
                            self.send_qun(data[1], content)
                            break
                else:
                    print 'has no data'




if __name__ == '__main__':
    myqq = Smartqq()
    myqq.downloadjpg()
    myqq.run()

