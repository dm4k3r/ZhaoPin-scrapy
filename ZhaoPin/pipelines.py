# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb.cursors
from twisted.enterprise import adbapi
import redis
from scrapy.exceptions import DropItem
import logging

logger = logging.getLogger(__name__)
redis_db = redis.Redis(host='192.168.1.110', port=6379, db=1)
redis_data_dict = "hex_url"


class DuplicatePipeline(object):
    """
    通过redis进行去重
    """
    def __init__(self, dbparmas, spider_name):
        redis_db.flushall()
        mysql_cn = MySQLdb.connect(**dbparmas)
        cur = mysql_cn.cursor()
        db_table = spider_name
        if redis_db.hlen(redis_data_dict) == 0:
            sql = "SELECT url_id FROM {0}".format(db_table)
            cur.execute(sql)
            df = cur.fetchall()
            for id in df:
                redis_db.hset(redis_data_dict, id['url_id'], 0)
            cur.close()

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
        spider_name = settings['spider_name']
        return cls(dbparmas, spider_name)

    # 处理item，取item里的url和key里的字段对比，看是否存在，存在就丢掉这个item。不存在返回item给后面的函数处理
    def process_item(self, item, spider):
        if redis_db.hexists(redis_data_dict, item['url_id']):
            raise DropItem("Duplicate item found: {0}".format(item))
        return item


class InsertRedis(object):
    def process_item(self, item, spider):
        redis_db.hset(redis_data_dict, item['url_id'], 0)
        return item


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
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)

    def handle_error(self, failure):
        print(failure)

    def do_insert(self, cursors, item):
        insert_sql, parmas = item.get_insert_sql()
        cursors.execute(insert_sql, parmas)


