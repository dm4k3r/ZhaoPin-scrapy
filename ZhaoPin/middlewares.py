# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import logging
from fake_useragent import UserAgent
import requests
from scrapy.exceptions import  IgnoreRequest
from ZhaoPin.ulits.common import get_md5
import redis
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from datetime import datetime, timedelta
from twisted.web._newclient import ResponseNeverReceived

logger = logging.getLogger(__name__)


# class ZhaopinSpiderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the spider middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_spider_input(self, response, spider):
#         # Called for each response that goes through the spider
#         # middleware and into the spider.
#
#         # Should return None or raise an exception.
#         return None
#
#     def process_spider_output(self, response, result, spider):
#         # Called with the results returned from the Spider, after
#         # it has processed the response.
#
#         # Must return an iterable of Request, dict or Item objects.
#         for i in result:
#             yield i
#
#     def process_spider_exception(self, response, exception, spider):
#         # Called when a spider or process_spider_input() method
#         # (from other spider middleware) raises an exception.
#
#         # Should return either None or an iterable of Response, dict
#         # or Item objects.
#         pass
#
#     def process_start_requests(self, start_requests, spider):
#         # Called with the start requests of the spider, and works
#         # similarly to the process_spider_output() method, except
#         # that it doesn’t have a response associated.
#
#         # Must return only requests (not items).
#         for r in start_requests:
#             yield r
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
#
#
# class ZhaopinDownloaderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_request(self, request, spider):
#         # Called for each request that goes through the downloader
#         # middleware.
#
#         # Must either:
#         # - return None: continue processing this request
#         # - or return a Response object
#         # - or return a Request object
#         # - or raise IgnoreRequest: process_exception() methods of
#         #   installed downloader middleware will be called
#         return None
#
#     def process_response(self, request, response, spider):
#         # Called with the response returned from the downloader.
#
#         # Must either;
#         # - return a Response object
#         # - return a Request object
#         # - or raise IgnoreRequest
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # Called when a download handler or a process_request()
#         # (from other downloader middleware) raises an exception.
#
#         # Must either:
#         # - return None: continue processing this exception
#         # - return a Response object: stops process_exception() chain
#         # - return a Request object: stops process_exception() chain
#         pass
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)

class IngoreRequestMiddleware(object):
    """
    忽略已经爬取的url
    """
    def __init__(self):
        self.redis_db = redis.Redis(host='192.168.1.110', port=6379, db=1)
        self.redis_data_dict = "hex_url"

    def process_request(self, request, spider):
        url_id = get_md5(request.url)
        if self.redis_db.hexists(self.redis_data_dict, url_id):
            logger.info("已经爬取,忽略url: {}".format(request.url))
            raise IgnoreRequest("IgnoreRequest : {0}".format(request.url))


class RandomUserAgentMiddleware(object):
    """
    随机切换User_Agent,Type在settings中设置，默认为random
    """
    def __init__(self, settings):
        super(RandomUserAgentMiddleware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = settings.get('USER_AGENT_TYPE', 'random')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)
        request.headers.setdefault(b'User-Agent', get_ua())


class HttpProxyMiddleware(object):
    # 遇到这些类型的错误直接当做代理不可用处理掉, 不再传给retrymiddleware
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)

    def __init__(self, settings):
        # 从配置文件中中获取是否使用代理，默认为False
        self.use_proxy = settings.getbool('USE_PROXY', False)
        # 从配置文件中中获取代理池服务器地址
        self.proxy_pool_url = settings.get('PROXY_REQUEST_URL')
        # 最后一次没有使用代理的时间
        self.last_no_proxy_time = datetime.now()
        # 代理模式切换时间，默认每20分钟切换一次
        self.proxy_delay_tiem = 5
        # 是否切换代理状态
        self.proxy_status = False

    @classmethod
    def from_crawler(cls, crawler):
        # 默认从setting.py获取配置，若有自定义配置，从自定义配置中获取
        settings = crawler.settings
        return cls(settings)

    # 从代理池中获取代理ip，格式为ip:port
    def get_proxy(self):
        ip_port = requests.get(self.proxy_pool_url + "/get/").text
        return ip_port

    #  对当前请求设置代理，代理格式为http://ip:port
    def set_proxy(self, request):
        if self.proxy_status:
            proxy = self.get_proxy()
            request.meta["proxy"] = "http://" + proxy
            logger.info("使用代理: {0}".format(proxy))
        else:
            pass

    # 切换代理ip并删除无效代理ip
    def change_proxy(self, request):
        if "proxy" in request.meta.keys():
            proxy_ip = request.meta['proxy'].split('/')[-1]
            logger.info("删除代理ip{}".format(proxy_ip))
            requests.get(self.proxy_pool_url + "/delete/?proxy={}".format(proxy_ip))
        proxy = self.get_proxy()
        request.meta["proxy"] = "http://" + proxy
        logger.info("切换代理: {0}".format(proxy))

    def process_request(self, request, spider):
        """
        处理请求的函数，切换代理模式，并根据模式设置是否使用代理,20分钟切换
        """
        if self.use_proxy:
            if datetime.now() > (self.last_no_proxy_time + timedelta(minutes=self.proxy_delay_tiem)):
                if self.proxy_status:
                    logger.info("<<<<<<<<<<切换为无代理模式>>>>>>>>>>")
                    self.proxy_status = False
                    self.last_no_proxy_time = datetime.now()
                else:
                    logger.info("<<<<<<<<<<切换为代理模式>>>>>>>>>>")
                    self.proxy_status = True
                    self.last_no_proxy_time = datetime.now()
        request.meta["dont_redirect"] = True
        self.set_proxy(request)

    def process_response(self, request, response, spider):
        """
        检查response.status
        """
        # status不是正常的200而且不在spider声明的正常爬取过程中可能出现的
        # status列表中, 则认为代理无效, 切换代理
        if response.status == 200:
            if "proxy" in request.meta.keys():
                logger.info("使用代理[{}]成功爬取".format(request.meta['proxy']))

        if self.use_proxy:
            if response.status != 200 \
                    and (not hasattr(spider, "website_possible_httpstatus_list") \
                         or response.status not in spider.website_possible_httpstatus_list):
                logger.info("response status[%d] not in spider.website_possible_httpstatus_list" % response.status)
                self.change_proxy(request)
                new_request = request.copy()
                new_request.dont_filter = True
                return new_request
            else:
                return response
        else:
            return response

    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常
        """
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            logger.info("处理异常url，并更换代理重试")
            self.change_proxy(request)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request