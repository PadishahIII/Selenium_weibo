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


def getNextPage(html):
    rst = re.compile(r"<a.*?href=\"(.+?)\".*?>下一页</a>")
    href = rst.findall(html)
    return href


file = open("test.html", "r", errors="replace", encoding='utf8')
#driver = webdriver.Edge()
#driver.get("http://localhost/test/test.html")
html = file.read()

#rst = re.compile(r"\"")
#str = "href=\"ss"
#print('a')
loc = html.find("下一页")
print(loc)
html = html[loc - 600:loc + 100]
print(html)
html = re.sub("\s", "", html, 0)
print(html)

rst = re.compile(r"<a.*?href=\"(\S+?)\"[^<]*?>下一页</a>")
res = rst.findall(html)
print(res[0])
rst = re.compile("http[s]?://\S+(/\S+?)*")
str = 'javascript:void(0)"class="pageS_txt1"suda-uatrack="key=tblog_profile_v6&amp;value=weibo_page">第&nbsp;1&nbsp;页<emclass="W_ficonficon_arrow_downS_ficon">c</em></a></span><aaction-type='
res = rst.match(str)
if (type(res) != NoneType):
    print(res.group())