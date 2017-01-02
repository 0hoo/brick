import logging
import scrapy

from ..items import EbayRecordItem
from .utils import xpath_get_price

from products.models import Product
from items.models import Item

logger = logging.getLogger()


class EbaySpider(scrapy.Spider):
    name = 'ebay'
    custom_settings = {'ITEM_PIPELINES': {'crawler.pipelines.EbayPipeline': 400}}
    allowed_domains = ['ebay.com']
    start_urls = ['http://www.ebay.com']

    def parse(self, response):
        product_codes = Item.objects.order_by().values_list('product__product_code', flat=True).distinct()
        for product_code in product_codes:
            product = Product.objects.get(product_code=product_code)
            product.ebay_item_set.all().delete()
            logger.info(product_code)
            url = 'http://www.ebay.com/sch/i.html?_from=R40&_nkw=lego+' + product_code + '&_sacat=0'
            yield scrapy.Request(url, callback=self.parse_search_list, meta={'product': product})

    def parse_search_list(self, response):
        links = response.xpath("//div[@id='ResultSetItems']/ul/li//h3[@class='lvtitle']/a/@href").extract()
        product = response.meta['product']
        for link in links:
            yield scrapy.Request(link, callback=self.parse_ebay_item, meta={'product': product})

    def parse_ebay_item(self, response):
        item = EbayRecordItem()
        item['product'] = response.meta['product']
        item['link'] = response.url
        item['title'] = response.xpath("//h1[@class='it-ttl']/text()").extract()[0]
        item['used'] = response.xpath("//div[@itemprop='itemCondition']/text()").extract()[0].upper() != 'NEW'

        currency = response.xpath("//span[@itemprop='priceCurrency']/@content").extract()
        if len(currency) > 0:
            if currency[0].upper() == 'USD':
                item['price'] = xpath_get_price(response, "//span[@itemprop='price']/text()")
            else:
                item['price'] = xpath_get_price(response, "//span[@id='convbinPrice']/text()") \
                                or xpath_get_price(response, "//span[@id='convbidPrice']/text()")
        else:
            item['price'] = xpath_get_price(response, "//span[@id='mm-saleDscPrc']/text()")

        yield item
