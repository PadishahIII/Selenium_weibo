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


def getNextPage(html):
    rst = re.compile(r"<a.*?href=\"(.+?)\".*?>下一页</a>")
    href = rst.findall(html)
    return href


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
str = '{"a":1}'
obj = json.loads(str)
print(obj)
