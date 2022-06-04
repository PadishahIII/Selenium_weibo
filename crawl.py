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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from pymysql import NULL
import time
from types import NoneType
import pymysql
import logging
import datetime
import dateutil.relativedelta


#不超过200字
def SentimentAnalysis(text):
    try:
        cred = credential.Credential("AKIDc5kHYZJ9k47uQgfNozuZx5xZv5yZuymJ",
                                     "HH2WjgNnxqTqwmCQN3SbT4ORDiwGK7ds")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

        req = models.SentimentAnalysisRequest()
        params = {"Text": text, "Mode": "2class"}
        req.from_json_string(json.dumps(params))

        resp = client.SentimentAnalysis(req)
        obj = json.loads(resp.to_json_string())

        return obj['Sentiment'], obj['Positive'], obj['Negative']

    except TencentCloudSDKException as err:
        print(err)


#   情感分析：
#    1 非常积极 高于0.7
#    2 比较积极 高于0.55
#    3 喜忧参半 0.45-0.55
#    4 比较消极
#    5 超级消极


def getSentimentResult(text):
    if (text == NULL or text == None or len(text) < 1):
        return -1
    positive_list = []
    negative_list = []
    num = 0
    step = 200
    try:
        if (len(text) <= step):
            sentiment, positive, negative = SentimentAnalysis(text)
            positive_list.append(positive)
            negative_list.append(negative)
            num += 1
        else:
            for i in range(0, len(text) - step + 1, step):
                sentiment, positive, negative = SentimentAnalysis(
                    text[i:min(i + step,
                               len(text) - 1)])
                positive_list.append(positive)
                negative_list.append(negative)
                num += 1
        positive_sum = 0
        negative_sum = 0
        for i in range(0, num):
            positive_sum += positive_list[i]
            negative_sum += negative_list[i]
        positive_avg = positive_sum / num
        negative_avg = negative_sum / num
        standard = [0.55, 0.7]
        if (positive_avg >= 0.5):
            if (positive_avg <= standard[0]):
                return 3
            if (positive_avg <= standard[1]):
                return 2
            else:
                return 1
        else:
            if (negative_avg <= standard[0]):
                return 3
            if (negative_avg <= standard[1]):
                return 4
            else:
                return 5
    except Exception as e:
        print(e)


