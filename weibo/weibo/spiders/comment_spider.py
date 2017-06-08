# -*- coding:utf-8 -*-
import scrapy
from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
# from scrapy.http import HtmlResponse
import re
import time
import json

from rec_driver import *
# from pyredis import RedisKv

from pymysql import PyMysql
import common

# surl
# start_search_page,end_search_page
# url_fans
# my_cookies

class CommentSpider(scrapy.spiders.Spider):
    name = "comment"
    allowed_domains = ['weibo.com', 'weibo.cn', 'sina.com.cn']
    # start_urls=['http://m.weibo.cn']

    spider_sep_per_time = 3600

    surl = 'http://weibo.com/xiaopapi/profile?rightmod=1&wvr=6&mod=personnumber&is_all=1'

    first_url_prefix = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id='
    first_url_suffix = '&page='

    blog_list=''
    blog_list_len=0
    blog_list_key=0
    comment_page=1
    url_page_demo=''
    blog_id=''

    mysql_con = ''
    my_cookies = {}
    error_file_dir = ""
    error_file=''
    cookies_user = conf1.MY_COOKIES1
    appid = 1287792

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

        self.mysql_con = PyMysql(conf1.MYSQL_URL, conf1.MYSQL_PORT, conf1.MYSQL_USER, conf1.MYSQL_PASSWD,
                                 conf1.MYSQL_DG_DB)
        return [scrapy.Request(url=self.surl, meta={'cookiejar': 3}, cookies=self.my_cookies, callback=self.see_home
                               )]

    def see_home(self, response):

        # print 'url'
        # print response.url
        # print 'body'
        # print response.body
        # print 'headers'
        # print response.headers
        # print 'meta'
        # print response.meta
        #
        # with open('commentpage', 'wb') as f:
        #     f.write(response.body)

        #login 过滤
        if not common.login_filter(self.error_file_dir, self.error_file, response.url):
            return


        #db list one
        blog_dict = self.get_blog_one(response.request.headers.getlist('Cookie')[0])
        if not blog_dict:
            return
        #catch
        #self.url_page_demo = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id='+str(blog_dict['blog_id'])+'&page='
        self.url_page_demo = self.first_url_prefix+str(blog_dict['blog_id'])+self.first_url_suffix
        # next_url='http://weibo.com'+str(blog_dict['url'])
        self.blog_id = blog_dict['blog_id']
        self.comment_page = 1
        next_url = self.url_page_demo + str(self.comment_page)

        return [
            scrapy.Request(url=next_url, meta={'cookiejar': 3}, cookies=self.my_cookies, dont_filter=True, callback=self.page_parse
                           )]


        #prase
        #file write
        #sleep

    def page_parse(self, response):

        if not common.login_filter(self.error_file_dir, self.error_file, response.url):
            return
        common.stay_cookie(self.name, response.request.headers.getlist('Cookie')[0])

        # print 'url'
        # print response.url
        # print 'body'
        # print response.body
        # print 'headers'
        # print response.headers
        # print 'meta'
        # print response.meta

        # with open('commentpage', 'wb') as f:
        #     f.write(response.body)
        time_now = int(time.time())

        res = json.loads(response.body)
        aa= res.get('data')
        str1 = aa.get('html')
        # with open('commentpage2', 'wb') as f:
        #     f.write(str1)
        # gbkTypeStr = bb.encode("GBK", 'ignore')
        # print gbkTypeStr

        list1 = Selector(text=str1).xpath('//div[contains(@class, "list_li S_line1 clearfix")]')
        for index1, link1 in enumerate(list1):
            link2 = link1.xpath(
                'div[contains(@class, "list_con")]/div[contains(@class, "WB_func clearfix")]/div[contains(@class, "WB_from S_txt2")]/text()').extract()
            if not link2:
                continue
            else:
                last_time_str = link2[0]
                m1 = re.match(r'(.*)' + u'分钟前' + '.*', last_time_str)
                if m1:
                    last_time = m1.groups()[0]
                    last_time = last_time.strip()
                    last_time = int(last_time)
                    last_time = last_time * 60
                    data_time = time_now - last_time

                    comment_id = ''
                    comment_id_list = link1.xpath('@comment_id').extract()
                    if comment_id_list:
                        comment_id = comment_id_list[0]

                    comment_text = ''
                    comment_text_list = link1.xpath(
                        'div[contains(@class, "list_con")]/div[contains(@class, "WB_text")]/text()').extract()
                    if comment_text_list:
                        for i in comment_text_list:
                            i = i.strip()
                            if i:
                                comment_text = i

                    comment_user_id = ''
                    comment_user_nickname = ''
                    a_list = link1.xpath('div[contains(@class, "list_con")]/div[contains(@class, "WB_text")]/a')
                    if a_list:
                        comment_user_id_list = a_list[0].xpath('@usercard').extract()
                        if comment_user_id_list:
                            comment_user_id_str = comment_user_id_list[0]
                            comment_user_id = comment_user_id_str[3:]

                        comment_user_nickname_list = a_list[0].xpath('text()').extract()
                        if comment_user_nickname_list:
                            comment_user_nickname = comment_user_nickname_list[0]

                    # print self.blog_id
                    # print data_time
                    # print comment_id
                    # print comment_text
                    # print comment_user_id
                    common.output_comment(self.blog_id, comment_id, comment_user_id, comment_text, data_time, comment_user_nickname, self.appid)

        if list1:
            link3 = list1[-1].xpath(
                'div[contains(@class, "list_con")]/div[contains(@class, "WB_func clearfix")]/div[contains(@class, "WB_from S_txt2")]/text()').extract()
            if link3:
                data_time_str = link3[0]
                m1 = re.match(r'(.*' + u'分钟前' + '.*)', data_time_str)
                if m1:
                    # next page
                    # pass
                    self.comment_page = self.comment_page + 1
                    next_url = self.url_page_demo + str(self.comment_page)
                    time.sleep(2)
                    return [
                        scrapy.Request(url=next_url, meta={'cookiejar': 3}, cookies=self.my_cookies, dont_filter=True,
                                       callback=self.page_parse
                                       )]

        #next blog
        # pass
        blog_dict = self.get_blog_one(response.request.headers.getlist('Cookie')[0])
        if not blog_dict:
            return
        # catch
        #self.url_page_demo = 'http://weibo.com/aj/v6/comment/big?ajwvr=6&id=' + str(blog_dict['blog_id']) + '&page='
        self.url_page_demo = self.first_url_prefix + str(blog_dict['blog_id']) + self.first_url_suffix
        # next_url='http://weibo.com'+str(blog_dict['url'])
        self.blog_id = blog_dict['blog_id']
        self.comment_page = 1
        next_url = self.url_page_demo + str(self.comment_page)
        time.sleep(2)
        return [
            scrapy.Request(url=next_url, meta={'cookiejar': 3}, cookies=self.my_cookies, dont_filter=True,
                           callback=self.page_parse
                           )]





    def get_blog_one(self,cookies_str):
        dict_tmp = {}
        if not self.blog_list:
            self.get_blog_list()

        if self.blog_list:
            if self.blog_list_key<self.blog_list_len:
                dict_tmp = self.blog_list[self.blog_list_key]
                self.blog_list_key = self.blog_list_key + 1
            else:
                self.blog_list=''
                self.blog_list_len = 0
                self.blog_list_key = 0
                #sleep
                common.rest(self.spider_sep_per_time)
                return self.get_blog_one(cookies_str)
                pass
        return dict_tmp
    def get_blog_list(self):
        sql = " select * from weibo_blog where appid = "+str(self.appid)+" order by create_time desc limit 20"
        ret = self.mysql_con.select(sql)
        if ret:
            self.blog_list=ret
            self.blog_list_len=len(ret)











