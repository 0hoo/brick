# -*- coding: utf-8 -*-
import logging

import scrapy
from scrapy.spiders.init import InitSpider
from scrapy.http import FormRequest

from ..items import BricklinkRecordItem
from .utils import xpath_get_price

from products.models import Product

logger = logging.getLogger()


class BricklinkSpider(InitSpider):
    name = 'bricklink'
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.BricklinkPipeline': 400}}
    allowed_domains = ['bricklink.com']
    start_urls = ['http://www.bricklink.com/com']

    def init_request(self):
        yield FormRequest(url='https://www.bricklink.com/ajax/renovate/login.ajax',
                          formdata={'userid': '0hoo', 'password': 'y732621h', 'override': 'false'},
                          callback=self.after_login)

    def after_login(self, response):
        return self.initialized()

    def parse(self, response):
        for product in Product.objects.all():
            logger.info(product.product_code)
            url = 'http://www.bricklink.com/catalogPG.asp?S=' + product.product_code + '-1'
            yield scrapy.Request(url, callback=self.parse_price, dont_filter=True, meta={'product': product})

    def parse_price(self, response: scrapy.http.Response):
        item = BricklinkRecordItem()
        item['bricklink_url'] = response.url
        item['product'] = response.meta['product']
        new_rows = response.xpath("//table[@id='id-main-legacy-table']/tr/td/table[3]/tr[3]/td[3]/table//table/tr")
        if len(new_rows) > 0:
            item['new_min_price'] = xpath_get_price(new_rows[2], "td/b/text()")
            item['new_average_price'] = xpath_get_price(new_rows[3], "td/b/text()")
            item['new_max_price'] = xpath_get_price(new_rows[5], "td/b/text()")

        used_rows = response.xpath("//table[@id='id-main-legacy-table']/tr/td/table[3]/tr[3]/td[4]/table//table/tr")
        if len(used_rows) > 0:
            item['used_min_price'] = xpath_get_price(used_rows[2], "td/b/text()")
            item['used_average_price'] = xpath_get_price(used_rows[3], "td/b/text()")
            item['used_max_price'] = xpath_get_price(used_rows[5], "td/b/text()")

        yield item
