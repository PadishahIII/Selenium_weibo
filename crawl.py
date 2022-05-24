from email.policy import strict
import json
from pickletools import long4
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request as request
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pymysql import NULL
import time
from types import NoneType


def scrapy_(cookie_str):
    file = open("test", "w", encoding="utf8", errors='replace')

    driver = webdriver.Edge()
    target_first = "https://weibo.com/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index?sudaref=weibo.com"
    driver.get(target_first)
    cookie_list = getDictCookie(cookie_str)
    for cookie in cookie_list:
        driver.add_cookie(cookie)
    driver.get(target_first)
    driver.refresh()

    driver.maximize_window()

    page_num = 1
    while (page_num <= 1):
        for i in range(5):  #滚动若干次
            js = "window.scrollTo(0,document.body.scrollHeight);"
            driver.execute_script(js)
            time.sleep(2)

        for ele in driver.find_elements_by_partial_link_text("展开全文"):
            driver.execute_script("arguments[0].click();", ele)
            time.sleep(2)

        html = driver.page_source
        nickname_list, date_list, text_list, statistic_list = getAllData(html)

        file.write("\n\n*******************  PAGE:" + str(page_num) +
                   " *****************************\n\n")
        file.write("帖子数：" + str(len(text_list)) + "\n")

        for i in range(0, len(nickname_list)):
            file.write(str(i) + ".  " + date_list[i] + "\n")
            file.write(nickname_list[i] + ":" + text_list[i] + "\n")
            file.write("评论数:" + statistic_list[i][0] + " 点赞数:" +
                       statistic_list[i][1] + "\n")
            file.write("\n")
        for i in range(len(nickname_list), len(text_list)):
            print(i, file=file)
            print(text_list[i], file=file)
            file.write("评论数:" + statistic_list[i][0] + " 点赞数:" +
                       statistic_list[i][1] + "\n")
            file.write("\n")

        next_page_btn = driver.find_element_by_link_text('下一页')
        if (next_page_btn != NULL and next_page_btn != NoneType):
            next_page_btn.click()
            time.sleep(2)
            page_num += 1
        else:
            break

    file.close()
    return


#构造cookie的关联数组
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


#(弃用)获取下一页的url
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


#(弃用)对整页的html预处理
def whole_preprocess(html):
    html_res = re.sub("<a.*?a>", '', html, 0)  #去掉链接
    #html_res = re.sub(r"\s", '', html_res, 0)  #去掉表情
    file = open("json.html", "w", encoding="utf8", errors="replace")

    #将script中的html代码提取出来,由于不需要utf8解码,html中的双引号已经是\",可以直接json解码
    json_list = re.findall("<script>FM.view\((.+)\);?</script>", html_res)
    for json_str in json_list:
        json_obj = json.loads(json_str, strict=False)
        if ("html" in json_obj.keys()):
            html_res += json_obj.get('html')
            #print(json_obj.get('html'), file=file)
    print(html_res, file=file)
    file.close()
    return html_res


#截取包含正文的div
def text_preprocess(html):
    rst = re.compile('<div class=.{0,4}WB_text W_f14.*?div>')  #非贪婪模式
    result = rst.findall(html)
    html_res = "\n".join(result)
    html_res = html_res.replace('\\', '')
    html_res = re.sub("<a.*?a>", '', html_res, 0)  #去掉链接
    return html_res


#提取每个帖子的时间、昵称、正文 TODO:评论
def getAllData(html):
    WB_box_bf = BeautifulSoup(html, features="html.parser")
    WB_box = WB_box_bf.find_all(
        "div", class_="WB_cardwrap WB_feed_type S_bg2 WB_feed_like")
    nickname_list = []  #昵称
    date_list = []  #帖子的时间
    text_list = []  #正文
    statistic_list = []  #评论数、点赞数

    #预处理
    def preprocess(html):
        filter_list = ['哈工大超话', '展开全文', '展开全文c', '收起全文', '收起全文d']
        html_res = re.sub("<a.*?</a>", '', html, 0)  #去掉链接
        for i in filter_list:
            html_res = html_res.replace(i, '')
        html_res = ''.join(x for x in html_res
                           if x.isprintable())  #去除不可打印字符如\u200b
        return html_res

    for i in WB_box:
        WB_detail_bf = BeautifulSoup(str(i))
        WB_detail = WB_detail_bf.find_all("div", class_="WB_detail")  #正文
        WB_handle = WB_detail_bf.find_all("div", class_="WB_handle")  #评论、点赞

        WB_info_bf = BeautifulSoup(str(WB_detail))

        WB_info_list = WB_info_bf.find_all("div", class_="WB_info")
        WB_from_S_txt2_list = WB_info_bf.find_all("div",
                                                  class_="WB_from S_txt2")
        WB_text_W_f14_list = WB_info_bf.find_all("div", class_="WB_text W_f14")

        a_nickname_bf = BeautifulSoup(str(WB_info_list[0]))
        a_date_bf = BeautifulSoup(str(WB_from_S_txt2_list[0]))

        a_nickname_list = a_nickname_bf.find_all("a")
        a_date_list = a_date_bf.find_all("a")

        span_bf = BeautifulSoup(str(WB_handle))
        span = span_bf.find_all("span", class_="line S_line1")
        em_reg = re.compile("<em>(.+?)</em>")
        if (len(span) >= 4):
            list = []
            for i in range(2, 4):
                text = em_reg.findall(str(span[i]).replace(' ', ''))
                if (text != NULL and text != NoneType and len(text) >= 1
                        and text[0].isdigit()):
                    list.append(text[0])
                else:
                    list.append('0')
            statistic_list.append(list)

        if (len(a_nickname_list) > 0):
            nickname_list.append(a_nickname_list[0].get("nick-name"))
        if (len(a_date_list) > 0):
            date_list.append(a_date_list[0].get("title"))
        if (len(WB_text_W_f14_list) > 0):
            if (len(WB_text_W_f14_list) == 1):
                text_list.append(
                    preprocess(WB_text_W_f14_list[0].text.replace(' ', '')))
            else:
                for text in WB_text_W_f14_list:
                    if ("node-type" in text.attrs.keys()
                            and text.get('node-type')
                            == 'feed_list_content_full'):  #展开全文
                        text_list.append(preprocess(text.text.replace(' ',
                                                                      '')))

    return nickname_list, date_list, text_list, statistic_list


#获取所有帖子正文(只提取正文)
def getText(html):
    div_bf = BeautifulSoup(html, features="html.parser")
    div = div_bf.find_all("div", class_="WB_text W_f14")
    list = []
    for i in div:
        list.append(i.text.replace(' ', ''))
    return list


if __name__ == "__main__":
    file = open("test", "w", encoding="utf8", errors='replace')
    out = open("res.html", "w", encoding="utf8", errors='replace')
    cookie_str = "SINAGLOBAL=2012260830470.789.1652279835753; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; webim_unReadCount=%7B%22time%22%3A1653323934983%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A41%2C%22msgbox%22%3A0%7D; PC_TOKEN=40a9a3a8e1; ALF=1684921934; SSOLoginState=1653385937; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvl0BlyU53MMV1Cc_p5M_sHLA8zHJlVl3qGGewPqoj6M4.; SUB=_2A25PiNqBDeThGeNJ7FYT8S_JwzSIHXVs_EtJrDV8PUNbmtB-LUrzkW9NS7N3Vholte-i4RmbiaLABOALFbG5sXjb; _s_tentry=weibo.com; Apache=7945095029938.9.1653385986988; ULV=1653385987133:6:6:2:7945095029938.9.1653385986988:1653316943984"
    scrapy_(cookie_str)
