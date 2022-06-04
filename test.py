from base64 import encode
import re
from types import NoneType
from pymysql import NULL
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from datetime import datetime
import json
from urllib import request


def getNextPage(html):
    rst = re.compile(r"<a.*?href=\"(.+?)\".*?>下一页</a>")
    href = rst.findall(html)
    return href


target = "https://api.weibo.com/2/comments/show.json?access_token=2.00yMAmSG0NzCoG7969bfecd0mHIdlC&id=4761732520611140"
res = request.Request(target)
response = request.urlopen(res)
print(response.getcode())
res_doc = response.read()
data_str = res_doc.decode('utf8')
data_obj = json.loads(data_str)
print(data_obj.keys())
print(data_obj['comments'][0]['text'])
print(data_obj['comments'][0]['idstr'])
print(data_obj['comments'][0]['user']['name'])
print(data_obj['comments'][0]['user']['profile_image_url'])
print(data_obj['comments'][0]['status']['text'])

#file = open("test.html", "r", errors="replace", encoding='utf8')
#option = webdriver.EdgeOptions()
#option.add_argument("headless")
#driver = webdriver.Edge(options=option)
#driver.get("http://localhost")
#ele = driver.find_element_by_link_text("link")
#print(ele)

#str = "Wed Jun 01 00:50:25 +0800 2011"
#format = "%a %b %d %H:%M:%S +0800 %Y"
#print(datetime.strptime(str, format))
#str = '{"a":1}'
#obj = json.loads(str)
#print(obj)

#function apply(){form = document.getElementById('queryform');list = form.getElementsByTagName('select');for(var i = 0;i<list.length;i++){list[i].options[1].selected=true; list[i].onchange();}}var btn = document.createElement('button');var parent = document.getElementById('bt').parentElement;btn.innerHTML="Automate";btn.onclick=apply;parent.appendChild(btn);
