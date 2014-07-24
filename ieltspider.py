#coding=utf8

import cookielib
import urllib2, urllib
import time
import re
import traceback
import time
import shutil
import hashlib
import json
import pprint


class User(object):
    """docstring for User"""

    AREA_MAP = {
        u"北京"   : "11" ,
        u"天津"   : "12" ,
        u"河北"   : "13" ,
        u"山西"   : "14" ,
        u"内蒙古" : "15" ,
        u"辽宁"   : "21" ,
        u"吉林"   : "22" ,
        u"黑龙江" : "23" ,
        u"上海"   : "31" ,
        u"江苏"   : "32" ,
        u"浙江"   : "33" ,
        u"安徽"   : "34" ,
        u"福建"   : "35" ,
        u"江西"   : "36" ,
        u"山东"   : "37" ,
        u"河南"   : "41" ,
        u"湖北"   : "42" ,
        u"湖南"   : "43" ,
        u"广东"   : "44" ,
        u"广西"   : "45" ,
        u"海南"   : "46" ,
        u"重庆"   : "50" ,
        u"四川"   : "51" ,
        u"贵州"   : "52" ,
        u"云南"   : "53" ,
        u"陕西"   : "61" ,
        u"甘肃"   : "62" ,
        u"新疆"   : "65" ,
    }

    def __init__(self, username="", password="", adminDate=""):
        self.username = username
        self.password = password
        self.adminDate = adminDate
        self.pwd_md5 = hashlib.md5(password).hexdigest()
        self.userid = username
        self.areas = ""
        self.centers = []

    @property
    def login_url(self):
        return "http://ielts.etest.net.cn/login"

    @property
    def query_url(self):
        return "http://ielts.etest.net.cn/myHome/%s/queryTestSeats?queryMonths=%s&queryProvinces=%s" % (self.userid, self.adminDate[:7], self.areas)

    @property
    def confirm_url(self):
        return "http://ielts.etest.net.cn/myHome/%s/createOrderConfirm" % self.userid

    @property
    def appoint_url(self):
        return "http://ielts.etest.net.cn/myHome/%s/newAppointment" % self.userid

    @property
    def reg_url(self):
        return "http://ielts.etest.net.cn/myHome/%s/registration" % self.userid

    def add_center(self, centerNameCn):
        # centerNameCn must be unicode
        self.centers.append(centerNameCn)

    def set_areas(self, areas_list):
        rs = []
        for name in areas_list:
            aid = self.AREA_MAP[name]
            rs.append(aid)
        self.areas = ",".join(rs)



users = []
s = open("info.txt").read().strip().decode("gbk")
parts = s.split("\n\n")
for part in parts:
    username, password, adminDate, areas, centers = part.split("\n")
    areas = areas.split(",")
    centers = centers.split(",")
    user = User(username, password, adminDate)
    user.set_areas(areas)
    user.centers = centers
    users.append(user)

users = users[:10]


open("success.txt", "a").write("================================\n")

while users:
    print "=============================================================="

    for user in users:

        try:

            time.sleep(1)

            print "-------", user.username, '---------'

            # if user.username in open("success").raad():
            #     users.remove(user)
            #     print user.username, "Successed"
            #     continue

            cj = cookielib.CookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
            #opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj), urllib2.ProxyHandler({'http':"10.239.120.37:911"}))
            opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.2) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.89 Safari/537.1'),
                                 ('Host', 'ielts.etest.net.cn'), 
                                 ('Origin', 'http://ielts.etest.net.cn'), 
                                 ]

            def get_page(url, data=None):
                resp = None
                n = 0
                while n < 2:
                    n = n + 1
                    try:
                        resp = opener.open(url, data, timeout=5)
                        page = resp.read()
                        return page
                    except:
                        #traceback.print_exc()
                        print "Will try after 1 seconds ..."
                        time.sleep(1)
                        continue
                raise "Get page failed"


            p = get_page(user.login_url)
            csrf = re.findall(r'name="CSRFToken" value="(.*)"', p)[0]
            print csrf

            formData = urllib.urlencode({'userId' : user.username,
                                         'userPwd' : user.pwd_md5,
                                         'checkImageCode' : "",
                                         'CSRFToken' : csrf,
                                         })
            p = get_page(user.login_url, formData)

            if "我的主页" not in p:
                raise "登陆失败 可能需要验证码"

            userid = re.findall(r'ID: </label> <span style=".*">(.*)</span>', p)[0]
            user.userid = userid

            p = get_page(user.reg_url)
            csrf = re.findall(r'name="CSRFToken" value="(.*)"', p)[0]

            print csrf, userid


            print user.query_url
            p = get_page(user.query_url)

            p = json.loads(p)

            rs = []
            for ls in p.values():
                rs += ls

            for r in rs:
                if r["adminDate"] == user.adminDate and r["centerNameCn"] in user.centers:
                    print r["adminDate"], r["centerNameCn"],
                    if r["optStatusEn"] != "Book seat":
                        print r["optStatusCn"]
                        if r['optStatusEn'] == "Test on the same date already booked, no re-booking allowed":
                            try:
                                users.remove(user)
                            except:
                                pass
                        continue

                    seatGuid = r["seatGuid"]
                    print u"可以预订", seatGuid
                    formData = urllib.urlencode({'seatGuid' : seatGuid,
                                                 'CSRFToken' : csrf,
                                                 })
                    p = get_page(user.confirm_url, formData)
                    if "btnConfirmNext" not in p:
                        print u"确认失败 下一轮重试"
                        continue
                    p = get_page(user.appoint_url, formData)
                    if '<li class="active">预订考位成功</li>' not in p:
                        print u"预订失败 下一轮重试"
                        continue

                    print u"预订考位成功", user.username, r["adminDate"], r["centerNameCn"]
                    success_msg = user.username + u" " + r["adminDate"] + u" " + r["centerNameCn"] + u"\n"
                    open("success.txt", "a").write(success_msg.encode("gbk"))
                    try:
                        users.remove(user)
                    except:
                        pass

        except:
            traceback.print_exc()


input_raw(u"完成所有任务,按下回车键退出...")


"""
info.txt example:

1945505
huangliming
2014-09-20
天津,北京
北京语言大学,天津外国语大学

rrrpvk@qq.com
Heyunting199759
2014-09-20
北京,天津
天津外国语大学

18801024845
danielYOUNG2014
2014-08-09
北京,天津
北京外国语大学IELTS考试中心,北京语言大学
"""

