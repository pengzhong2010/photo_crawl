#!/usr/bin/env python
# -*- coding: utf-8 -*-

from rec_driver import *


class PyMysql:

    def __init__(self, host, port, user, passwd, db, charset="utf8", autocommit=False):
        self._cursor = None
        self._conn = None
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._db = db
        self._charset = charset
        self._autocommit = autocommit
        self._retry = 10
        self._internal = 60

        i = 0
        while self._cursor is None and i < self._retry:
            try:
                self.reconnect()
                i += 1
                if self._conn.open:
                    pass
                    # ilog_info.info("mysql connected, host: %s, port: %d, user: %s, db: %s" % (self._host, self._port, self._user, self._db))
            except Exception as e:
                pass
                # ilog.error("mysql connecting error, host: %s, port: %d, user: %s, db: %s, err_msg: %s\t%s" %
                #            (self._host, self._port, self._user, self._db, str(e), traceback.format_exc().replace("\n", "")))

    def __del__(self):
        self.close()

    def reconnect(self):
        self.close()
        try:
            self._conn = MySQLdb.connect(
                host=self._host, port=self._port, user=self._user, passwd=self._passwd, db=self._db)
            self.set_character_set()
            self._cursor = self._conn.cursor(MySQLdb.cursors.DictCursor)
            # cur = conn.cursor(MySQLdb.cursors.DictCursor)
            if self._conn.open:
                pass
                # ilog_info.info("mysql reconnected, host: %s, port: %d, user: %s, db: %s" % (self._host, self._port, self._user, self._db))
        except Exception as e:
            time.sleep(self._internal)

            # ilog.error("mysql reconnecting error, host: %s, port: %d, user: %s, db: %s, err_msg: %s\t%s" %
            #            (self._host, self._port, self._user, self._db, str(e), traceback.format_exc().replace("\n", "")))

    def select(self, sql, mode="many"):
        ret = None
        try:
            if self._cursor is not None:
                self._cursor.close()
                self._cursor = None
            self._cursor = self._conn.cursor(MySQLdb.cursors.DictCursor)

            self._cursor.execute(sql)
            if mode == "many":
                ret = self._cursor.fetchall()
            else:
                ret = self._cursor.fetchone()
        except (AttributeError, MySQLdb.OperationalError):
            # ilog.error("mysql not connected,  host: %s, port: %d, user: %s, db: %s, sql: %s, err_msg: %s" %
            #            (self._host, self._port, self._user, self._db, sql, traceback.format_exc().replace("\n", "")))
            time.sleep(self._internal)
            self.reconnect()
            self._cursor.execute(sql)
            if mode == "many":
                ret = self._cursor.fetchall()
            else:
                ret = self._cursor.fetchone()
        except Exception as e:
            # ilog.error("selecting error, host: %s, port: %d, user: %s, db: %s, sql: %s, err_msg: %s\t%s" %
            #            (self._host, self._port, self._user, self._db, sql, str(e), traceback.format_exc().replace("\n", "")))
            # if e.args[0] == 2006:
            #     self.reconnect()
            pass
        return ret

    def excute(self, sql, mode="many", args=None):
        ret_status = False
        try:
            if mode == "many":
                self._cursor.executemany(sql, args)
            else:
                self._cursor.execute(sql, args)
            self.commit()
            ret_status = True
        except (AttributeError, MySQLdb.OperationalError):
            self.rollback()
            # print "mysql not connected, host: %s, port: %d, user: %s, db: %s, sql: %s, err_msg: %s" % (self._host, self._port, self._user, self._db, sql, traceback.format_exc().replace("\n", ""))
            # ilog.error("mysql not connected, host: %s, port: %d, user: %s, db: %s, sql: %s, err_msg: %s" %
            #            (self._host, self._port, self._user, self._db, sql, traceback.format_exc().replace("\n", "")))
            time.sleep(self._internal)
            self.reconnect()
            if mode == "many":
                self._cursor.executemany(sql, args)
            else:
                self._cursor.execute(sql, args)
            self.commit()
            ret_status = True
        except Exception as e:
            self.rollback()
            # print "inserting error, host: %s, port: %d, user: %s, db: %s, sql: %s, err_msg: %s\t%s" %   (self._host, self._port, self._user, self._db, sql, str(e), traceback.format_exc().replace("\n", ""))
            # ilog.error("inserting error, host: %s, port: %d, user: %s, db: %s, sql: %s, err_msg: %s\t%s" %
            #            (self._host, self._port, self._user, self._db, sql, str(e), traceback.format_exc().replace("\n", "")))
            # if e.args[0] == 2006:
            #     self.reconnect()
        return ret_status

    def autocommit(self):
        self._conn.autocommit(self._autocommit)

    def set_character_set(self):
        self._conn.set_character_set(self._charset)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()

    def close(self):
        try:
            if self._cursor is not None:
                self._cursor.close()
                self._cursor = None
            if self._conn is not None:
                self._conn.close()
                self._conn = None
        except Exception as e:
            pass
            # ilog.error("mysql close error, host: %s, port: %d, user: %s, db: %s, err_msg: %s\t%s" %
            #            (self._host, self._port, self._user, self._db, str(e), traceback.format_exc().replace("\n", "")))

    def get_rows_num(self):
        return self._cursor.rowcount

    def get_mysql_version(self):
        MySQLdb.get_client_info()


def main():
    pymysql = PyMysql(conf.MYSQL_URL_TEST, conf.MYSQL_PORT,
                      conf.MYSQL_USER, conf.MYSQL_PASSWD, conf.MYSQL_DG_DB)
    sql = "select * from click_log where click_logid = 3"
    print sql
    ret_list = pymysql.select(sql)
    print ret_list


if __name__ == '__main__':
    main()
