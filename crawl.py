from pickletools import long4
import re
from bs4 import BeautifulSoup
import urllib.request as request
import json

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
        "SINAGLOBAL=2012260830470.789.1652279835753; XSRF-TOKEN=I3QNp-m8uSVO6N7LAOQxDknN; SUB=_2A25Pe2fWDeThGeNJ7FYT8S_JwzSIHXVs8d4erDV8PUNbmtB-LWjFkW9NS7N3VgUdjDA5fIZiiRyWEk7wFs82GIXP; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KzhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; ALF=1684032261; SSOLoginState=1652496262; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9r59DJ9EF331uu4nyZDIBNpVVl3AOcV5p2YOot_aZfdCU9BbFyKBCNCwewoB7jlCZY9zQd5Y1oBhziWFQ66FSseA==; PC_TOKEN=1318b7196f; _s_tentry=weibo.com; Apache=9624643993500.246.1652496293665; ULV=1652496293682:2:2:2:9624643993500.246.1652496293665:1652279835810; webim_unReadCount=%7B%22time%22%3A1652496331274%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A43%2C%22msgbox%22%3A0%7D; wb_view_log_5774211588=1536*8641.25"
    )
    response = request.urlopen(res)
    print(response.getcode())  #状态码
    res_doc = response.read()
    res_doc = res_doc.decode('utf8')  #指定编码方式
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
                "SINAGLOBAL=2012260830470.789.1652279835753; XSRF-TOKEN=I3QNp-m8uSVO6N7LAOQxDknN; SUB=_2A25Pe2fWDeThGeNJ7FYT8S_JwzSIHXVs8d4erDV8PUNbmtB-LWjFkW9NS7N3VgUdjDA5fIZiiRyWEk7wFs82GIXP; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KzhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; ALF=1684032261; SSOLoginState=1652496262; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9r59DJ9EF331uu4nyZDIBNpVVl3AOcV5p2YOot_aZfdCU9BbFyKBCNCwewoB7jlCZY9zQd5Y1oBhziWFQ66FSseA==; PC_TOKEN=1318b7196f; _s_tentry=weibo.com; Apache=9624643993500.246.1652496293665; ULV=1652496293682:2:2:2:9624643993500.246.1652496293665:1652279835810; webim_unReadCount=%7B%22time%22%3A1652496331274%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A43%2C%22msgbox%22%3A0%7D; wb_view_log_5774211588=1536*8641.25"
            )
            response = request.urlopen(res)
            print(response.getcode())  #状态码
            res_doc = response.read()
            res_doc = res_doc.decode('unicode_escape')  #指定编码方式
            if (since_id_index == 0):
                print("len:" + str(len(res_doc)))  #131123
                #print(int(since_id[0]) - int(since_id[1]))  #3016551566545

            data += res_doc
            rnd = str(int(rnd) + 100000)
            cnt += 1
            current_page += 1
            since_id_index += 1
        return data

    data_ = getWholePage(2, page_index)
    data += data_

    #获取url列表
    if (page_index == 1):
        return data, getUrlList(data)

    return data


def getUrlList(html):
    a_bf = BeautifulSoup(html, features="html.parser")
    a_list = a_bf.find_all("a")
    url_list = set()
    for a_obj in a_list:
        if (a_obj != NULL and 'bpfilter' in a_obj.attrs.keys()
                and 'href' in a_obj.attrs.keys() and len(a_obj['href']) >= 30):
            url_list.add(a_obj['href'].replace(r'\/', '/'))
    return list(url_list)


def preprocess(html):
    rst = re.compile('<div class=.{0,4}WB_text W_f14.*?div>')  #非贪婪模式
    result = rst.findall(html)
    html_res = "\n".join(result)
    html_res = html_res.replace('\\', '')
    html_res = re.sub("<a.*?a>", '', html_res, 0)  #去掉链接
    return html_res


#获取所有帖子正文
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
    print(len(UrlList))
    for i in UrlList:
        print(i)
    page = 2
    #while(page<)
    #预处理及提取
    html = str(res_doc)
    out.write(html)
    html_res = preprocess(html)
    list = getText(html_res)
    print(len(list))
    index = 1
    for i in list:
        print(index, file=file)
        index += 1
        print(i, file=file)
        print('\n', file=file)
    file.close()
    out.close()
    #print(html_res)