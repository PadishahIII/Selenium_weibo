from email.policy import strict
import json
from pickletools import long4
import re
from bs4 import BeautifulSoup
import urllib.request as request
import json
from matplotlib.font_manager import json_dump

from pymysql import NULL


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

    #翻页TODO:要先从翻页的事件中得到该页的所有url
    def getWholePage(current_page_ini, page):
        data = ''
        rnd = "1652528312609"  #递增
        current_page = current_page_ini
        since_id = ['4762965007931076',
                    '4759948456364531']  #4762965007931076,4759948456364531
        since_id_index = 0
        cnt = 0

        file = open("raw.html", "w", encoding="utf8", errors='replace')

        while (cnt < len(since_id)):
            pagebar = '1'
            if (since_id_index == 0):
                pagebar = '0'
            target = "https://weibo.com/p/aj/v6/mblog/mbloglist?ajwvr=6&domain=100808&current_page=" + str(
                current_page
            ) + "&since_id=" + since_id[since_id_index] + "&page=" + str(
                page
            ) + "&pagebar=" + pagebar + "&tab=super_index&pl_name=Pl_Core_MixedFeed__262&id=100808ec2f8f02483cbf2206505d27f9ffb3c1&script_uri=/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index&feed_type=1&pre_page=1&domain_op=100808&__rnd=" + rnd
            res = request.Request(target)
            res.add_header(
                "Cookie",
                "SINAGLOBAL=2012260830470.789.1652279835753; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; PC_TOKEN=cd12a7f8f3; ALF=1684120236; SSOLoginState=1652584238; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvXRRkvP0Egci3jorNLVmgEIoLZJiltCs6EotW9MTmb0g.; SUB=_2A25PhB9_DeThGeNJ7FYT8S_JwzSIHXVs8He3rDV8PUNbmtB-LXDVkW9NS7N3Vmp0gToiKS71-HWQ_dUptLT6cVtz; XSRF-TOKEN=HB3So32veWS4D1X56-gJBFRj; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9r59DJ9EF331uu4nyZDIBNpTGjjXP40N2nSgJ0MQYH2u-R8Qk6FIHoFm-sDtzMZiOQpBLhkNOeys2IK_5tVKRSsQ==; _s_tentry=weibo.com; Apache=1363728247308.7576.1652584251532; ULV=1652584251724:4:4:1:1363728247308.7576.1652584251532:1652526029346; wb_view_log_5774211588=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1652584560909%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A43%2C%22msgbox%22%3A0%7D"
            )
            response = request.urlopen(res)
            print(response.getcode())  #状态码
            res_doc = response.read()
            res_doc = res_doc.decode('unicode_escape',
                                     errors='replace')  #指定编码方式
            res_doc = getData(res_doc)
            if (since_id_index == 0):
                print("len:" + str(len(res_doc)))  #131123
                #print(int(since_id[0]) - int(since_id[1]))  #3016551566545

            file.write(res_doc)

            data += res_doc
            rnd = str(int(rnd) + 100000)
            cnt += 1
            current_page += 1
            since_id_index += 1
        file.close()
        return data

    data_ = getWholePage(2, page_index)
    data += data_

    #获取url列表
    if (page_index == 1):
        return data, getUrlList(data)

    return data


#从json字符串中提取data字段
def getData(jsonstr):
    jsonlist = list(jsonstr)
    index = jsonstr.find('"data":')
    jsonlist[index + len('"data":')]
    datastr = ''.join(jsonlist[index + len('"data":') + 1:len(jsonlist) - 2])
    return datastr.replace(r"\/", "/")


#提取所有页的链接
def getUrlList(html):
    a_bf = BeautifulSoup(html, features="html.parser")
    a_list = a_bf.find_all("a")
    url_list = set()
    for a_obj in a_list:
        if (a_obj != NULL and 'bpfilter' in a_obj.attrs.keys()
                and 'href' in a_obj.attrs.keys() and len(a_obj['href']) >= 30):
            url_list.add(a_obj['href'].replace(r'\/', '/'))
    return list(url_list)


#对整页的html预处理
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
            text_list.append(WB_text_W_f14_list[0].text.replace(' ', ''))

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
    #爬取网页
    UrlList = []
    res_doc, UrlList = scrapy(1)

    #预处理及提取
    out.write(res_doc)
    html_res = whole_preprocess(res_doc)
    nickname_list, date_list, text_list = getAllData(html_res)

    for i in range(0, len(nickname_list)):
        file.write(str(i) + ".  " + date_list[i] + "\n")
        file.write(nickname_list[i] + ":" + text_list[i] + "\n")
        file.write("\n")
    for i in range(len(nickname_list), len(text_list)):
        print(i, file=file)
        print(text_list[i], file=file)
        file.write("\n")

    print("帖子数：" + len(text_list))

    print("页数：" + len(UrlList))
    for i in UrlList:
        print(i)

    file.close()
    out.close()