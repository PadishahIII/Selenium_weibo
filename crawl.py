from codecs import utf_16_be_decode
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.nlp.v20190408 import nlp_client, models
import json
import re
import selenium
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib.request as request
import json
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pymysql import NULL
import time
from types import NoneType
import pymysql
import logging


#长度要小于500字,utf8格式
def LexicalAnalysis(text):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户secretId，secretKey,此处还需注意密钥对的保密
        cred = credential.Credential("AKIDc5kHYZJ9k47uQgfNozuZx5xZv5yZuymJ",
                                     "HH2WjgNnxqTqwmCQN3SbT4ORDiwGK7ds")

        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

        req = models.LexicalAnalysisRequest()
        params = {"Text": text}
        req.from_json_string(json.dumps(params))

        cnt = 0
        while (cnt < 4):
            resp = client.LexicalAnalysis(req)
            json_obj = json.loads(resp.to_json_string())
            nerlist = json_obj['NerTokens']
            poslist = json_obj['PosTokens']
            if (nerlist == NoneType or poslist == NoneType):
                cnt += 1
                continue
            else:
                return nerlist, poslist

    except TencentCloudSDKException as err:
        logging.exception(err)


#对任意长度文本分词
def getKeywords(text):
    keywords_list = dict()
    NerToken_list = []
    PosToken_list = []  #分词及词性
    try:
        if (len(text) <= 500):
            NerToken_list, PosToken_list = LexicalAnalysis(text)
        else:
            for i in range(0, len(text) - 499, 500):
                nl, pl = LexicalAnalysis(text[i:min(i + 500, len(text) - 1)])
                NerToken_list.extend(nl)
                PosToken_list.extend(pl)
        for word_obj in PosToken_list:
            if (word_obj['Pos'] != 'n'):
                continue
            if (word_obj['Word'] in keywords_list.keys()):
                keywords_list[word_obj['Word']] = keywords_list.get(
                    word_obj['Word']) + 1
            else:
                keywords_list[word_obj['Word']] = 1
        return keywords_list
    except Exception as e:
        print(e)


