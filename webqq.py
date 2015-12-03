# -*- coding: utf-8 -*-
__mtime__ = '2015/6/30'
"""
人的成就感来源于两样东西，创造和毁灭。
dgl0518@gmail.com
version = v0.6

请运行main.py
"""
import re
import os
import sys
import ssl
import time
import json
import urllib
import urllib2
import random
import cookielib
import Queue
from threading import Thread
from PyQt4.QtGui import QApplication
from PyQt4.QtCore import QUrl
from PyQt4.QtWebKit import QWebPage
import logging

# 如果提示ssl证书出错,就取消注释
ssl._create_default_https_context = ssl._create_unverified_context


logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='myapp.log',
                filemode='w')

#################################################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s[line:%(lineno)d] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
#################################################################################################

class WebQQ():
    """
    user                  用户名QQ
    pwd                   密码
    qun                   要监听的群
    """
    def __init__(self, qq, pwd):
        self.user = qq
        self.pwd = pwd
        self.qun = []
        self.dics = []
        self.salt = ''
        self.vcode = ""
        self.ptwebqq= ''
        self.hash = ''
        self.msgId= random.randint(1000000,9999999)
        self.status= 'online' # 第二次提交里面的
        self.psessionid = '' # 通过第二次获取发送消息需要的
        self.vfwebqq = '' # 第二次提交返回的json,用于获取联系人列表等
        self.qqlist = {} # {"uin":qq号码}
        self.cookie = cookielib.CookieJar()
        self.headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
               'Host':'ssl.ptlogin2.qq.com',
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
               'Accept-Encoding':'gzip, deflate',
               'Connection': 'keep-alive'
               }
        self.header1 = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0)',
               'Host':"s.web2.qq.com",
               'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6',
               'Accept-Encoding':'gzip, deflate',
               'Connection': 'keep-alive',
               'Origin': 'http://s.web2.qq.com',
               'Referer' :"http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1"
               }
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cookie))
        urllib2.install_opener(self.opener)
        self.ptvfsession = self.get_ptvfsession()
        self.Q = Queue.Queue()
        self.NUM = 2 # 几线程
        


    def get_cookie_by_name(self, cj, name):
        # 查找 cookie.value
        return [cookie for cookie in cj if cookie.name == name][0]

    def setTime(self):
        return int(time.time()*1000)

    def gethash(uin, ptwebqq):
        uin += ""
        N=[0,0,0,0]
        for T in range(len(ptwebqq)):
            N[T%4]=N[T%4]^int(ptwebqq[T])


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



    def get_ptvfsession(self):
        # 得到 pt_verifysession_v1,为第一次连接做准备
        url = ('https://ssl.ptlogin2.qq.com/check?pt_tea=1&uin={user}&'
                'appid=501004106&js_ver=10128&js_type=0&login_sig=&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html&r=0.5468034720012842')
        request = urllib2.Request(url=url.format(user=self.user), headers=self.headers)
        resule = self.opener.open(request)
        ptui = re.findall(r"'(.*?)'",resule.read())

        if len(ptui) == 5 :
            print u'STEP1:成功获取ptvfsession:'
            logging.debug(resule.read())

            # 不需要验证码
            if ptui[0] == '0':
                print(ptui)
                self.vcode = ptui[1]
                self.salt = ptui[2]
                logging.debug(self.vcode)
                return ptui[3]
            else:
                # 需要验证码
                #ptui_checkVC('1','ur5fgIYoCFBoR8VjIq0eJatm7W1_DmSEHgcWPwT6LurJrnpsj3BGEg**','\x00\x00\x00\x00\x2b\xd5\xdc\xce','','0');
                logging.info('需要验证码')
                url = "https://ssl.captcha.qq.com/getimage?aid=501004106&r=0.07438549748621881&uin={user}&cap_cd={cap_cd}".format(user=self.user,cap_cd=ptui[1])
                self.salt = ptui[2]
                # 下载验证码
                x= self.opener.open(url).read()
                with open('vcode.jpg','wb') as f:
                    f.write(x)
                os.popen('start "" "vcode.jpg"')
                self.vcode = raw_input(u'在代码的当前目录找到vcode.jpg.然后输入它.Please input vcode:').upper()
                # 返回 verifysession
                return self.get_cookie_by_name(self.cookie, 'verifysession').value
        else:
            print(u'STEP1:第一步就出错了,下面就别运行了.')
            sys.exit()
         


    def firstLogin(self):

        def encodePassword():
        # 密码加密模块 ,为了可读性,放在里面
            password = self.pwd
            vcode = self.vcode

            passwdEncode="""<!DOCTYPE html>
                        <html>
                        <body>
                            JsCodeBetweenHere" -- <script src="encode.js"></script> --
                            <p id="demo"></p>
                            <script>
                            //var salt_ = uin2hex("{salt}");
                            document.getElementById("demo").innerHTML=getEncryption('{password}','{salt}','{vcode}');</script>
                        </body>
                        </html>
                        """
            with open('passwdEncode.html','w') as f:
                 f.write(passwdEncode.format(password=password,salt=self.salt,vcode=vcode))
            url = 'passwdEncode.html'  
            r = Render(url)
            html = r.frame.toHtml()
            pwd = re.findall(r'"demo">(.*?)</p>',html)[0]
            return pwd

        url= ("https://ssl.ptlogin2.qq.com/login?u={user}&p={pwd}&verifycode={vcode}&"
            "webqq_type=10&remember_uin=1&login2qq=1&aid=501004106&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&"
            "h=1&ptredirect=0&ptlang=2052&daid=164&from_ui=1&pttype=1&dumy=&fp=loginerroralert&action=0-22-9178&mibao_css=m_webqq&t=1&g=1&"
            "js_type=0&js_ver=10128&login_sig=&pt_randsalt=0&pt_vcode_v1=0&pt_verifysession_v1={ptvfsession}".format(user=self.user, pwd=encodePassword(),vcode=self.vcode,  ptvfsession=self.ptvfsession))
        print(url)
        self.headers['Referer'] = "https://ui.ptlogin2.qq.com/cgi-bin/login?daid=164&target=self&style=16&mibao_css=m_webqq&appid=501004106&enable_qlogin=0&no_verifyimg=1&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html&f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001"
        request = urllib2.Request(url=url, headers=self.headers)
        result = self.opener.open(request)
        tmp = re.findall(r"'(.*?)'",result.read())
        if tmp[0] == '0':
            try:
                print('STEP2:Welcome {0}'.format(tmp[-1]))
            except:
                print(u'Welcome --由Pythoner QQ群提供机器人')
        else:
        	logging.error('第一步登陆出错')


        # print tmp #调试用
        if tmp[2]:
            # print 'tmp[2]:',tmp[2] # 调试用
            request = urllib2.Request(url=tmp[2])
            # http://ptlogin4.web2.qq.com/check_sig?pttype=1&uin=1170624690&service=login&nodirect=0&ptsigx=1c1b9ce6493e0dc616f35447256e6228fe01d3111788e2d27b4b11f5c5a7cbbd9346640ff8892ce5574ccdad831d0077a7e9119bb096a29e365bbf82f40d95d0&s_url=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26webqq_type%3D10&f_url=&ptlang=2052&ptredirect=100&aid=501004106&daid=164&j_later=0&low_login_hour=0&regmaster=0&pt_login_type=1&pt_aid=0&pt_aaid=0&pt_light=0&pt_3rd_aid=0
            self.opener.open(request)
            self.ptwebqq = self.get_cookie_by_name(self.cookie, "ptwebqq").value

            return True
        else:
        	logging.error('获取ptwebqq出错'+tmp)
            # print(tmp)
            # print(tmp[4])
            return False


    def getvfwebqq(self):
        # 得到 vfwebqq 位于第一次和第二登录之间
        
        url = 'http://s.web2.qq.com/api/getvfwebqq?ptwebqq={ptwebqq}&clientid=53999199&psessionid=&t={t}'.format(ptwebqq=self.ptwebqq, t=self.setTime())
        print url
        self.headers['Referer'] = "http://s.web2.qq.com/proxy.html?v=20130916001&callback=1&id=1"
        self.headers['Host'] = "s.web2.qq.com"
        request  = urllib2.Request(url=url,headers=self.headers)
        result = self.opener.open(request).read()
        # print result
        logging.debug(result)
        jsonData = json.loads(result)

        self.vfwebqq = jsonData['result']['vfwebqq']
        print "jsonData@getvfwebqq = ",jsonData





    def secondeLogin(self):
        """第二次连接"""
        url = "http://d.web2.qq.com/channel/login2"
        data = {'ptwebqq':self.ptwebqq,
                'clientid':53999199,
                'psessionid':'',
                'status': self.status
        }
        postdata = urllib.urlencode({'r':json.dumps(data)})
        # postdata = postdata.replace('+','')

        # print('postdata:',postdata)
        logging.debug('postdata'+postdata) 
        self.headers['Referer'] = "http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2"
        self.headers['Host'] = "d.web2.qq.com"
        self.headers['Origin'] = "http://d.web2.qq.com"
        self.headers['Content-Type'] = "application/x-www-form-urlencoded"
        request = urllib2.Request(url=url, data=postdata,headers=self.headers)
        resultJson = self.opener.open(request).read()
        # print(resuleJson)
        logging.debug('第二次连接返回:'+postdata) 
        jsonData = json.loads(resultJson)
        try :
            self.psessionid = jsonData['result']['psessionid']
            print 'psessionid=',self.psessionid
            logging.debug('psessionid'+self.psessionid) 

            # print(self.psessionid) #调试
        except NameError,e:
        	logging.error('第二次连接出错:'+resultJson+str(e))
            # print(u'出错信息:',resultJson)
            sys.exit()


    def send_buddy_msg2(self, uin, content):
        #r:{"to":3497160265,"content":"[\"44\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]","face":0,
        # "clientid":53999199,"msg_id":80120003,"psessionid":""}
        # r:{"to":972050537,"content":"[\"1\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]","face":0,"clientid":53999199,"msg_id":20690001,"psessionid":""}
        url = "http://d.web2.qq.com/channel/send_buddy_msg2"
        try:
            data = {"to":uin,"content":content,"face":0,"clientid":53999199,"msg_id":self.msgId,"psessionid":self.psessionid}
        except:
            print (u'这个无法识别')
            return False
        self.msgId += 1
        postdata = urllib.urlencode({'r':json.dumps(data)})
        request = urllib2.Request(url=url,data=postdata,headers=self.headers)
        result = self.opener.open(request).read()
        logging.info('Send to friend:'+result)
        return True

    def send_sess_msg2(self, qunuin, uin, content):
        """临时会话"""
        # 为临时会话做准备
        

        def getGroupSig( qunuin, uin ):
            # 返回group_sig
            #print qunuin
            url = "http://d.web2.qq.com/channel/get_c2cmsg_sig2?id={qunuin}&to_uin={uin}&clientid=53999199&psessionid={psession}&service_type=0&t={t}".format(qunuin =qunuin ,uin=uin, psession=self.psessionid, t= self.setTime())
            #print '临时会话url=',url
            #print 'headers =',self.headers
            request = urllib2.Request(url=url,headers=self.headers)
            try:
                getgroup_sig = self.opener.open(request).read()
            except:
                return None
            group_sig = json.loads(getgroup_sig)['result']['value']
            #print '临时会话准备:',getgroup_sig
            return group_sig

        self.headers['Host'] = "d.web2.qq.com"
        url = "http://d.web2.qq.com/channel/send_sess_msg2"
        try:
            data = {"to":uin,"content":content,"face":0,"clientid":53999199,"msg_id":self.msgId, "psessionid":self.psessionid,
                    "group_sig":getGroupSig(qunuin, uin),"service_type":0}
        except KeyError,e:
            print(e,u'无法识别@send_sess_msg2')
            return False
        self.msgId += 1
        postdata = urllib.urlencode({'r':json.dumps(data)})
        request = urllib2.Request(url=url,data=postdata,headers=self.headers)
        result = self.opener.open(request).read()
        logging.info('send_sess_msg2',result)
        return True

    def send_qun(self, group_uin, content):
        """发送群消息
        send_qun(群的uin不是群号码,要说的内容)
        """
        #
        #r:{"to":3497160265,"content":"[\"44\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]","face":0,
        # "clientid":53999199,"msg_id":80120003,"psessionid":""}\
        url = 'http://d.web2.qq.com/channel/send_qun_msg2'
        try:
            data = {"group_uin":group_uin,u"content":content,"face":0,"clientid":53999199,
                    "msg_id":self.msgId,"psessionid": self.psessionid}
        except:
            print(u'这个无法识别.')
            return False

        self.msgId += 1
        postdata = urllib.urlencode({'r':json.dumps(data)})

        request = urllib2.Request(url=url,data=postdata,headers=self.headers)
        resule = self.opener.open(request).read()
        print '发送群消息完成',resule
        return True
        # print(u'send_qun:',resule.read())


    def get_user_friends2(self):
        """好友列表
        未完成
        """
        url = 'http://s.web2.qq.com/api/get_user_friends2'
        if self.hash == '':
            self.hash = self.getHash()
        print self.hash
        data = {'vfwebqq':self.vfwebqq,
                'hash':self.hash,
        }
        postdata = urllib.urlencode({'r':json.dumps(data)})
        request = urllib2.Request(url=url,data=postdata,headers=self.headers)
        resule = self.opener.open(request).read()
        print resule


        #r:{"vfwebqq":"04e0d5cea4db9f99ff14226b170336b7effbc79c20abc2213c62ec3e085f1f602824bd63e0bcf6df","hash":"59000B85021F57F9"}

    def get_group_name_list_mask2(self):
        """群列表"""
        url = 'http://s.web2.qq.com/api/get_group_name_list_mask2'
        if self.hash == '':
            self.hash = self.gethash(self.user,self.ptwebqq)
        data = {'vfwebqq':self.vfwebqq,
                'hash':self.hash}
        postdata = urllib.urlencode({'r':json.dumps(data)})
        request = urllib2.Request(url=url, data=postdata, headers=self.header1)
        result = self.opener.open(request).read()


        #r:{"vfwebqq":"04e0d5cea4db9f99ff14226b170336b7effbc79c20abc2213c62ec3e085f1f602824bd63e0bcf6df","hash":"59000B85021F57F9"}

    def get_friend_uin2(self, uin):
        """根据uin获取真实qq号码 
        位于poll2之后
        """
        url = "http://s.web2.qq.com/api/get_friend_uin2?tuin={uin}&type=1&vfwebqq={vfwebqq}&t={t}".format(uin=uin, vfwebqq=self.vfwebqq, t=self.setTime())
        # print "url = ",url
        request = urllib2.Request(url=url, headers=self.header1)
        result = self.opener.open(request).read()
        print u"得到真实QQ",result
        logging.info('get_friend_uin2'+result)

        jsonData = json.loads(result)
        try:
            return jsonData['result']['account']
        except:
            return 'wrong'


    def poll2(self):
        # headers = self.headers
        # headers['Referer']="http://d.web2.qq.com/proxy.html?v=20130916001&callback=1&id=2"
        # headers['Origin'] = "http://d.web2.qq.com"
        # headers['Host'] = "d.web2.qq.com"
        url = "http://d.web2.qq.com/channel/poll2"

        data = {"ptwebqq":self.ptwebqq,"clientid":53999199,"psessionid":self.psessionid,"key":""}
        postdata = urllib.urlencode({'r':json.dumps(data)})
        # r:{"ptwebqq":"ff8722e74af545034e2e0eda40e122893dde1ab207d6942ba2b02707564a1908","clientid":53999199,"psessionid":"8368046764001d636f6e6e7365727665725f77656271714031302e3133332e34312e383400001c28000015ad026e0400b250c6456d0000000a40506278457755704f426d000000282965a9252152552cf8f2192cb08db6e9db5b1ec1831ddc089161e141ce2c6e3acd6ab83ad8485ac6","key":""}
        request = urllib2.Request(url=url, data=postdata, headers=self.headers)
        resultJson = self.opener.open(request).read()
        
        logging.info(resultJson)
        # print resultJson # 返回的数据
        try:
            jsonData =json.loads(resultJson)
            retcode = jsonData.get('retcode')
        except ValueError, e:
            logging.warning('得到retcode出错'+str(e))
            return None

        # 得到poll2的各种返回值,并解析
            #{"retcode":0,"result":[{"poll_type":"group_message","value":{"msg_id":23466,"from_uin":1181939558,"to_uin":1170624690,"msg_id2":790448,"msg_type":43,"reply_ip":180061859,"group_code":2950907597,"send_uin":3848242064,"seq":356596,"time":1436432297,"info_seq":318611911,"content":[["font",{"size":10,"color":"000000","style":[0,0,0],"name":"\u5FAE\u8F6F\u96C5\u9ED1"}],"\u786E\u5B9A  \u6CA1\u6709\u8FDB\u5165\u767B\u5F55\u9875\u9762? "]}}]}
            #{"retcode":0,"result":[{"poll_type":"message","value":{"msg_id":33358,"from_uin":972050537,"to_uin":1170624690,"msg_id2":206584,"msg_type":9,"reply_ip":176488532,"time":1436432378,"content":[["font",{"size":10,"color":"000000","style":[0,0,0],"name":"\u5B8B\u4F53"}],"2 "]}}]}
            # {"retcode":0,"result":[{"poll_type":"group_message","value":{"msg_id":15327,"from_uin":1926942161,"to_uin":1170624690,"msg_id2":545479,"msg_type":43,"reply_ip":176756447,"group_code":361386902,"send_uin":3707129227,"seq":361526,"time":1436940494,"info_seq":318611911,"content":[["font",{"size":10,"color":"000000","style":[0,0,0],"name":"\u5FAE\u8F6F\u96C5\u9ED1"}],"\u6211\u8349 \u4E0D\u9519",["cface",{"name":"{DCE817CC-032E-1422-79B2-153FE30C8A1A}.GIF","file_id":2690274053,"key":"                ","server":"111.30.131.147:80"}]," "]}}]}
        if retcode == 0:
            content = jsonData['result'][0]['value']['content'][1]  # 数据
            if isinstance(content, list):
                content = jsonData['result'][0]['value']['content'][2]
                if isinstance(content, list):
                    return None

            if jsonData['result'][0]['poll_type'] == 'group_message':
                # 防止获取到 {"retcode":0,"result":[{"poll_type":"group_message","value":{"msg_id":18454,"from_uin":3934600307,"to_uin":1170624690,"msg_id2":818693,"msg_type":43,"reply_ip":176488532,"group_code":3104312629,"send_uin":1335530021,"seq":24388,"time":1436973033,"info_seq":172965579,"content":[["font",{"size":13,"color":"000000","style":[0,0,0],"name":"Vani"}],["face",1]," \u81EA\u5DF1\u722C\u4E00\u904D\u5C31\u77E5\u9053\u4E86 "]}}]}

                fromuin = jsonData['result'][0]['value']['from_uin']    # 群的uin
                senduin = jsonData['result'][0]['value']['send_uin']    # 发送者的uin

                if self.qqlist.has_key(str(senduin)):
                    # 通过senduin 获取真实qq
                    realQQ = self.qqlist[str(senduin)]
                else:
                    realQQ = self.get_friend_uin2(senduin)
                    self.qqlist[str(senduin)] = realQQ

                print "realQQ = ",realQQ

                value = [ 'group_message',                              # 消息类型
                        fromuin,                                        # 发送对象的uin(如果是群发送的,就是群的,不是发这个信息的人的uin)
                        content,                                        # 文本
                        jsonData['result'][0]['value']['info_seq'],     # 群QQ
                        realQQ                                          # 真实qq
                ]
                #                     类型:group_message                                 接受对象的uin                       文本                                         群qq
                return value
            elif jsonData['result'][0]['poll_type'] == 'sess_message': # 如果是临时消息

                value = [ 'sess_message', 
	                jsonData['result'][0]['value']['from_uin'], 
	                content,
	                jsonData['result'][0]['value']['id'],    # 群的uin
	                jsonData['result'][0]['value']['ruin'] ] #ruin是发送者qq号码
                # [类型, uin, 文本,群的uin, 发送者的qq号码]
                return value

            elif jsonData['result'][0]['poll_type'] == 'message' : # 如果是好友消息
                value = [ 'message', 
	                jsonData['result'][0]['value']['from_uin'], 
	                content ] # 机器人不要加好友
                return value                

        elif retcode == 116:
            p = jsonData.get('p')
            if p:
                self.ptwebqq = p

        elif retcode == 102:
            # 正常
            pass

        elif retcode == 121:
            print '程序出现未知错误,可能断网,账号在别处登录(这是一个调试语句,请反馈)'
            sys.exit()

        else:
            logging.info('Find a new retcode@258'+jsonData)

        #{"retcode":0,"result":[{"poll_type":"message","value":{"msg_id":10826,"from_uin":3497160265,"to_uin":1170624690,"msg_id2":35369,"msg_type":9,"reply_ip":180061926,"time":1436369771,"content":[["font",{"size":13,"color":"000000","style":[0,0,0],"name":"Vani"}],"77 "]}}]}
        #{"retcode":0,"result":[{"poll_type":"group_message","value":{"msg_id":29379,"from_uin":3611423534,"to_uin":1170624690,"msg_id2":894486,"msg_type":43,"reply_ip":176756639,"group_code":3863674170,"send_uin":3497160265,"seq":567,"time":1436369835,"info_seq":301311638,"content":[["font",{"size":13,"color":"000000","style":[0,0,0],"name":"Vani"}],"1 "]}}]}

        """
        类型 group_message
        发送者的qq 1170624690
        群的uin 3769154670
        content 1
        '群qq',x['result'][0]['value']['info_seq']
        """

    def install(self, *arg):
        self.dics = arg
        self.qun = [i[0] for i in arg]



    def sendMeg(self):
        # 未完成
        while 1:
            data = self.Q.get()
            # print "Q.get(data) = ",data
            if data[0] == "group_message" and data[3] in self.qun:
                # 得到传入的词库
                qunIndex = self.qun.index(data[3]) #  [group_message, 发送对象的uin(如果是群发送的,就是群的,不是发这个信息的人的uin) , 文本, 群qq, 发信息者真实的qq]
                print '这是一个群信息:',data[2]
                gdata = "" #存储全局数据
                for dic in self.dics[qunIndex][1]:
                    if data[2] == "-h ":
                        try:
                            a = dic.__doc__.replace("\n","\\n")
                            gdata += a
                        except Exception,e:
                            logging.debug('正在解析__doc__'+str(e))
                        continue

                    content = dic.keyIn(data)
                    # print '%s返回的:'%(dic.__class__),content
                    logging.info("%s返回:%s"%(dic.__class__,content))
                    # 如果词库有返回东西
                    if content :
                        if isinstance(content,unicode):
                            self.send_qun(data[1], content)
                            self.Q.task_done()
                            break
                        # 如果是列表
                        elif isinstance(content,list):
                            for qq in content[1]:
                                self.send_qun(self.qqlist[str(qq)], content)
                                self.Q.task_done()
                        else:
                            print "ERROR:%s返回的是"%(dic), type(content)
                        break
                        # 没返回跳出
                        
                else:
                    if gdata:
                        world = "[\""+ gdata+"\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]"
                        # print "-h =",world
                        #u"[\""+ gdata+u"\",[\"font\",{\"name\":\"宋体\",\"size\":10,\"style\":[0,0,0],\"color\":\"000000\"}]]"  
                        self.send_qun(data[1], world)
                        self.Q.task_done()

            elif data[0] == "sess_message":
                print '这是一个临时消息:',data[2]
                for dic in self.dics[0][1]:
                    content = dic.keyIn(data) # [类型, uin, 文本, 发送者的qq号码]
                    # print '词库返回的东西2:',content
                    logging.debug(content)
                    if content :
                        self.send_sess_msg2(data[3], data[1], content)
                        self.Q.task_done()
                        break

            # time.sleep(0.5)
        # print '我不应该输出的'


    def run(self):
        # 未完成
        if  not self.firstLogin():
            print('Error@firstLogin')
            sys.exit()
        # print 'getvfwebqq'
        self.getvfwebqq()
        # print 'getvfwebqqover'
        self.secondeLogin()

        # self.get_user_friends2()
        for i in range(self.NUM):
            t = Thread(target=self.sendMeg)
            t.setDaemon(True)
            t.start()
        while 1:
            try:
                while 1:
                    data = self.poll2()
                    if data:
                        self.Q.put(data)
                        break
            except Exception, e:
                logging.error("连接poll2出错%s"%e)
            # time.sleep(0.8)




class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit()  
  
# if __name__ == '__main__':
#     qq = WebQQ('qq号码','qq密码','[群号码,]')
#     qq.run()
"""
http://s.web2.qq.com/api/get_group_info_ext2?gcode=4021234072&vfwebqq=18719f04f2a09c5838ade2ca71ecd62417a4a1473da03d15117d0ba4bc775b8998e71a82c2bf4d48&t=1436941239672

{"retcode":0,"result":{"stats":[{"client_type":41,"uin":1170624690,"stat":10}],
"minfo":[{"nick":"认的你","province":"","gender":"male","uin":3932511133,"country":"","city":""},
{"nick":"VS","province":"江苏","gender":"male","uin":1170624690,"country":"中国","city":"镇江"}],
"ginfo":{"face":0,"memo":"","class":25,"fingermemo":"","code":4021234072,"createtime":1422517345,"flag":1090520065,"level":0,"name":"滚键盘","gid":2421039191,"owner":3932511133,"members":[{"muin":3932511133,"mflag":0},{"muin":1170624690,"mflag":0}],"option":2},
"vipinfo":[{"vip_level":0,"u":3932511133,"is_vip":0},{"vip_level":0,"u":1170624690,"is_vip":0}]}}

"""
