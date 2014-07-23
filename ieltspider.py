#coding=utf8


import cookielib
import urllib2, urllib
import time
import re
import traceback
import time
import shutil
import hashlib

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.ProxyHandler({'http':"10.239.120.37:911"}))
opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'),
                     ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'), 
                     ('Accept-Language', 'zh-cn,zh;q=0.8,en-us;q=0.5,en;q=0.3'), 
                     ('Connection', 'keep-alive'),
                     ]
opener.addheaders.append( ('Accept-encoding', 'identity') )
opener.addheaders.append( ('Referer', 'http://ielts.etest.net.cn/login') )


def get_page(url, data=None):
    resp = None
    n = 0
    while n < 3:
        n = n + 1
        try:
            resp = opener.open(url, data, timeout=5)
            page = resp.read()
            return page
        except:
            traceback.print_exc()
            print "Will try after 1 seconds ..."
            time.sleep(1)
            continue
        break
    return "Null"


AREA_MAP = {
    "北京"   : "11" ,
    "天津"   : "12" ,
    "河北"   : "13" ,
    "山西"   : "14" ,
    "内蒙古" : "15" ,
    "辽宁"   : "21" ,
    "吉林"   : "22" ,
    "黑龙江" : "23" ,
    "上海"   : "31" ,
    "江苏"   : "32" ,
    "浙江"   : "33" ,
    "安徽"   : "34" ,
    "福建"   : "35" ,
    "江西"   : "36" ,
    "山东"   : "37" ,
    "河南"   : "41" ,
    "湖北"   : "42" ,
    "湖南"   : "43" ,
    "广东"   : "44" ,
    "广西"   : "45" ,
    "海南"   : "46" ,
    "重庆"   : "50" ,
    "四川"   : "51" ,
    "贵州"   : "52" ,
    "云南"   : "53" ,
    "陕西"   : "61" ,
    "甘肃"   : "62" ,
    "新疆"   : "65" ,
}

LOGIN_URL = "http://ielts.etest.net.cn/login"
QUERY_URL = "http://ielts.etest.net.cn/myHome/1945505/queryTestSeats?queryMonths=$qms&queryProvinces=$qps"

username = "1945505"
password = "huangliming" #"4a788c684c43ad35f11c3f5e2b39638e"
pwd_md5 = hashlib.md5(password).hexdigest()

p = get_page(LOGIN_URL)
csrf = re.findall(r'name="CSRFToken" value="(.*)"', p)[0]
print csrf

formData = urllib.urlencode({'userId' : username,
                             'userPwd' : pwd_md5,
                             'checkImageCode' : "",
                             'CSRFToken' : csrf,
                             })
p = get_page(LOGIN_URL, formData)
if "我的主页" not in p:
    raise "请输入验证码"
#print p


query_url = QUERY_URL.replace("$qms", "2014-09").replace("$qps", "11,12")
print query_url
p = get_page(query_url)
print p