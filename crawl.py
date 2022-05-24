from email.policy import strict
import json
from pickletools import long4
import re
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request as request
import json
from matplotlib.font_manager import json_dump
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

        html = driver.page_source
        nickname_list, date_list, text_list = getAllData(html)

        file.write("\n\n*******************  PAGE:" + str(page_num) +
                   " *****************************\n\n")
        file.write("帖子数：" + str(len(text_list)) + "\n")

        for i in range(0, len(nickname_list)):
            file.write(str(i) + ".  " + date_list[i] + "\n")
            file.write(nickname_list[i] + ":" + text_list[i] + "\n")
            file.write("\n")
        for i in range(len(nickname_list), len(text_list)):
            print(i, file=file)
            print(text_list[i], file=file)
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


#获取一整页的内容
def scrapy(page_index):
    data = ''
    #第一页,获取url列表
    if (page_index == 1):
        target_first = "https://weibo.com/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index?current_page=6&since_id=4738962205704901&page=1"
        target = target_first
    else:
        target = "https://weibo.com" + UrlList[page_index - 1]
        #since_id = '4738962205704901'  #4738962205704901
    #page = page_index
    #current_page = 2

    res = request.Request(target)
    res.add_header(
        "Cookie",
        "SINAGLOBAL=2012260830470.789.1652279835753; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; PC_TOKEN=cd12a7f8f3; ALF=1684120236; SSOLoginState=1652584238; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvXRRkvP0Egci3jorNLVmgEIoLZJiltCs6EotW9MTmb0g.; SUB=_2A25PhB9_DeThGeNJ7FYT8S_JwzSIHXVs8He3rDV8PUNbmtB-LXDVkW9NS7N3Vmp0gToiKS71-HWQ_dUptLT6cVtz; XSRF-TOKEN=HB3So32veWS4D1X56-gJBFRj; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9r59DJ9EF331uu4nyZDIBNpTGjjXP40N2nSgJ0MQYH2u-R8Qk6FIHoFm-sDtzMZiOQpBLhkNOeys2IK_5tVKRSsQ==; _s_tentry=weibo.com; Apache=1363728247308.7576.1652584251532; ULV=1652584251724:4:4:1:1363728247308.7576.1652584251532:1652526029346; wb_view_log_5774211588=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1652584560909%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A43%2C%22msgbox%22%3A0%7D"
    )
    response = request.urlopen(res)
    print(response.getcode())  #状态码
    res_doc = response.read()
    res_doc = res_doc.decode('utf8', errors='replace')  #指定编码方式
    data += res_doc

    #获取第一个滚动url
    si_cp_tab = getSinceID(res_doc)
    print(si_cp_tab)

    #翻页TODO:要先从翻页的事件中得到该页的所有url
    def getWholePage(current_page_ini, page, si_cp_tab):
        data = ''
        rnd = "1652528312609"  #递增
        #current_page = current_page_ini
        #since_id = ['4762965007931076',
        #            '4759948456364531']  #4762965007931076,4759948456364531
        #since_id_index = 0
        cnt = 0

        file = open("raw.html", "w", encoding="utf8", errors='replace')

        while (si_cp_tab != ''):
            pagebar = '1'
            if (cnt == 0):
                pagebar = '0'
            target = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100808&" + si_cp_tab + "&page=" + str(
                page
            ) + "&pagebar=" + pagebar + "&pl_name=Pl_Core_MixedFeed__262&id=100808ec2f8f02483cbf2206505d27f9ffb3c1&script_uri=/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index&feed_type=1&pre_page=1&domain_op=100808&__rnd=" + rnd
            res = request.Request(target)
            res.add_header(
                "Cookie",
                "SINAGLOBAL=2012260830470.789.1652279835753; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; PC_TOKEN=cd12a7f8f3; ALF=1684120236; SSOLoginState=1652584238; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvXRRkvP0Egci3jorNLVmgEIoLZJiltCs6EotW9MTmb0g.; SUB=_2A25PhB9_DeThGeNJ7FYT8S_JwzSIHXVs8He3rDV8PUNbmtB-LXDVkW9NS7N3Vmp0gToiKS71-HWQ_dUptLT6cVtz; XSRF-TOKEN=HB3So32veWS4D1X56-gJBFRj; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9r59DJ9EF331uu4nyZDIBNpTGjjXP40N2nSgJ0MQYH2u-R8Qk6FIHoFm-sDtzMZiOQpBLhkNOeys2IK_5tVKRSsQ==; _s_tentry=weibo.com; Apache=1363728247308.7576.1652584251532; ULV=1652584251724:4:4:1:1363728247308.7576.1652584251532:1652526029346; wb_view_log_5774211588=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1652584560909%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A43%2C%22msgbox%22%3A0%7D"
            )
            #发送请求 应答为json
            response = request.urlopen(res)
            print(response.getcode())  #状态码
            res_doc = response.read()
            res_doc = res_doc.decode('unicode_escape',
                                     errors='replace')  #指定编码方式
            res_doc = getData(res_doc)

            #在新的应答中提取下一次翻页的url
            si_cp_tab = getSinceID(res_doc)
            print(si_cp_tab)

            file.write(res_doc)
            file.write(
                "\n<!-- ******************************************************************************** -->\n"
            )

            data += res_doc
            rnd = str(int(rnd) + 100000)
            cnt += 1
        file.close()
        return data

    data_ = getWholePage(2, page_index, si_cp_tab)
    data += data_

    #获取url列表
    if (page_index == 1):
        return data, getUrlList(data)

    return data


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
    WB_detail_bf = BeautifulSoup(html, features="html.parser")
    WB_detail = WB_detail_bf.find_all("div", class_="WB_detail")
    nickname_list = []  #昵称
    date_list = []  #帖子的时间
    text_list = []  #正文

    #预处理
    def preprocess(html):
        html_res = re.sub("<a.*?</a>", '', html, 0)  #去掉链接
        html_res = html_res.replace("哈工大超话", '')
        html_res = ''.join(x for x in html_res
                           if x.isprintable())  #去除不可打印字符如\u200b
        return html_res

    for i in WB_detail:
        WB_info_bf = BeautifulSoup(str(i))

        WB_info_list = WB_info_bf.find_all("div", class_="WB_info")
        WB_from_S_txt2_list = WB_info_bf.find_all("div",
                                                  class_="WB_from S_txt2")
        WB_text_W_f14_list = WB_info_bf.find_all("div", class_="WB_text W_f14")

        a_nickname_bf = BeautifulSoup(str(WB_info_list[0]))
        a_date_bf = BeautifulSoup(str(WB_from_S_txt2_list[0]))

        a_nickname_list = a_nickname_bf.find_all("a")
        a_date_list = a_date_bf.find_all("a")

        if (len(a_nickname_list) > 0):
            nickname_list.append(a_nickname_list[0].get("nick-name"))
        if (len(a_date_list) > 0):
            date_list.append(a_date_list[0].get("title"))
        if (len(WB_text_W_f14_list) > 0):
            text_list.append(
                preprocess(WB_text_W_f14_list[0].text.replace(' ', '')))

    return nickname_list, date_list, text_list


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
