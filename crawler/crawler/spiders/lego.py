import logging

import scrapy
from scrapy_splash import SplashRequest

from ..items import ProductItem
from .utils import xpath_get

logger = logging.getLogger()

START_URL = 'https://shop.lego.com/en-US/New-Sets?S1=&callback=json&cc=us&do=json-db&i=1&jsonp=jsonCallback&count=100'


class LegoSpider(scrapy.Spider):
    name = 'lego'
    base_url = 'https://shop.lego.com/en-US'
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.ProductPipeline': 400}}
    start_urls = [START_URL, ]
    not_product_urls = ['http://shop.lego.com/en-US/Pick-A-Brick-11998',
                        'http://shop.lego.com/en-US/LEGO-Gift-Card-2853101',
                        'http://shop.lego.com/en-US/Reload-Gift-Card',
                        ]

    def parse(self, response: scrapy.http.Response):
        yield SplashRequest(self.start_urls[0], dont_filter=True, callback=self.parse_list, args={'wait': 3.0})

    def parse_list(self, response: scrapy.http.Response):
        urls = response.xpath("//a[@class='product-leaf__link-title']/@href").extract()
        for lego_url in urls:
            url = response.urljoin(lego_url)
            if url not in LegoSpider.not_product_urls:
                yield scrapy.Request(url, callback=self.parse_lego)
        next_page = xpath_get(response, "//*[@class='pagination__next']/@href")
        print(next_page)
        if next_page:
            next_url = response.urljoin(next_page)
            yield SplashRequest(next_url, callback=self.parse_list, args={'wait': 3.0})

    def parse_lego(self, response: scrapy.http.Response):
        product = ProductItem()
        product['title'] = xpath_get(response, "//*[@itemprop='name']/text()")
        product['product_code'] = xpath_get(response, "//*[@class='product-details__product-code']/text()")
        price_text = xpath_get(response, "//*[@class='product-price__list-price']/text()")
        if price_text:
            product['official_price'] = float(price_text[1:])
        product['official_image_url'] = xpath_get(response, "//*[@class='viewer-default-image']/img/@src")
        product['ages'] = xpath_get(response, "//*[@class='product-details__ages']/text()")
        product['pieces'] = xpath_get(response, "//*[@class='product-details__piece-count']/text()")
        product['marketing_text'] = xpath_get(response, "//*[@class='product-features__description']/p/text()")
        product['official_url'] = response.url
        breadcrumb_links = response.xpath("//*[@data-test='breadcrumb-link']/span/text()").extract()
        if len(breadcrumb_links) > 1:
            product['theme_title'] = breadcrumb_links[1]
        review_count_text = xpath_get(response, "//*[@class='overview__reviews']/text()")
        if review_count_text and len(review_count_text.split(' ')) > 1:
            product['official_review_count'] = int(review_count_text[0])
        rating_values = response.xpath("//*[@itemprop='aggregateRating']/*[@itemprop='ratingValue']/text()").extract()
        if rating_values and len(rating_values) > 1:
            product['official_rating'] = float(rating_values[1])
        yield product
