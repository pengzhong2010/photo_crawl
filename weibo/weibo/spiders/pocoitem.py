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
from bson import ObjectId


class PocoitemSpider(scrapy.spiders.Spider):
    name = "pocoitem"
    # allowed_domains = ['weibo.com', 'weibo.cn', 'sina.com.cn']
    # start_urls=['http://m.weibo.cn']
    surl='http://photo.poco.cn/vision.htx&p=1&index_type=hot&tid=-1&gid=0'
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


        self.item_find()
        if not self.iteminfo:
            self.logger.info('item empty')
            return
        next_url = self.iteminfo.get("url")
        if not next_url:
            return
            # print self.my_cookies
        return [scrapy.Request(url=next_url, meta={'cookiejar': 2}, cookies=self.my_cookies, callback=self.see_item
                               )]



    def see_item(self, response):

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
        b = 1
        try:
            str1 = str.decode('GBK').encode('UTF-8')
        except Exception, e:
            b = 0
        # str.decode('UTF-8').encode('GBK')
        # with open('poco3', 'wb') as f:
        #     f.write(str)
        # with open('poco4', 'wb') as f:
        #     f.write(str1)

        if b:
            content = Selector(text=str1).xpath('//div[contains(@class, "final-page-txt lh20 color2 f14")]').extract_first()
            data_time = Selector(text=str1).xpath(
                '//li[contains(@class, "item-time")]/text()').extract_first()
            # print data_time
            # return

            list1 = Selector(text=str1).xpath('//ul[contains(@class, "artList")]/li')
            # print list1

            item_org_imgs=[]
            item_small_imgs = []
            for index1, li1 in enumerate(list1):
                div_list1 = li1.xpath('div')
                div_img_item = div_list1[1]
                div_list2 = div_img_item.xpath('div')
                div_img_box = div_list2[0]
                item_org_img = div_img_box.xpath('img/@data_org_bimg').extract_first()
                item_org_imgs.append(item_org_img)
                item_small_img = div_img_box.xpath('img/@data_img_small').extract_first()
                item_small_imgs.append(item_small_img)

            # print item_org_imgs
            # print item_small_imgs


            self.iteminfo['content'] = content
            self.iteminfo['item_org_imgs'] = item_org_imgs
            self.iteminfo['item_small_imgs'] = item_small_imgs
            self.iteminfo['data_time'] = data_time

            self.item_update()
            # return
        else:
            self.item_update_empty()

        self.item_find()
        if not self.iteminfo:
            return

        next_url = self.iteminfo.get("url")
        if not next_url:
            return
            # print self.my_cookies
        time.sleep(5)
        yield scrapy.Request(url=next_url, meta={'cookiejar': 2}, cookies=self.my_cookies, callback=self.see_item
                               )



    def item_list_insert(self,item):

        one = self.collection.find_one({"url":item['url'],"img_main":item['img_main'],"title":item['title']})
        if not one:

            res = self.collection.insert_one(item)
        # res.inserted_id
            self.logger.info('insert'+str(res.inserted_id))

    def item_find(self):
        self.iteminfo={}
        one = self.collection.find_one({"data_source":"http://photo.poco.cn","item_org_imgs":{"$exists":False},"url":{"$exists":True},"cate":"人像"})
        # one = self.collection.find_one({"_id": ObjectId("590da01610b8a7623bac5bba")})
        # print one
        self.iteminfo = one

    def item_update(self):
        # print self.iteminfo
        res = self.collection.update_one({"_id":self.iteminfo["_id"]},{"$set":{"content":self.iteminfo["content"],"item_org_imgs":self.iteminfo["item_org_imgs"],"item_small_imgs":self.iteminfo["item_small_imgs"],"data_time":self.iteminfo["data_time"]}})
        # print res.modified_count
        if res.modified_count:
            self.logger.info('update' +"\t"+ str(self.iteminfo["_id"]))

    def item_update_empty(self):
        res = self.collection.update_one({"_id": self.iteminfo["_id"]}, {
            "$set": {"item_org_imgs": False
                     }})
        # print res.modified_count
        if res.modified_count:
            self.logger.info('update empty' + "\t" + str(self.iteminfo["_id"]))
