import scrapy
# from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import HtmlResponse

from rec_driver import *
# from pyredis import RedisKv

from pymysql import PyMysql

from pymongo import MongoClient

class TestSpider(scrapy.spiders.Spider):
    name = "test"
    allowed_domains = ['weibo.com','weibo.cn','sina.com.cn']
    # start_urls=['http://m.weibo.cn']
    # surl = 'http://m.weibo.cn'
    def start_requests(self):
        surl =u'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=http%3A%2F%2Fm.weibo.cn%2F'

        return [scrapy.Request(url='http://m.weibo.cn/u/5708787172', meta={'cookiejar': 0}, callback=self.see_home
                               )]

    def see_home(self,response):
        self.mydb_con = MongoClient("mongodb://" + conf1.MONGO_HOST + ":" + str(conf1.MONGO_PORT))
        self.mydb_db = self.mydb_con.photo
        self.collection = self.mydb_db.item
        one = self.collection.find_one()
        print one
        return
        print "123"
        for document in one:
            print(document)
        print "345"
        return










        # print 'url'
        # print response.url
        # print 'body'
        # print response.body
        # print 'headers'
        # print response.headers
        # print 'meta'
        # with open('one_case', 'ab') as f:
        #     f.write(response.body)

        mysql_con = PyMysql(conf1.MYSQL_URL, conf1.MYSQL_PORT, conf1.MYSQL_USER, conf1.MYSQL_PASSWD, conf1.MYSQL_DG_DB)
        i=123
        sql = "insert into fensi_daily_static ( `appid` ) values ( %d )" % i
        ret = mysql_con.excute(sql, "one")
        # sql = """
        # select uid from weibo_fans_origin where status=0 order by id limit 100
        # """
        # ret = mysql_con.select(sql)

        # sql = "select id from weibo_fensi_info_id where id = %s " % 1237
        # ret = mysql_con.select(sql,'one')
        # sql = "select article_infoid, date_format(article_time, \"%%Y%%m%%d %%H\"), thum_url, small_thum_url from article_info where article_infoid = %d" % article_infoid
        # article_tuple = self._pymysql.select(sql, 'one')
        # t_tuple = tuple(["xx", "oo", 3190353011])
        # sql = """
        #             update weibo_fans_origin set info1= %s ,info2= %s ,`status`=1 where uid= %s
        #
        #         """
        # ret = mysql_con.excute(sql, "one", t_tuple)
        # t_tuple1 = tuple([2325,'123dd','123ccc',1])
        # t_tuple2 = tuple([2324, '123dd1', '123ccc1', 1])
        # t_tuple=[t_tuple1,t_tuple2]
        #
        # sql = """
        #         insert into weibo_fans_origin (
        #             `uid`,`info1`,`info2`,`status`
        #         ) values (%s,%s,%s,%s)
        #
        #     """
        # ret = mysql_con.excute(sql, "many", t_tuple)

        print ret

        # for i in ret:
        #     print i
        #     print i.get("id")
        #     print i.get("uid")
        #     print i.get("catch_status")