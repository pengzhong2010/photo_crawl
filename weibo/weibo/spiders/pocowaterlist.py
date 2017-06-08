# -*- coding:utf-8 -*-
import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
# from scrapy.http import HtmlResponse
import re
import time

from rec_driver import *
# from pyredis import RedisKv

from pymysql import PyMysql
import common

from pymongo import MongoClient


class PocowaterlistSpider(scrapy.spiders.Spider):
    name = "pocowaterlist"
    # allowed_domains = ['weibo.com', 'weibo.cn', 'sina.com.cn']
    # start_urls=['http://m.weibo.cn']
    # surl='http://photo.poco.cn/vision.htx&p=1&index_type=hot&tid=-1&gid=0'
    surl='http://photo.poco.cn/vision.htx&index_type=hot&tid=-1&gid=17#list'
    web_domain = 'http://photo.poco.cn'

    spider_sep_per_time=3600

    mydb_con = ''

    my_cookies = {}
    error_file_dir = ""
    error_file = ''
    cookies_user = conf1.MY_COOKIES1
    # appid=1287792
    iteminfo = {}

    def shell_init(self):
        self.error_file_dir = conf1.error_file_dir
        self.error_file = self.name + '_error'

    def start_requests(self):
        self.shell_init()
        cookies_list = common.read_cookie(self.name, self.cookies_user).split('; ')
        for i in cookies_list:
            tmp = i.split('=')

            k = tmp[0]

            v = tmp[1]

            self.my_cookies.setdefault(k, v)
        #
        # self.mydb_con = MongoClient("mongodb://"+conf1.MONGO_HOST+":"+str(conf1.MONGO_PORT))
        self.mydb_con = MongoClient(
            'mongodb://' + conf1.MONGO_USER + ':' + conf1.MONGO_PWD + '@' + conf1.MONGO_HOST + ':' + str(
                conf1.MONGO_PORT) + '/' + conf1.MONGO_DBNAME)

        self.mydb_db = self.mydb_con.photo
        self.collection = self.mydb_db.item

        # print self.my_cookies
        return [scrapy.Request(url=self.surl, meta={'cookiejar': 2}, cookies=self.my_cookies, callback=self.see_list
                               )]

    def see_list(self, response):
        # print 'url'
        # print response.url
        # print 'body'
        # print response.body
        # print 'headers'
        # print response.headers
        # print 'meta'
        # print response.meta
        # print 'cookies'
        # print type(response.request.headers.getlist('Cookie')[0])
        # print response.request.headers.getlist('Cookie')[0]
        # return

        # if not common.login_filter(self.error_file_dir, self.error_file, response.url):
        #     return

        next_cookie = response.request.headers.getlist('Cookie')[0]
        common.stay_cookie(self.name, next_cookie)
        cookies_list = next_cookie.split('; ')
        self.my_cookies = {}
        for i in cookies_list:
            tmp = i.split('=')

            k = tmp[0]

            v = tmp[1]

            self.my_cookies.setdefault(k, v)

        str = response.body

        # str.decode('UTF-8').encode('GBK')
        # with open('poco1', 'wb') as f:
        #     f.write(str)


        str1 = str.decode('GBK').encode('UTF-8')

        # with open('poco2', 'wb') as f:
        #     f.write(str1)
        # return

        # str1 = response.body
        # str1 = str1.replace('\r\n', '')
        # str1 = str1.replace('\t', '')
        # str1 = str1.replace('\\r\\n', '')
        # str1 = str1.replace('\\n', '')
        # str1 = str1.replace('\\t', '')

        # with open('commentlist1', 'wb') as f:
        #     f.write(str1)
        # return

        list1 = Selector(text=str1).xpath('//div[contains(@class, "mod-txtimg230-list")]/ul')
        # print len(list1)
        # print list1
        list2 = list1[0]
        # print list2
        list3 = list2.xpath('li')
        # print list3
        for index1, li1 in enumerate(list3):
            div_list = li1.xpath('div')
            # print div_list
            div1 = div_list[0]
            item_url = div1.xpath('a/@href').extract_first()
            # print item_url
            # return
            # item_url = item_url[0]
            item_img_main = div1.xpath('a/img/@src').extract_first()
            # item_img_main = item_img_main[0]
            # print item_url
            # print item_img_main
            # return
            div2 = div_list[1]
            list4 = div2.xpath('h4/a')
            a0 = list4[0]
            item_title = a0.xpath('span/text()').extract_first()
            # item_title = item_title[0]
            # print item_title
            # return
            a1 = list4[1]
            author_url = a1.xpath('@href').extract_first()
            # author_url = author_url[0]
            author_name = a1.xpath('text()').extract_first()
            # author_name = author_name[0]
            author_uid = a1.xpath('@data-usercard-uid').extract_first()
            # author_uid = author_uid[0]
            # print author_name
            # print author_uid
            # print author_url
            # return
            span_list = div2.xpath('p/span')
            browse_num=0
            vote_num=0
            comment_num=0
            for index2, span in enumerate(span_list):
                num = span.xpath('text()').extract()
                num = num[0]
                num_type_tmp = span.xpath('em/@class').extract()
                num_type_tmp = num_type_tmp[0]
                if num_type_tmp == 'icon-num icon-browse-num fl mr5':
                    browse_num = num
                if num_type_tmp == 'icon-num icon-vote-num fl mr5':
                    vote_num = num
                if num_type_tmp == 'icon-num icon-comment-num fl mr5':
                    comment_num = num
            # print browse_num
            # print vote_num
            # print comment_num
            # return
            item = {"data_source":self.web_domain,"cate":"潜水","url":item_url,"img_main":item_img_main,"title":item_title,"author_url":author_url,"author_name":author_name,"author_uid":author_uid,"browse_num":browse_num,"vote_num":vote_num,"comment_num":comment_num}
            self.item_list_insert(item)


            # return
        next_page_url = Selector(text=str1).xpath('//div[contains(@class, "page f-tdn color2 tc")]/a[contains(@id, "nextpage")]/@href').extract()
        if (not next_page_url) or (len(next_page_url) == 0):
            return
        next_page_url = next_page_url[0]
        # print next_page_url
        next_url = response.urljoin(next_page_url)
        # print "next_url"
        # print next_url
        # return
        time.sleep(10)
        yield scrapy.Request(url=next_url, meta={'cookiejar': 2}, cookies=self.my_cookies, dont_filter=True,
                           callback=self.see_list
                           )



    def item_list_insert(self,item):

        one = self.collection.find_one({"url":item['url'],"img_main":item['img_main'],"title":item['title']})
        if not one:

            res = self.collection.insert_one(item)
        # res.inserted_id
            self.logger.info('insert'+str(res.inserted_id))
        else:
            res = self.collection.update_one({"_id": one["_id"]}, {
                "$set": {"browse_num": item["browse_num"], "vote_num": item["vote_num"],"comment_num": item["comment_num"]}})
            # print res.modified_count
            if res.modified_count:
                self.logger.info('update list' + "\t" + str(one["_id"]))







