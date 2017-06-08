# -*- coding:utf-8 -*-
import scrapy
# from scrapy.selector import HtmlXPathSelector
from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import re
import datetime
import time
import sys
sys.setrecursionlimit(100000000)


from rec_driver import *
# from pyredis import RedisKv

from pymysql import PyMysql


class Parse():
    name='parse'

    str_parse_tmp=''
    uid_info={}
    id_tmp=0
    id_run_tmp=0
    mysql_con = PyMysql(conf1.MYSQL_URL, conf1.MYSQL_PORT, conf1.MYSQL_USER, conf1.MYSQL_PASSWD,
                                 conf1.MYSQL_DG_DB)


    def get_uid(self):

        self.id_run_tmp=0
        self.id_run_tmp=self.select_uid_for_parse()
        self.id_tmp = self.id_run_tmp

    def get_text(self):
        self.str_parse_tmp=''
        if self.id_run_tmp:
            sql = " select detail from weibo_text where id= %d" % int(self.id_run_tmp)
            ret = self.mysql_con.select(sql)
            # print ret
            if ret:
                for i in ret:
                    self.str_parse_tmp = i.get("detail")
        #
        return




    def select_uid_for_parse(self):
        # return 1075489207
        if not self.id_tmp:
            sql = """
                select id from weibo_fensi_info
                    where last_update_time = 0 and id >2864293
                    order by id
                    limit 1
                """
        else:

            sql = "select id from weibo_fensi_info where last_update_time = 0 and id > %d order by id limit 1 " % int(self.id_tmp)
        ret = self.mysql_con.select(sql)

        if ret:
            # res_list_tmp = []
            for i in ret:
                res_id=i.get("id")
            return res_id
        else:
            print sql
            print "sleeping"
            # time.sleep(60)
            # return self.select_uid_for_parse()
            return 0


    def parse_go(self):
        self.get_uid()
        # print self.id_run_tmp
        # print self.id_tmp

        if self.id_run_tmp:
            self.get_text()

            if self.str_parse_tmp:
                self.parse_text()
                self.insert_uid_info()
            return self.parse_go()


            # else:
            #     # pass
            #     return self.parse_go()
        # time.sleep(0.05)


    def parse_text(self):
        if not self.str_parse_tmp:
            return
        info={}
        str1=self.str_parse_tmp
        self.uid_info={}
        try:
            m2 = re.match(r'.*\"html\":\"\<!--模块--\>(.*)', str1)
            if m2:
                str2 = m2.groups()[0]

                list1 = Selector(text=str2).xpath('//div[contains(@class, "m_wrap clearfix")]/ul/li')
                # print list1
                for index, link in enumerate(list1):
                    key = ''
                    values = []
                    list_tmp = link.xpath('span/text()').extract()
                    if list_tmp:
                        key = list_tmp[0]
                        if key == u'昵称：':
                            info['nick_name'] = list_tmp[1]
                        elif key == u'所在地：':
                            position_list = list_tmp[1].split(' ')
                            position_len = len(position_list)
                            if position_len:
                                info['province'] = position_list[0]
                                if position_len > 1:
                                    info['city'] = position_list[1]
                        elif key == u'性别：':
                            if list_tmp[1] == u'男':
                                info['sex'] = 1
                            else:
                                info['sex'] = 0
                        elif key == u'简介：':
                            info['desc_fill'] = list_tmp[1]
                        elif key == u'生日：':
                            str_s = list_tmp[1]
                            try:
                                str_s = str_s.replace(u'年', '-')
                                str_s = str_s.replace(u'月', '-')
                                str_s = str_s.replace(u'日', '')
                                br_list = str_s.split('-')

                                br_m = int(br_list[1])
                                if br_m < 10:
                                    br_m_str = '0' + str(br_m)
                                else:
                                    br_m_str = str(br_m)
                                br_list[1] = br_m_str
                                br_m = int(br_list[2])
                                if br_m < 10:
                                    br_m_str = '0' + str(br_m)
                                else:
                                    br_m_str = str(br_m)
                                br_list[2] = br_m_str
                                str_s = '-'.join(br_list)
                                # print str_s

                                s = time.mktime(time.strptime(str(str_s), '%Y-%m-%d'))
                            except Exception as e:
                                s = 0
                            info['birth_fill'] = int(s)


                        elif key == u'注册时间：':
                            # print list_tmp
                            str_s = list_tmp[1]
                            s = time.mktime(time.strptime(str_s, '%Y-%m-%d'))
                            info['regis_date'] = int(s)
                        elif key == u'公司：':
                            company_list = link.xpath('span')
                            company_list_info = []
                            for ix, linkx in enumerate(company_list):
                                company_one_list = linkx.xpath('text()').extract()
                                company_one_str = ''
                                if not company_one_list[0] == u'公司：':
                                    part1 = linkx.xpath('a/text()').extract()
                                    company_one_str = part1[0]
                                    # print company_one_str
                                    for i in company_one_list:
                                        company_one_str = company_one_str + i
                                    # print company_one_str
                                    company_list_info.append(company_one_str)
                            # info['company'] = json.dumps(company_list_info)
                            info['company'] = ';'.join(company_list_info)
                        elif key == u'大学：':
                            university_list = link.xpath('span')
                            university_list_info = []
                            for ix, linkx in enumerate(university_list):
                                university_one_list = linkx.xpath('text()').extract()
                                university_one_str = ''
                                if not university_one_list[0] == u'大学：':
                                    part1 = linkx.xpath('a/text()').extract()
                                    university_one_str = part1[0]
                                    # print company_one_str
                                    for i in university_one_list:
                                        university_one_str = university_one_str + i
                                    # print university_one_str
                                    university_list_info.append(university_one_str)
                            # info['university'] = json.dumps(university_list_info)
                            info['university'] = ';'.join(university_list_info)
                        elif key == u'标签：':
                            spans = link.xpath('span/a/text()').extract()
                            if spans:
                                info['tags'] = ';'.join(spans)
                                # tags=spans[1]

            # "html":"<div class="PRF_modwrap S_line1 clearfix">
            m3 = re.match(r'.*\"html\":\"\<div class=\"PRF_modwrap S_line1 clearfix\"\>(.*)', str1)
            if m3:
                str3 = m3.groups()[0]
                # print str3
                list2 = Selector(text=str3).xpath('//p[contains(@class, "level_info")]/span')
                for index, link in enumerate(list2):
                    x1 = link.xpath('text()').extract()
                    x2 = link.xpath('span/text()').extract()

                    # print x1[0]
                    # print x2[0]
                    if x1[0] == u' 当前等级： ':
                        m3_1 = re.match(r'.*([\d]+).*', str1)
                        if m3_1:
                            info['weibo_level'] = m3_1.groups()[0]

                    elif x1[0] == u' 经验值： ':
                        info['exp_value'] = x2[0]


                        # print list2

            # "html":"<div class="WB_cardwrap S_bg2" >
            m4 = re.match(r'.*\"html\":\"\<div class=\"WB_cardwrap S_bg2\" \>(.*)', str1)
            if m4:
                str4 = m4.groups()[0]
                list4 = Selector(text=str4).xpath('//table[contains(@class, "tb_counter")]/tbody/tr/td/a')
                # print list4.extract()
                for index, link4 in enumerate(list4):

                    x1 = link4.xpath('span/text()').extract()
                    x2 = link4.xpath('strong/text()').extract()

                    if x1[0] == u'关注':
                        info['attr_count'] = x2[0]
                    elif x1[0] == u'粉丝':
                        info['fensi_count'] = x2[0]
                    elif x1[0] == u'微博':
                        info['weibo_count'] = x2[0]

            # else:
            #     print "not match"

            # print info
            self.uid_info=info
        except Exception as e:
            pass


    def insert_uid_info(self):
        id = self.id_run_tmp
        print id
        if not id :
            return

        info=self.uid_info
        if not info:
            return
        info_keys=[]
        info_values=[]

        # info_keys.append('id')
        # info_values.append(int(id))

        # print info

        nick_name=info.get('nick_name')
        if nick_name:
            info_keys.append('nick_name')
            info_values.append(nick_name)
        weibo_count = info.get('weibo_count')
        if weibo_count:
            info_keys.append('weibo_count')
            info_values.append(int(weibo_count))
        fensi_count = info.get('fensi_count')
        if fensi_count:
            info_keys.append('fensi_count')
            info_values.append(int(fensi_count))

        weibo_level = info.get('weibo_level')
        if weibo_level:
            info_keys.append('weibo_level')
            info_values.append(int(weibo_level))

        exp_value = info.get('exp_value')
        if exp_value:
            info_keys.append('exp_value')
            info_values.append(int(exp_value))
        sex = info.get('sex')
        if sex is not None:
            info_keys.append('sex')
            info_values.append(sex)
        city = info.get('city')
        if city:
            info_keys.append('city')
            info_values.append(city)
        province = info.get('province')
        if province:
            info_keys.append('province')
            info_values.append(province)
        university = info.get('university')
        if university:
            info_keys.append('university')
            info_values.append(university)
        company = info.get('company')
        if company:
            info_keys.append('company')
            info_values.append(company)
        desc_fill = info.get('desc_fill')
        if desc_fill:
            info_keys.append('desc_fill')
            info_values.append(desc_fill)
        tags = info.get('tags')
        if tags:
            info_keys.append('tags')
            info_values.append(tags)
        birth_fill = info.get('birth_fill')
        if birth_fill:
            info_keys.append('birth_fill')
            info_values.append(birth_fill)
        regis_date = info.get('regis_date')
        if regis_date:
            info_keys.append('regis_date')
            info_values.append(regis_date)

        time_int = time.mktime(datetime.datetime.now().timetuple())
        last_update_time= int(time_int)
        info_keys.append('last_update_time')
        info_values.append(last_update_time)


        t_tuple = tuple(info_values)
        ss=' = %s , '.join(info_keys)
        sql="update weibo_fensi_info set "+ss+" = %s where id = "+str(id)+" "
        print sql
        print info_values

        # t_tuple = tuple([data_update.get("info1"), data_update.get("info2"), data_update.get("uid")])
        #     sql = """
        #             update weibo_fensi_info_id set info1= %s ,info2= %s ,`status`=1 where uid= %s
        #
        #         """
        ret = self.mysql_con.excute(sql, "one", t_tuple)
        print ret




def main():
    tm = Parse()
    # while 1:
    #     tm.parse_go()

    tm.parse_go()



    # rm.test()

if __name__ == "__main__":
    main()