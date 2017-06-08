# -*- coding:utf-8 -*-

import os
import time
import re

def add():
    pass


def stay_cookie(class_name_in, cookies_str):
    file_dir = "./tmp"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_dir + '/' + str(class_name_in) + '_cookies', 'wb') as f:
        f.write(cookies_str)


def read_cookie(class_name_in, str_in):
    file_dir = "./tmp"
    if os.path.exists(file_dir + '/' + str(class_name_in) + '_cookies'):
        f = open(file_dir + '/' + str(class_name_in) + '_cookies')
        cookies_str = f.read()
        if cookies_str:
            return cookies_str
    return str_in


def rest(time_second_int):
    print 'sleep'
    time.sleep(time_second_int)


def login_filter(error_file_dir, error_file, url):
    if not os.path.exists(error_file_dir):
        os.makedirs(error_file_dir)
    time_now = time.strftime('%Y-%m-%d %X', time.gmtime(time.time()))
    run_error_str = time_now + '---' + url + "---" + "login faild" + "\r\n"
    m_url = re.match(r'.*(https://passport.weibo.com/visitor/visitor).*', url)
    if m_url:
        str4 = m_url.groups()[0]
        run_error_str = run_error_str + "---" + str4
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return

    m_url1 = re.match(r'.*(login.sina.com.cn/sso/login.php).*', url)
    if m_url1:
        str5 = m_url1.groups()[0]
        run_error_str = run_error_str + "---" + str5
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return

    m_url2 = re.match(r'.*(weibo\.com/login).*', url)
    if m_url2:
        str6 = m_url2.groups()[0]
        run_error_str = run_error_str + "---" + str6
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return
    # login.sina.com.cn
    m_url3 = re.match(r'.*(login).*', url)
    if m_url3:
        str7 = m_url3.groups()[0]
        run_error_str = run_error_str + "---" + str7
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return
    m_url4 = re.match(r'.*(sysbusy).*', url)
    if m_url4:
        str8 = m_url4.groups()[0]
        run_error_str = run_error_str + "---" + str8
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return
    m_url5 = re.match(r'.*(accessdeny).*', url)
    if m_url5:
        str1 = m_url5.groups()[0]
        run_error_str = run_error_str + "---" + str1
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return
    m_url6 = re.match(r'.*(login\.php).*', url)
    if m_url6:
        str1 = m_url6.groups()[0]
        run_error_str = run_error_str + "---" + str1
        with open(error_file_dir + '/' + error_file, 'ab') as f:
            f.write(run_error_str)
        return
    return True


def catch_filter(error_file_dir, error_file, url):
    if not os.path.exists(error_file_dir):
        os.makedirs(error_file_dir)
    time_now = time.strftime('%Y-%m-%d %X', time.gmtime(time.time()))
    run_error_str = time_now + '---' + url + "---" + "catch faild" + "\r\n"
    str4 = 'catch nothing'
    run_error_str = run_error_str + "---" + str4
    with open(error_file_dir + '/' + error_file, 'ab') as f:
        f.write(run_error_str)
    return


def output_comment(blog_id, comment_id, comment_user_id, comment_text, datatime, comment_user_nickname, appid):
    # date_now = time.strftime('%Y-%m-%d', time.gmtime(time.time()))
    file_dir = "./comment_data"
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    if not os.path.exists(file_dir + '/' + str(appid)):
        os.makedirs(file_dir + '/' + str(appid))

    str1 = str(blog_id) + "\t" + comment_id + "\t" + comment_user_id + "\t" + comment_text + "\t" + str(
        datatime) + "\t" + comment_user_nickname + "\r\n"
    with open(file_dir + '/' + str(appid) + '/' + str(blog_id), 'ab') as f:
        f.write(str1)