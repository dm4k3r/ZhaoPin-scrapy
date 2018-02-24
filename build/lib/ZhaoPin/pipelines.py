# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
from MySQLdb import cursors
from twisted.enterprise import adbapi


class MysqlTwsitedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparmas = dict(
            host = settings['MYSQL_HOST'],
            db = settings['DB_NAME'],
            user = settings['MYSQL_USERNAME'],
            password = settings['MYSQL_PASSWORD'],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparmas)
        return cls(dbpool)


    def process_item(self, item, spider):
        query = self.dbpool.runIntertraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursors, item):
        insert_sql, parmas = item.get_insert_sql()
        cursors.execute(insert_sql, parmas)


