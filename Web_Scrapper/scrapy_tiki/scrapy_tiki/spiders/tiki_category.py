# -*- coding: utf-8 -*-
import scrapy
from ..items import ScrapyTikiCategory

class TikiCategorySpider(scrapy.Spider):
    name = 'tiki_category'
    start_urls = ['https://tiki.vn/dien-thoai-may-tinh-bang/c1789?src=c.1789.hamburger_menu_fly_out_banner']
    def parse(self, response):
        categories = ScrapyTikiCategory()
        link = response.css('.title').css('::attr(href)').extract()
        #name = response.css('.product-box-list .title').css('::text').extract()
        #price = response.css('.product-box-list .final-price').css('::text').extract()
        #categories['name']=name
        categories['link']=link
        #categories['price']=price
        yield categories