#提取关键词
#text不超过10000个字符
def getTopic(text):
    if (text == None or len(text) <= 0):
        return None
    try:
        cred = credential.Credential("AKIDc5kHYZJ9k47uQgfNozuZx5xZv5yZuymJ",
                                     "HH2WjgNnxqTqwmCQN3SbT4ORDiwGK7ds")
        httpProfile = HttpProfile()
        httpProfile.endpoint = "nlp.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = nlp_client.NlpClient(cred, "ap-guangzhou", clientProfile)

        req = models.KeywordsExtractionRequest()
        params = {"Text": text}
        req.from_json_string(json.dumps(params))

        resp = client.KeywordsExtraction(req)

        word_list = list()
        json_obj = json.loads(resp.to_json_string())
        for obj in json_obj.get('Keywords'):
            word_list.append(obj['Word'])
        return word_list

    except TencentCloudSDKException as err:
        print(err)


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
    if (text == NULL or text == None or len(text) < 1):
        return dict()
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
            if (word_obj['Pos'] != 'n' or len(word_obj['Word']) < 2):
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

    #WEBDRIVER:True开启浏览器
    def __init__(self, WEBDRIVER):
        #数据库连接
        self.conn = pymysql.connect(host='localhost',
                                    user='root',
                                    password='914075',
                                    db='WeiBo_HIT_DB',
                                    charset='utf8mb4')
        logging.info("Mysql Connected")
        self.cur = self.conn.cursor()
        self.out = open("test", "w", encoding="utf8", errors='replace')

        if (WEBDRIVER):
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

    def BuildSentiment(self, TblName, mode):
        update_sql = "update " + TblName + " set sentiment={0} where id={1};"
        select_text_sql = "select id,text from " + TblName + ";"
        select_senti_sql = "select sentiment from " + TblName + " where id={0};"

        try:
            res = self.cur.execute(select_text_sql)
            id_text_list = self.cur.fetchall()

            done_num = 0
            have_done_num = 0
            for i in range(0, len(id_text_list)):
                select_res = self.cur.execute(
                    select_senti_sql.format(str(id_text_list[i][0])))
                topic_res = self.cur.fetchone()
                if (mode != 'update' and select_res > 0 and topic_res != None
                        and topic_res[0] != None and len(topic_res[0]) > 0):
                    #已经做过情感分析了
                    have_done_num += 1
                    continue

                sentiment = getSentimentResult(id_text_list[i][1])
                if (sentiment == None or sentiment <= 0):
                    logging.error(
                        "Error code 2 when build sentiment:Invaild text")
                    continue

                res_ = self.cur.execute(
                    update_sql.format(str(sentiment), str(id_text_list[i][0])))
                self.conn.commit()
                done_num += 1
                print("已完成:" + str(i))
            logging.info("完成对表" + TblName + "的情感分析,共进行了" + str(done_num) +
                         "次" + ",跳过" + str(have_done_num) + "条元组")
        except Exception as e:
            logging.exception(e)

    #对正文提取出关键词
    def BuildTopic(self, TblName, mode):
        update_topic_sql = "update " + TblName + " set topic='{0}' where id={1};"
        select_text_sql = "select id,text,mid from " + TblName + ";"
        select_topic_sql = "select topic from " + TblName + " where mid='{0}'"

        try:
            res = self.cur.execute(select_text_sql)
            id_text_list = self.cur.fetchall()

            done_num = 0
            have_done_num = 0
            for i in range(0, len(id_text_list)):
                select_res = self.cur.execute(
                    select_topic_sql.format(id_text_list[i][2]))
                topic_res = self.cur.fetchone()
                if (mode != 'update' and select_res > 0 and topic_res != None
                        and topic_res[0] != None and len(topic_res[0]) > 0):
                    #已经分过词了
                    have_done_num += 1
                    continue

                topic_list = getTopic(id_text_list[i][1])
                if (topic_list == None):
                    continue

                topic_str = ','.join(topic_list)
                res_ = self.cur.execute(
                    update_topic_sql.format(topic_str,
                                            str(id_text_list[i][0])))
                self.conn.commit()
                done_num += 1
                print("已完成:" + str(i))
            logging.info("完成对表" + TblName + "的话题关键词提取,共进行了" + str(done_num) +
                         "次" + ",跳过" + str(have_done_num) + "条元组")
        except Exception as e:
            logging.exception(e)

    #维护话题关键词与微博mid之间的关系
    def BuildTopicList(self, mode):
        get_mid_topic_sql = "select mid,topic from alldata;"
        query_topic_sql = "select topic from topic_list where topic='{0}';"
        get_mid_list_sql = "select mid_list from topic_list where topic='{0}';"
        insert_topic_sql = "insert into topic_list (topic,mid_list) values ('{0}',\"{1}\");"
        update_topic_sql = "update topic_list set mid_list=\"{0}\" where topic='{1}';"
        update_mode_sql = "update topic_list set mid_list='' where true;"

        def Insert(topic, mid_list):
            mid_list = mid_list.replace('\"', "'")  #统一单双引号
            res = self.cur.execute(insert_topic_sql.format(topic, mid_list))
            self.conn.commit()

        def Update(topic, mid_list):
            mid_list = mid_list.replace('\"', "'")
            res = self.cur.execute(update_topic_sql.format(mid_list, topic))
            self.conn.commit()

        def GetMidListCount(topic):
            res = self.cur.execute(get_mid_list_sql.format(topic))
            midlist_list = self.cur.fetchone()
            midlist_str = midlist_list[0]
            if (len(midlist_str) <= 0):
                mid_list = []
            else:
                mid_list = midlist_str.split(',')
            return mid_list

        if (mode == 'update'):
            res_update_mode = self.cur.execute(update_mode_sql)

        update_cnt = 0  #更新的关键词
        insert_cnt = 0  #新建的关键词
        text_cnt = 0  #处理的帖子数
        topic_cnt = 0  #处理的关键词数

        res_mid_topic = self.cur.execute(get_mid_topic_sql)
        mid_topic_list = self.cur.fetchall()
        if (res_mid_topic <= 0 or mid_topic_list == None
                or len(mid_topic_list) <= 0 or mid_topic_list[0] == None):
            logging.error("None result when fetch keywords,SQL:" +
                          get_mid_topic_sql)
            return
        for mid_keywords in mid_topic_list:
            text_cnt += 1
            topic_str = mid_keywords[1]
            mid = mid_keywords[0]

            if (topic_str == None or mid == None or len(topic_str) <= 0
                    or len(mid) <= 0):
                continue

            topic_list = topic_str.split(',')
            if (topic_list == None):
                continue
            for topic in topic_list:
                if (topic == ''):
                    continue
                topic_cnt += 1
                print(topic_cnt)
                res_query_keyword = self.cur.execute(
                    query_topic_sql.format(topic))
                if (res_query_keyword <= 0):
                    #新建关键词
                    mid_list = list()
                    mid_list.append(mid)
                    midlist_str = ','.join(mid_list)
                    Insert(topic, midlist_str)
                    insert_cnt += 1
                else:
                    #更新mid list 和频次
                    mid_list = GetMidListCount(topic)
                    if (mid_list == None):
                        logging.error(
                            "Error code 1 when fetch mid_list, mid=" + mid)
                        continue
                    if (mid in mid_list):
                        pass
                    else:
                        mid_list.append(mid)
                        midlist_str = ','.join(mid_list)
                        Update(topic, midlist_str)
                        update_cnt += 1
        logging.info("记录一次topic_list的维护,更新了" + str(update_cnt) + "条关键词元组," +
                     "新建" + str(insert_cnt) + "条关键词元组," + "共处理" +
                     str(text_cnt) + "条帖子的" + str(topic_cnt) + "个关键词")
        return

    #维护 关键词与mid_list之间的映射 只考虑正文，不包含评论
    def BuildKeywordsList(self, mode):
        get_mid_keywords_sql = "select mid,keywords from alldata;"
        query_keyword_sql = "select keyword from keywords_list where keyword='{0}';"
        get_mid_list_count_sql = "select mid_list,count from keywords_list where keyword='{0}';"
        insert_keyword_sql = "insert into keywords_list (keyword,mid_list,count) values ('{0}',\"{1}\",{2});"
        update_keyword_sql = "update keywords_list set mid_list=\"{0}\",count={1} where keyword='{2}';"
        update_mode_sql = "update keywords_list set mid_list='' where true;"

        def Insert(keyword, mid_list, count):
            mid_list = mid_list.replace('\"', "'")  #统一单双引号
            res = self.cur.execute(
                insert_keyword_sql.format(keyword, mid_list, str(count)))
            self.conn.commit()

        def Update(keyword, mid_list, count):
            mid_list = mid_list.replace('\"', "'")
            res = self.cur.execute(
                update_keyword_sql.format(mid_list, str(count), keyword))
            self.conn.commit()

        def GetMidListCount(keyword):
            res = self.cur.execute(get_mid_list_count_sql.format(keyword))
            midlist_count_list = self.cur.fetchone()
            if (res <= 0 or midlist_count_list == None
                    or len(midlist_count_list) <= 0
                    or midlist_count_list[0] == None):
                return None, None
            else:
                mid_list_str = midlist_count_list[0]  #TODO:
                count = midlist_count_list[1]
                if (len(mid_list_str) <= 0):
                    mid_list = []
                else:
                    mid_list = mid_list_str.split(',')
                return mid_list, count

        if (mode == 'update'):
            res_update_mode = self.cur.execute(update_mode_sql)

        update_cnt = 0  #更新的关键词
        insert_cnt = 0  #新建的关键词
        text_cnt = 0  #处理的帖子数
        keyword_cnt = 0  #处理的关键词数

        res_mid_keywords = self.cur.execute(get_mid_keywords_sql)
        mid_keywords_list = self.cur.fetchall()
        if (res_mid_keywords <= 0 or mid_keywords_list == None
                or len(mid_keywords_list) <= 0
                or mid_keywords_list[0] == None):
            logging.error("None result when fetch keywords,SQL:" +
                          get_mid_keywords_sql)
            return
        for mid_keywords in mid_keywords_list:
            text_cnt += 1
            keywords_str = mid_keywords[1]
            mid = mid_keywords[0]

            if (keywords_str == None or mid == None or len(keywords_str) <= 0
                    or len(mid) <= 0):
                continue

            keywords_obj = json.loads(keywords_str)
            if (keywords_obj == None):
                continue
            for keyword in keywords_obj.keys():
                keyword_cnt += 1
                print(keyword_cnt)
                res_query_keyword = self.cur.execute(
                    query_keyword_sql.format(keyword))
                if (res_query_keyword <= 0):
                    #新建关键词
                    mid_list = list()
                    mid_list.append(mid)
                    mid_list_str = ','.join(mid_list)
                    count = keywords_obj.get(keyword)
                    Insert(keyword, mid_list_str, count)
                    insert_cnt += 1
                else:
                    #更新mid list 和频次
                    mid_list, count = GetMidListCount(keyword)
                    if (mid_list == None or count == None):
                        logging.error(
                            "Error code 0 when fetch mid_list and count, mid="
                            + mid)
                        continue
                    if (mid in mid_list):
                        pass
                    else:
                        mid_list.append(mid)
                        mid_list_str = ','.join(mid_list)
                        count += keywords_obj.get(keyword)
                        Update(keyword, mid_list_str, count)
                        update_cnt += 1
        logging.info("记录一次keywords_list的维护,更新了" + str(update_cnt) + "条关键词元组," +
                     "新建" + str(insert_cnt) + "条关键词元组," + "共处理" +
                     str(text_cnt) + "条帖子的" + str(keyword_cnt) + "个关键词")
        return

    #统计关键词频率
    #mode :update 重置
    def BuildKeywordsStatistic(self, TblName, start_time_str, end_time_str,
                               months, mode):
        get_max_id_sql = "select max(id) from keywords_statistic;"
        get_keywords_sql = "select keywords from " + TblName + " where date between '{0}' and '{1}';"
        query_keywords_sql = "select id from keywords_statistic where start_date between '{0}' and '{1}';"
        insert_keywords_sql = "insert into keywords_statistic (id,start_date,end_date,keywords_frequency)values({0},'{1}','{2}','{3}');"
        update_keywords_frequency_sql = "update keywords_statistic set keywords_frequency='{0}' where id={1};"
        get_keywords_frequency_sql = "select keywords_frequency from keywords_statistic where id={0};"
        update_mode_sql = "update keywords_statistic set keywords_frequency='{}' where true;"

        if (mode == 'update'):
            res_update_mode = self.cur.execute(update_mode_sql)

        update_cnt = 0  #更新的元组个数
        insert_cnt = 0  #新建的元组个数
        #try:
        #获取下一个id
        res_id = self.cur.execute(get_max_id_sql)
        id_list = self.cur.fetchone()
        id = 0
        if (res_id <= 0 or id_list == None or len(id_list) <= 0
                or id_list[0] == None):
            id = 0
        else:
            id = int(id_list[0])
        next_id = id + 1

        #start_time_str = "2019-01-01"
        #end_time_str = "2022-04-01"
        time_obj = datetime.datetime.strptime(start_time_str, "%Y-%m-%d")
        delta = dateutil.relativedelta.relativedelta(months=months)
        while (time.mktime(time_obj.timetuple()) <= time.mktime(
                time.strptime(end_time_str, "%Y-%m-%d"))):
            #try:
            #月底
            endOfMonth = time_obj + delta - datetime.timedelta(days=1)
            res_get_keywords = self.cur.execute(
                get_keywords_sql.format(str(time_obj), str(endOfMonth)))
            keywords_list = self.cur.fetchall()  #需要统计的元组
            logging.info(
                "SQL:" +
                get_keywords_sql.format(str(time_obj), str(endOfMonth)))
            if (res_get_keywords > 0 and keywords_list != None
                    and len(keywords_list) > 0):
                exec_id = 0  #要更新的频率元组的id
                #查询该时间段的统计元组是否已经建立
                res_query_keywords = self.cur.execute(
                    query_keywords_sql.format(str(time_obj), str(endOfMonth)))
                if (res_query_keywords <= 0):
                    #建立元组
                    res_insert = self.cur.execute(
                        insert_keywords_sql.format(
                            str(next_id), time_obj.strftime("%Y-%m-%d"),
                            endOfMonth.strftime("%Y-%m-%d"), '{}'))
                    self.conn.commit()
                    exec_id = next_id  #在新元组上更新
                    next_id += 1
                    insert_cnt += 1
                else:
                    query_keywords_list = self.cur.fetchone()
                    if (query_keywords_list != None):
                        exec_id = query_keywords_list[0]  #在已有的元组上更新
                        update_cnt += 1

                #取出之前的统计结果
                res_get_keywords_frequency = self.cur.execute(
                    get_keywords_frequency_sql.format(str(exec_id)))
                get_keywords_frequency_list = self.cur.fetchone()
                keywords_frequency_obj = NULL  #待更新的频率元组
                if (get_keywords_frequency_list != None):
                    keywords_frequency_str = get_keywords_frequency_list[0]
                    try:
                        keywords_frequency_obj = json.loads(
                            keywords_frequency_str)
                    except Exception as e:
                        logging.error("Invaild DB data:'" +
                                      keywords_frequency_str + "' id=" +
                                      str(exec_id))
                        logging.exception(e)
                #更新
                for i in range(0, len(keywords_list)):
                    for keywords_str in keywords_list[i]:
                        keywords_obj = json.loads(keywords_str)
                        if (keywords_obj == None):
                            continue
                        for key in keywords_obj.keys():
                            if (key in keywords_frequency_obj.keys()):
                                keywords_frequency_obj[key] += keywords_obj[
                                    key]
                            else:
                                keywords_frequency_obj[key] = keywords_obj[key]
                #写回数据库
                res_update_keywords_frequency_sql = self.cur.execute(
                    update_keywords_frequency_sql.format(
                        json.dumps(keywords_frequency_obj, ensure_ascii=False),
                        str(exec_id)))
                self.conn.commit()

                #时间增长
            time_obj = time_obj + delta
        logging.info("统计关键词频率,更新元组个数:" + str(update_cnt) + ",新建元组个数:" +
                     str(insert_cnt) + ",时间区间:" + start_time_str + " to " +
                     end_time_str)
        #except Exception as e:
        #    logging.exception(e)
        #except Exception as e:
        #    logging.exception(e)


