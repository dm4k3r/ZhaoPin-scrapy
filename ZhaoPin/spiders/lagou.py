# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ZhaoPin.items import ZhaoPinItem, LagouItem
from ZhaoPin.ulits.common import get_md5
from datetime import datetime


class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    start_urls = ['https://lagou.com/']

    rules = (
        Rule(LinkExtractor(allow=r'zhaopin/[a-zA-z]/'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'gongsi/j\d+.html'), follow=True),
        Rule(LinkExtractor(allow=r'jobs/\d+.html'), callback='parse_item', follow=True),
    )
    custom_settings = {
        "spider_name": "lagou",
        'COOKIES_ENABLED': False,
        'DOWNLOAD_DELAY': 3,
        'DEFAULT_REQUEST_HEADERS': {
            'Host': 'www.lagou.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cookie': 'user_trace_token=20171015132411-12af3b52-3a51-466f-bfae-a98fc96b4f90; LGUID=20171015132412-13eaf40f-b169-11e7-960b-525400f775ce; SEARCH_ID=070e82cdbbc04cc8b97710c2c0159ce1; ab_test_random_num=0; X_HTTP_TOKEN=d1cf855aacf760c3965ee017e0d3eb96; showExpriedIndex=1; showExpriedCompanyHome=1; showExpriedMyPublish=1; hasDeliver=0; PRE_UTM=; PRE_HOST=www.baidu.com; PRE_SITE=https%3A%2F%2Fwww.baidu.com%2Flink%3Furl%3DsXIrWUxpNGLE2g_bKzlUCXPTRJMHxfCs6L20RqgCpUq%26wd%3D%26eqid%3Dee53adaf00026e940000000559e354cc; PRE_LAND=https%3A%2F%2Fwww.lagou.com%2F; index_location_city=%E5%85%A8%E5%9B%BD; TG-TRACK-CODE=index_hotjob; login=false; unick=""; _putrc=""; JSESSIONID=ABAAABAAAFCAAEG50060B788C4EED616EB9D1BF30380575; _gat=1; _ga=GA1.2.471681568.1508045060; LGSID=20171015203008-94e1afa5-b1a4-11e7-9788-525400f775ce; LGRID=20171015204552-c792b887-b1a6-11e7-9788-525400f775ce',
            'Referer': 'www.lagou.com',
            'Origin': 'www.lagou.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\ Chrome/64.0.3282.140 Safari/537.36',
        }
    }

    def parse_item(self, response):
        Item = ZhaoPinItem(LagouItem(), response)
        Item.add_value('url_id', get_md5(response.url))
        Item.add_value('url', response.url)
        Item.add_xpath('company', '//div[@class="company"]/text()')
        Item.add_xpath('position', '//div[@class="job-name"]/span[@class="name"]/text()')
        Item.add_xpath('minimum_wage', '//dd[@class="job_request"]/p/span[1]/text()')
        Item.add_xpath('maximum_wage', '//dd[@class="job_request"]/p/span[1]/text()')
        Item.add_xpath('location', '//dd[@class="job_request"]/p/span[2]/text()')
        Item.add_xpath('minimum_experience', '//dd[@class="job_request"]/p/span[3]/text()')
        Item.add_xpath('maximum_experience', '//dd[@class="job_request"]/p/span[3]/text()')
        Item.add_xpath('education_requirements', '//dd[@class="job_request"]/p/span[4]/text()')
        Item.add_xpath('type', '//dd[@class="job_request"]/p/span[5]/text()')
        description_selector = response.xpath('//dd[@class="job_bt"]')
        description = description_selector.xpath('string(.)').extract()
        Item.add_value('description', description)
        Item.add_xpath('address', '//div[@class="work_addr"]/a/text()')
        Item.add_value('crawl_created_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        Item.add_value('crawl_updated_time', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        yield Item.load_item()
