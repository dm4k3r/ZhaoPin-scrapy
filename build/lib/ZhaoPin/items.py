# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import TakeFirst, Join, MapCompose
from ZhaoPin.ulits.common import wages_convert, remov_tag, max_num, min_num, filter_education_requirements, filter_addrs


class ZhaoPinItem(ItemLoader):
    default_output_processor = TakeFirst()


class LagouItem(scrapy.Item):
    # url转换md5
    url_id = scrapy.Field()
    # 职位描述url
    url = scrapy.Field()
    # 公司
    company = scrapy.Field()
    # 职位
    position = scrapy.Field()
    # 最低工资
    minimum_wage = scrapy.Field(input_processor=MapCompose(remov_tag, wages_convert, min_num))
    # 最高工资
    maximum_wage = scrapy.Field(input_processor=MapCompose(remov_tag, wages_convert, max_num))
    # 地理位置
    location = scrapy.Field(input_processor=remov_tag)
    # 最低工作经验
    minimum_experience = scrapy.Field(input_processor=MapCompose(remov_tag, min_num))
    # 最高工作经验
    maximum_experience  = scrapy.Field(input_processor=MapCompose(remov_tag, max_num))
    # 学历要求
    education_requirements = scrapy.Field(input_processor=MapCompose(remov_tag, filter_education_requirements))
    # 工作类型
    type = scrapy.Field()
    # 工作描述
    description = scrapy.Field()
    # 工作地点
    address = scrapy.Field(input_processor=MapCompose(Join(separator=u''), filter_addrs))
    #爬取生成时间
    crawl_created_time = scrapy.Field()
    #爬取更新时间
    crawl_updated_time = scrapy.Field()


    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO lagou (url_id, url, company, position, minimum_wage, maximum_wage, location, minimum_experience,
            maximum_experience, education_requirements, type, description, address, crawl_created_time, crawl_updated_time)
            VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE company=VALUES(company),
            minimum_wage=VALUES(minimum_wage), maximum_wage=VALUES(maximum_wage), position=VALUES(position), 
            minimum_experience=VALUES(maximum_experience), maximum_experience=VALUES(maximum_experience), 
            education_requirements=VALUES(education_requirements), type=VALUES(type), description=VALUES(description),
            crawl_updated_time=VALUES(crawl_updated_time)
        """
        parmas = (self.get('url_id'), self.get('url'), self.get('company'), self.get('position'), self.get('minimum_wage'),
                  self.get('maximum_wage'), self.get('location'), self.get('minimum_experience'), self.get('maximum_experience'),
                  self.get('education_requirements'), self.get('type'), self.get('description'), self.get('address'),
                  self.get('crawl_created_time'),self.get('crawl_updated_time'))
        return (insert_sql, parmas)

