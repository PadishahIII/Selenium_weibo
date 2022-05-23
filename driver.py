from types import NoneType
from bs4 import BeautifulSoup
from pymysql import NULL
import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
import re


def getDictCookie(str):
    cookie_list = list()
    rst = re.compile(r"(.+?)\s*=\s*(.+?)\s*;")
    res = rst.findall(str)
    for i in res:
        if (i[0] != '' and i[1] != ''):
            cookie = dict()
            cookie['name'] = i[0].replace(" ", "")
            cookie['value'] = i[1].replace(" ", "")
            cookie['domain'] = 'weibo.com'
            cookie_list.append(cookie)

    return cookie_list


def getNextPage(html):
    loc = html.find("下一页")
    html = html[loc - 600:loc + 100]
    print(html)
    html = re.sub("\s", "", html, 0)
    rst = re.compile("<a.*?href=\"(\S+?)\"[^<]*?>下一页</a>")
    href = rst.findall(html)
    rst = re.compile("http[s]?://\S+(/\S+?)*")
    if (href == NULL or len(href) == 0
            or type(rst.match(href[0])) == NoneType):
        return ''
    return href[0]


def scrapy(cookie_str):
    driver = webdriver.Edge()
    file = open("log", "w", errors="replace")
    target_first = "https://weibo.com/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index?sudaref=weibo.com"
    driver.get(target_first)
    cookie_list = getDictCookie(cookie_str)
    for cookie in cookie_list:
        driver.add_cookie(cookie)
    driver.get(target_first)
    driver.refresh()

    driver.maximize_window()
    #next_page = NULL
    #next_page_link = re.compile(r"")
    for i in range(5):  #滚动若干次
        js = "window.scrollTo(0,document.body.scrollHeight);"
        driver.execute_script(js)
        time.sleep(2)
        #try:
        #    #next_page = driver.find_element(by=By.CLASS_NAME,
        #    #                                value='page next S_txt1 S_line1')
        #    next_page = driver.find_element_by_class_name(
        #        'page next S_txt1 S_line1')
        #except selenium.common.exceptions.NoSuchElementException as e:
        #    continue
    html = driver.page_source
    file.write(html)
    next_page_url = getNextPage(html)
    if (next_page_url != ''):
        js = "let atag  = document.createElement('a');atag.href='{0}';atag.click();".format(
            next_page_url)
        driver.execute_script(js)
    else:
        print("none nextUrl")
    #next_page.click()
    time.sleep(9999)


if __name__ == '__main__':
    #str = "SINAGLOBAL=2012260830470.789.1652279835753; SSOLoginState=1652584238; XSRF-TOKEN=HB3So32veWS4D1X56-gJBFRj; _s_tentry=weibo.com; Apache=1363728247308.7576.1652584251532; ULV=1652584251724:4:4:1:1363728247308.7576.1652584251532:1652526029346; PC_TOKEN=21f4d2caee; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; ALF=1684769000; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvrjXUMBPo1gmYeyouta8PyTPbt9JdTzK3SuOWOeqzels.; SUB=_2A25PjiU6DeThGeNJ7FYT8S_JwzSIHXVs-hHyrDV8PUNbmtANLUTAkW9NS7N3VnPuWs1ATF_0jrxtW2wwTO7MY0hL; wb_view_log_5774211588=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1653233010269%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A44%2C%22msgbox%22%3A0%7D"
    #Dict = getDictCookie(str)
    #print(Dict)
    cookie_str = "SINAGLOBAL=2012260830470.789.1652279835753; SSOLoginState=1652584238; XSRF-TOKEN=HB3So32veWS4D1X56-gJBFRj; _s_tentry=weibo.com; Apache=1363728247308.7576.1652584251532; ULV=1652584251724:4:4:1:1363728247308.7576.1652584251532:1652526029346; PC_TOKEN=21f4d2caee; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; ALF=1684769000; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvrjXUMBPo1gmYeyouta8PyTPbt9JdTzK3SuOWOeqzels.; SUB=_2A25PjiU6DeThGeNJ7FYT8S_JwzSIHXVs-hHyrDV8PUNbmtANLUTAkW9NS7N3VnPuWs1ATF_0jrxtW2wwTO7MY0hL; wb_view_log_5774211588=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1653233010269%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A44%2C%22msgbox%22%3A0%7D"
    scrapy(cookie_str)