#    def BuildCommentsKeywords(self, TblName, mode):
#        update_keyword_sql = "update " + TblName + " set keywords='{0}' where id='{1}';"
#        select_text_sql = "select id,text from " + TblName + ";"
#        select_keywords_sql = "select keywords from " + TblName + " where id='{0}'"
#
#        res = self.cur.execute(select_text_sql)  #TODO:

#对正文分词
#mode:update 重新分词

    def BuildKeywords(self, TblName, mode):
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
                if (mode != 'update' and select_res > 0
                        and keywords_res != None and len(keywords_res[0]) > 0):
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

    #评论爬虫
    def scrapy_comments(self, target_base, TblName, mode):
        get_all_mid_sql = "select mid from alldata;"
        insert_comment_sql = "insert into " + TblName + " (id,mid,text,username,face)values('{0}','{1}','{2}','{3}','{4}');"
        query_id_sql = "select id from " + TblName + " where id='{0}'"
        update_sql = "update " + TblName + " set text='{0}',username='{1}',face='{2}' where id='{3}';"

        def Insert(id, mid, text, username, face):
            res = self.cur.execute(
                insert_comment_sql.format(id, mid, text, username, face))
            self.conn.commit()

        def Update_Flush(id, mid, text, username, face):
            res = self.cur.execute(query_id_sql.format(id))
            res_list = self.cur.fetchall()
            if (res > 0 and res_list != None and len(res_list) > 0
                    and res_list[0] != None):
                if (mode == 'flush'):
                    flush_res = self.cur.execute(
                        update_sql.format(text, username, face, id))
                    self.conn.commit()
                    return True
                return False
            else:
                Insert(id, mid, text, username, face)
                return True

        def request_comment(mid):
            res = request.Request(target_base.format(mid))
            response = request.urlopen(res)
            res_doc = response.read()
            data_str = res_doc.decode('utf8', 'ignore')
            data_obj = json.loads(data_str)
            if (data_obj != None and 'comments' in data_obj.keys()):
                logging.info("Request comment of " + mid + ", response code " +
                             str(response.getcode()) + ", counts: " +
                             str(len(data_obj['comments'])))
                return data_obj
            else:
                logging.error("Failed to request comment of " + mid +
                              ", response data:" + "\n\t\t\t" + data_str)
                return None

        comments_num = 0
        res_mid = self.cur.execute(get_all_mid_sql)
        mid_list = self.cur.fetchall()
        if (res_mid <= 0 or mid_list == None or len(mid_list) <= 0
                or mid_list[0] == None):
            logging.error("None mid list when execute SQL " + get_all_mid_sql)
            return
        for mid in mid_list:
            data_obj = request_comment(mid[0])
            comments_num += len(data_obj['comments'])
            for arr in data_obj['comments']:
                text = arr['text']
                id = arr['idstr']
                username = arr['user']['name']
                face = arr['user']['profile_image_url']

                text = self.preprocess_comments(text)
                Update_Flush(id, mid[0], text, username, face)
                print("comment_num:" + str(comments_num))
            time.sleep(10)

        logging.info("共更新" + str(comments_num) + "条评论")

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
            res_list = self.cur.fetchall()
            if (res > 0 and res_list != None and len(res_list) > 0
                    and res_list[0] != None):
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

        res_id = self.cur.execute(get_max_id_sql)
        id_list = self.cur.fetchone()
        if (res_id <= 0 or id_list == None or len(id_list) <= 0
                or id_list[0] == None):
            id = 1
        else:
            id = id_list[0] + 1
        true_id = id  #id=1是测试元组
        text_cnt = 0  #新加入的帖子数
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
                            text_cnt += 1

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

        logging.info("记录对" + target_first + "的一次爬取，新加入" + str(text_cnt) +
                     "条帖子")
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

    def preprocess_comments(self, data):
        data_res = re.sub("^回复@.*?:", '', data, 0)
        data_res = ''.join(x for x in data_res if x.isprintable())
        return data_res

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

    #cookie_str = "SINAGLOBAL=2012260830470.789.1652279835753; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFTCEhVX8PyDSbzM9fNdvH85JpX5KMhUgL.Fo-NS0BEeK2f1hn2dJLoIEBLxKqLBozL1K5LxKnL12BLB.eLxK-LBo5L12qLxK-L1hqLBoMt; PC_TOKEN=f537443d32; ALF=1685856098; SSOLoginState=1654320100; SCF=AtLJ0ZM7dPtydutgQFGH2sx9Z-clxSbtt5worLTD6UKvXYgodzu67s0wCwcTdX5dOi_-v1Gib6jG20PXrpVY6ec.; SUB=_2A25Pnpu1DeThGeNJ7FYT8S_JwzSIHXVs7Yp9rDV8PUNbmtANLWfkkW9NS7N3VgQYhOr5UmYz5OTXJY5oLBVUxfAa; XSRF-TOKEN=0Bu_X36L91O6uHXgZm5vAuyI; WBPSESS=TlDwwucyEECKkCVNMnOgDCUsjPrxBSPv6-c3l-ry9u9-ZHBNYYmN_TRFpR7XZq9r59DJ9EF331uu4nyZDIBNpecJqT6NhB98cGGECFxtPGw4mLEzUVLEqX8QfPptJ902BC_3GlFqnVX7IxhbVre5CA==; _s_tentry=weibo.com; Apache=4228646352087.906.1654320113866; ULV=1654320113941:10:2:2:4228646352087.906.1654320113866:1654167086306; wb_view_log_5774211588=1536*8641.25; webim_unReadCount=%7B%22time%22%3A1654320122166%2C%22dm_pub_total%22%3A23%2C%22chat_group_client%22%3A0%2C%22chat_group_notice%22%3A0%2C%22allcountNum%22%3A47%2C%22msgbox%22%3A0%7D"
    ##'哈工大'超话
    #target_url = "https://weibo.com/p/100808ec2f8f02483cbf2206505d27f9ffb3c1/super_index?sudaref=weibo.com"
    ##'哈尔滨工业大学'超话
    #target_url2 = "https://weibo.com/p/100808c4afb07615e340a55ff32c5aaa8e47a5/super_index"
    Crawler = crawler(None)
    ##Crawler.scrapy_chaohua(target_url, cookie_str,'chaohuadata', 'insertmid')
    ##Crawler.alterLogFile("test2")
    #Crawler.scrapy_chaohua(target_url, cookie_str, 'chaohuadata',
    #                       'update')  #对已经存在数据库中的帖子不做处理，存储新爬到的帖子
    #Crawler.BuildKeywords('chaohuadata', '')  #对新加入的帖子分词
    ##Crawler.BuildKeywords('chaohuadata2', 'update')
    #Crawler.BuildTopic('chaohuadata', '')
    #Crawler.BuildTopic('chaohuadata2', '')

    #Crawler.BuildKeywordsStatistic('chaohuadata', '2019-07-01', '2022-04-01',
    #                               1, '')
    #Crawler.BuildKeywordsStatistic('chaohuadata2', '2019-07-01', '2022-04-01',
    #                               1, '')
    #target_base = "https://api.weibo.com/2/comments/show.json?access_token=2.00yMAmSG0NzCoG7969bfecd0mHIdlC&id={0}"
    #Crawler.scrapy_comments(target_base, 'comments', 'update')
    #Crawler.BuildKeywordsList('')
    #Crawler.BuildTopicList('')
    #Crawler.BuildSentiment('chaohuadata', '')
    Crawler.BuildSentiment('chaohuadata2', '')
