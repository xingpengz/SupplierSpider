import copy
import json
import re

import requests
import scrapy
from scrapy import FormRequest

from SupplierSpider.items import SupplierspiderItem


class AnphabeSpider(scrapy.Spider):
    name = 'anphabe'
    allowed_domains = ['anphabe.com']

    def start_requests(self):
        return [FormRequest(
            "https://company.vietnambestplacestowork.com/api/export-company-award/top100/2021?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx",
            callback=self.parse,
            dont_filter=True
        )]

    def parse(self, response):
        item = SupplierspiderItem()
        info = response.text
        info = json.loads(info)
        for i in info:
            if i['name']:
                item['name_foreign'] = i['name']
                item['name_en'] = i['name']
            if i['portal_url']:
                item['website'] = i['portal_url']
            elif i['company_website']:
                item['website'] = i['company_website']
            item['description_en'] = i['description']
            yield scrapy.Request(url=item['website'], dont_filter=True, callback=self.parse_detail, meta={'item': copy.deepcopy(item)})

    def parse_detail(self, response):
        item = response.meta['item']
        item['country_id'] = 2
        keywords = response.xpath('//*[@id="block-company-company-information"]/div/div/div/div/div/div/ul/li[3]/div/div[2]/text()').extract()
        if keywords:
            item['english_keywords'] = keywords
            item['foreign_keywords'] = keywords
        item['email'] = ''
        phone = response.xpath('//*[@id="block-company-company-information"]/div/div/div/div/div/div/ul/li[5]/p[2]/text()').extract()
        if phone:
            item['office_phone'] = phone
        else:
            item['office_phone'] = ''
        address = response.xpath('//*[@id="block-company-company-information"]/div/div/div/div/div/div/ul/li[5]/p[1]/span/text()').extract()
        if address:
            item['address_en'] = address
        else:
            item['address_en'] = ''
        if item['website']:
            item['status'] = 110
        else:
            item['status'] = 5
        yield item