class crawler:

    def __init__(self):
        #数据库连接
        self.conn = pymysql.connect(host='localhost',
                                    user='root',
                                    password='914075',
                                    db='WeiBo_HIT_DB',
                                    charset='utf8mb4')
        logging.info("Mysql Connected")
        self.cur = self.conn.cursor()
        self.out = open("test", "w", encoding="utf8", errors='replace')

        #初始化WebDriver
        option = webdriver.EdgeOptions()
        option.add_argument("headless")
        #option.add_argument("Accept-Charset:utf-8")
        self.driver = webdriver.Edge(options=option)

        self.filter_list_chaohua = [
            '哈工大超话', '哈尔滨工业大学超话', '展开全文c', '展开全文', '收起全文d', '收起全文'
        ]
        self.filter_list_search = []

    def alterLogFile(self, filepath):
        self.out.close()
        self.out = open(filepath, "w", encoding="utf8", errors="replace")

    #对正文分词
    def BuildKeywords(self, TblName):
        update_keyword_sql = "update " + TblName + " set keywords='{0}' where id={1};"
        select_text_sql = "select id,text,mid from " + TblName + ";"
        select_keywords_sql = "select keywords from " + TblName + " where mid='{0}'"

        try:
            res = self.cur.execute(select_text_sql)
            id_text_list = self.cur.fetchall()

            done_num = 0
            have_done_num = 0
            for i in range(1, len(id_text_list)):
                select_res = self.cur.execute(
                    select_keywords_sql.format(id_text_list[i][2]))
                keywords_res = self.cur.fetchone()
                if (select_res > 0 and keywords_res != None
                        and len(keywords_res[0]) > 0):
                    #已经分过词了
                    have_done_num += 1
                    continue

                keywords_dict = getKeywords(id_text_list[i][1])

                json_str = json.dumps(keywords_dict, ensure_ascii=False)
                res_ = self.cur.execute(
                    update_keyword_sql.format(json_str,
                                              str(id_text_list[i][0])))
                self.conn.commit()
                done_num += 1
                print("已完成:" + str(i))
            logging.info("完成对表" + TblName + "的分词,共进行了" + str(done_num) + "次" +
                         ",跳过" + str(have_done_num) + "条元组")
        except Exception as e:
            logging.exception(e)

    #超话爬虫
    #mode：update
    def scrapy_chaohua(self, target_first, cookie_str, TblName, mode):
        get_max_id_sql = "select max(id) from " + TblName + ";"
        insert_sql = "insert into " + TblName + " (id,date,nickname,comment_num,favour_num,text,face,share_num,mid)values({0},'{1}','{2}',{3},{4},'{5}','{6}',{7},'{8}');"
        update_face_share_sql = "update " + TblName + " set face='{0}',share_num={1} where id={2};"
        update_mid_sql = "update " + TblName + " set mid='{0}' where id={1};"
        update_full_sql = "update " + TblName + " set date='{0}',nickname='{1}',comment_num={2},favour_num={3},text='{4}',face='{5}',share_num={6},mid='{7}' where id={8};"
        query_mid_sql = "select mid from " + TblName + " where mid='{0}'"

        def Insert(id, date, nickname, comment_num, favour_num, text, face,
                   share_num, mid):
            res = self.cur.execute(
                insert_sql.format(id, date, nickname, comment_num, favour_num,
                                  text, face, share_num, mid))
            self.conn.commit()
            #log

        #True:插入了新数据
        def Update_Mode(id, date, nickname, comment_num, favour_num, text,
                        face, share_num, mid):
            res = self.cur.execute(query_mid_sql.format(mid))
            if (res > 0):
                #更新评论
                return False
            else:
                Insert(id, date, nickname, comment_num, favour_num, text, face,
                       share_num, mid)
                self.conn.commit()
                return True

        def UpdateFaceShare(id, face, share_num):
            res = self.cur.execute(
                update_face_share_sql.format(face, share_num, id))
            self.conn.commit()

        def UpdateMID(id, mid):
            res = self.cur.execute(update_mid_sql.format(mid, id))
            self.conn.commit()

        def UpdateFull(id, date, nickname, comment_num, favour_num, text, face,
                       share_num, mid):
            res = self.cur.execute(
                update_full_sql.format(date, nickname, comment_num, favour_num,
                                       text, face, share_num, mid, id))
            self.conn.commit()

        #获取超话首页
        self.driver.get(target_first)
        #添加cookie(每天要通过burp更新)
        cookie_list = crawler.getDictCookie(cookie_str)
        for cookie in cookie_list:
            self.driver.add_cookie(cookie)
        self.driver.get(target_first)
        self.driver.refresh()

        self.driver.maximize_window()

        self.cur.execute(get_max_id_sql)
        id = self.cur.fetchone()[0] + 1
        true_id = 2  #id=1是测试元组
        page_num = 1
        while (page_num < 2):
            for i in range(10):  #滚动若干次
                js = "window.scrollTo(0,document.body.scrollHeight);"
                self.driver.execute_script(js)
                time.sleep(2)
                try:
                    page_btn = self.driver.find_elements_by_class_name(
                        'W_pages')
                    if (len(page_btn) <= 0):
                        continue
                    else:
                        break
                except:
                    break

            for ele in self.driver.find_elements_by_partial_link_text("展开全文"):
                self.driver.execute_script("arguments[0].click();", ele)
                time.sleep(2)

            html = self.driver.page_source
            nickname_list, date_list, text_list, statistic_list, face_list, mid_list = self.getAllData_Chaohua(
                html)

            #写入数据库
            logging.info("Page:" + str(page_num) + ";帖子数:" +
                         str(len(text_list)))
            try:
                for i in range(0, len(nickname_list)):
                    if (mode == 'insertfs'):
                        UpdateFaceShare(str(true_id), face_list[i],
                                        statistic_list[i][0])
                    elif (mode == 'insertmid'):
                        UpdateMID(str(true_id), mid_list[i])
                    elif (mode == 'update'):
                        res = Update_Mode(str(true_id), date_list[i],
                                          nickname_list[i],
                                          statistic_list[i][1],
                                          statistic_list[i][2], text_list[i],
                                          face_list[i], statistic_list[i][0],
                                          mid_list[i])
                        if (res):
                            true_id += 1

            except Exception as e:
                logging.exception(e)

            try:
                next_page_btn = self.driver.find_element_by_link_text('下一页')
                if (next_page_btn != NULL and next_page_btn != NoneType):
                    #next_page_btn.click()
                    self.driver.execute_script("arguments[0].click();",
                                               next_page_btn)
                    time.sleep(2)
                    page_num += 1
                else:
                    break
            except Exception as e:
                logging.exception(e)
                break

        return

    #搜索爬虫 TODO
    def scrapy_search(self, cookie_str):
        get_max_id_sql = "select max(id) from SearchData;"
        insert_sql = "insert into SearchData (id,date,nickname,comment_num,favour_num,text)values({0},'{1}','{2}',{3},{4},'{5}');"

        def Insert(id, date, nickname, comment_num, favour_num, text):
            res = self.cur.execute(
                insert_sql.format(id, date, nickname, comment_num, favour_num,
                                  text))
            self.conn.commit()
            #log

    #构造cookie的关联数组
    @staticmethod
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

    #预处理
    def preprocess(self, html, filter_list):
        html_res = re.sub("<a.*?</a>", '', html, 0)  #去掉链接
        for i in filter_list:
            html_res = html_res.replace(i, '')
        html_res = ''.join(x for x in html_res
                           if x.isprintable())  #去除不可打印字符如\u200b
        return html_res

    #提取每个帖子的时间、昵称、正文 TODO:评论
    def getAllData_Chaohua(self, html):
        WB_box_bf = BeautifulSoup(html, features="html.parser")
        WB_box_list = WB_box_bf.find_all(
            "div",
            class_=re.compile(
                "WB_cardwrap WB_feed_type S_bg2( WB_feed_vipcover)? WB_feed_like"
            ))
        nickname_list = []  #昵称
        date_list = []  #帖子的时间
        text_list = []  #正文
        statistic_list = []  #转发数、评论数、点赞数
        face_list = []  #头像url
        mid_list = []  #微博ID，用于获取评论

        for WB_box in WB_box_list:
            WB_detail_bf = BeautifulSoup(str(WB_box))
            WB_detail = WB_detail_bf.find_all("div", class_="WB_detail")  #正文
            WB_handle = WB_detail_bf.find_all("div",
                                              class_="WB_handle")  #评论、点赞
            WB_face = WB_detail_bf.find_all("div", class_="face")

            WB_info_bf = BeautifulSoup(str(WB_detail))

            WB_info_list = WB_info_bf.find_all("div", class_="WB_info")
            WB_from_S_txt2_list = WB_info_bf.find_all("div",
                                                      class_="WB_from S_txt2")
            WB_text_W_f14_list = WB_info_bf.find_all("div",
                                                     class_="WB_text W_f14")

            a_nickname_bf = BeautifulSoup(str(WB_info_list[0]))
            a_date_bf = BeautifulSoup(str(WB_from_S_txt2_list[0]))

            a_nickname_list = a_nickname_bf.find_all("a")
            a_date_list = a_date_bf.find_all("a")

            span_bf = BeautifulSoup(str(WB_handle))
            span = span_bf.find_all("span", class_="line S_line1")
            em_reg = re.compile("<em>(.+?)</em>")

            face_bf = BeautifulSoup(str(WB_face))
            img_list = face_bf.find_all("img")
            if (len(img_list) > 0):
                if ("src" in img_list[0].attrs.keys()):
                    face_list.append(img_list[0].get('src'))

            if (len(span) >= 4):
                list = []
                for i in range(1, 4):
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
                        self.preprocess(
                            WB_text_W_f14_list[0].text.replace(' ', ''),
                            self.filter_list_chaohua))
                else:
                    for text in WB_text_W_f14_list:
                        if ("node-type" in text.attrs.keys()
                                and text.get('node-type')
                                == 'feed_list_content_full'):  #展开全文
                            text_list.append(
                                self.preprocess(text.text.replace(' ', ''),
                                                self.filter_list_chaohua))

            if ('mid' in WB_box.attrs.keys()
                    and WB_box.get('mid') != NoneType):
                mid_list.append(WB_box.get('mid'))
            else:
                logging.error("ERROR:None mid")

        return nickname_list, date_list, text_list, statistic_list, face_list, mid_list


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        filename="log",
        filemode="a",
        format=
        "%(asctime)s - %(name)s - %(levelname)-9s - %(filename)-8s : %(lineno)s line - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        encoding='utf8',
        errors='replace')

    cookie_str = "SINAGLOBAL=2012260830470.789.1652279835753; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; ALF=1684997462; SSOLoginState=1653461466; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvsewtZLk2xOuVl2j4iORn5uzK16U6V9zaT9CnJDRKtBU.; SUB=_2A25PiaGLDeThGeNJ7FYT8S_JwzSIHXVs_pRDrDV8PUNbmtB-LWnGkW9NS7N3VjzQnmRckTAv4w_I6mvEuD6oKo8g; XSRF-TOKEN=xHuC381rGgFVG5x4HQB6kHqL; _s_tentry=weibo.com; Apache=7682961489905.312.1653461481403; ULV=1653461481602:7:7:3:7682961489905.312.1653461481403:1653385987133; wb_view_log_5774211588=1536*8641.25; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9ruRLMs4Ikp4qjr8I_Em1omLVGMFb8LgbnSJz_lYqUmMrkwj-OV9wcv_9BVHDoO1FHMm33E-AlB5hZNEBSx-wRHQ==; webim_unReadCount=%7B%22time%22%3A1653474579408%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A44%2C%22msgbox%22%3A0%7D; PC_TOKEN=9834886566"
    #'哈工大'超话
    target_url = "https://weibo.com/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index?sudaref=weibo.com"
    #'哈尔滨工业大学'超话
    target_url2 = "https://weibo.com/p/100808c4afb07615e340a55ff32c5aaa8e47a5/super_index"
    Crawler = crawler()
    #Crawler.scrapy_chaohua(target_url, cookie_str,'chaohuadata', 'insertmid')
    #Crawler.alterLogFile("test2")
    #Crawler.scrapy_chaohua(target_url2, cookie_str, 'chaohuadata2', 'update')#对已经存在数据库中的帖子不做处理，存储新爬到的帖子
    #Crawler.BuildKeywords('chaohuadata')  #对新加入的帖子分词
