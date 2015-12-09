# -*- coding: utf-8 -*-
"""
示例词库,返回天气
出现错误请联系dgl0518@gmail.com
欢迎进QQ群讨论172965579
"""
__author__ = 'Twotiger'
__mtime__ = '2015/7/17'

"""
人的成就感来源于两样东西，创造和毁灭。
"""
import json
import urllib2

from baseclass import BaseDict
base = BaseDict()


class Weather(BaseDict):
    """
    命令: <城市>天气 --认的你
        南京天气
        北京天气
"""
    def __init__(self):
        self.ak = "A1ee5b034230a2b914d5208a64c4a66d" # 我相信你是一个有节操的程序员,请到 http://developer.baidu.com/map/carapi-7.htm 申请
        self.url = "http://api.map.baidu.com/telematics/v3/weather?location={city}&output=json&ak={ak}"
        self.headers = {
            "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.134 Safari/537.36"
        }


    def getJson(self, city):
        request = urllib2.Request(url=self.url.format(city=city.encode('utf-8'), ak=self.ak),headers=self.headers)
        try:
            result = urllib2.urlopen(request).read()
        except:
        #except urllib2.HTTPError:
            print "获取JSON失败@getweather.py"
            return None
        jsondata = json.loads(result)
        data = ""
        if jsondata['error'] == 0:
            data = jsondata['results'][0]['currentCity'] + "\\n" + "PM25:" +jsondata['results'][0]['pm25'] + "\\n"
            for i in jsondata['results'][0]['weather_data']:
                data += i['date'] +' '+ i['temperature'] +' '+i['weather'] +' '+ i['wind'] +"\\n"
            return data
        else:
            return result

    @base.mydecorator
    def keyIn(self, content):
        city = (content[2].strip())[:-2]
        print type(city)
        if city and (content[2].strip())[-2:]==u"天气":
            weather1 = self.getJson(city)
            # print 'wheather1=',weather1
            return weather1
        else:
            return None

    def getinfo(self):
        return """命令: <城市>天气 --认的你
        南京天气
        北京天气
"""


if __name__ == "__main__":
    print Weather
    weahter1 = Weather()
    print weahter1.keyIn([1,2,u'镇江天气'])
