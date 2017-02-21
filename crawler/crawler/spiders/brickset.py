# -*- coding: utf-8 -*-
import logging

import scrapy
from .utils import xpath_get
from ..items import BrickSetItem

from sets.models import BrickSet

logger = logging.getLogger()


class BricksetDotComThemeSpider(scrapy.Spider):
    name = 'brickset_theme'
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.BricksetDotComThemePipeline': 400}}
    allowed_domains = ['brickset.com']
    start_urls = ['http://brickset.com']

    def parse(self, response):
        bricksets = BrickSet.objects.filter(theme_title='')
        for brickset in bricksets:
            logger.info(brickset.brick_code)
            url = 'http://brickset.com/sets/' + brickset.brick_code + '-1'
            yield scrapy.Request(url, callback=self.parse_brickset, meta={'brickset': brickset})

    def parse_brickset(self, response):
        brickset = response.meta['brickset']
        item = BrickSetItem()
        item['brick_code'] = brickset.brick_code
        for link in response.xpath('//dd/a'):
            if link.xpath('@href').extract()[0].startswith('/sets/theme-'):
                theme_title = link.xpath('text()').extract()[0]
                if theme_title:
                    item['theme_title'] = theme_title.strip()
                    break
        yield item


class BricksetDotComPriceSpider(scrapy.Spider):
    name = 'brickset_price'
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.BricksetDotComPricePipeline': 400}}
    allowed_domains = ['brickset.com']
    start_urls = ['http://brickset.com']

    def parse(self, response):
        bricksets = BrickSet.objects.filter(official_price=None)
        for brickset in bricksets:
            logger.info(brickset.brick_code)
            url = 'http://brickset.com/sets/' + brickset.brick_code + '-1'
            yield scrapy.Request(url, callback=self.parse_brickset, meta={'brickset': brickset})

    def parse_brickset(self, response):
        brickset = response.meta['brickset']
        item = BrickSetItem()
        item['brick_code'] = brickset.brick_code
        for i in range(5, 13):
            rrp_text = xpath_get(response, '//dd[' + str(i) + ']/text()')
            for each in rrp_text.split(' '):
                if each.startswith('$'):
                    item['official_price'] = each.split('$')[1]
                    break
        yield item