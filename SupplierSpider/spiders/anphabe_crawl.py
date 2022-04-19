import copy
import hashlib, json, os
import re
from urllib.parse import urlparse

import scrapy
from scrapy import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class AnphabeCrawlSpider(CrawlSpider):
    name = 'anphabe_crawl'
    # allowed_domains = ['anphabe.com']
    start_urls = ['https://company.vietnambestplacestowork.com/api/export-company-award/top100/2021?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx']

    def _parse(self, response, **kwargs):
        start_urls = [
            'https://company.vietnambestplacestowork.com/api/export-company-award/top100/2021?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx',
            'https://company.vietnambestplacestowork.com/api/export-company-award/top100/2020?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx',
            'https://company.vietnambestplacestowork.com/api/export-company-award/top100/2018?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx',
            'https://company.vietnambestplacestowork.com/api/export-company-award/top100/2017?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx',
            'https://company.vietnambestplacestowork.com/api/export-company-award/top100/2016?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_start_url)

    def parse_start_url(self, response):
        info = json.loads(response.text)
        for i in info:
            name = i['name']
            description_en = i['description']
            if i['portal_url']:
                url = i['portal_url']
            elif i['company_website']:
                url = i['company_website']
            else:
                continue
            if name:
                supplier = {}
                supplier['country_id'] = 42 # Vietnam
                supplier['name_foreign'] = name
                supplier['name_en'] = name
                if description_en:
                    supplier['description_en'] = description_en
                yield scrapy.Request(url=url, dont_filter=True, callback=self.parse_item, meta={'supplier': copy.deepcopy(supplier)})

    # rules = (
    #     Rule(LinkExtractor(allow=r'http.*?com\\/'), callback='parse_item'),
    # )

    def parse_item(self, response):
        supplier = response.meta.get('supplier')
        keyword = response.xpath('//*[@id="block-company-company-information"]/div/div/div/div/div/div/ul/li[3]/div/div[2]/text()').extract_first()
        website = response.xpath('//*[@id="block-company-company-information"]/div/div/div/div/div/div/ul/li[4]/div/div[2]/a/@href').extract_first()
        if website and 'http' in website:
            parsed_result = urlparse(website)
            if parsed_result and parsed_result.netloc:
                website = parsed_result.netloc
                supplier['website'] = website
                supplier['status'] = 110
        else:
            supplier['website'] = response.url
            supplier['status'] = 5
        if keyword:
            supplier['foreign_keywords'] = keyword
            supplier['english_keywords'] = supplier['foreign_keywords']
        address = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Address')]/..)").extract_first()
        if not address:
            address = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Head Office')]/..)").extract_first()
        if not address:
            address = response.xpath("string(//li[@class='last']/p/strong[contains(text(), 'Address')]/..)").extract_first()
        if not address:
            address = response.xpath("string(//li[@class='last']/p/b[contains(text(), ' Ho Chi Minh')]/..)").extract_first()
        if not address:
            address = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Ho Chi Minh Office')]/..)").extract_first()
        if not address:
            address = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Địa')]/..)").extract_first()
        if not address:
            address = response.xpath("//li[@class='last']/p/span[contains(text(), 'Address')]/text()").extract_first()
        if address and ':' in address:
            address = address.split(':')[-1]
            if address:
                address = address.strip()
                supplier['address_en'] = address
        elif address and 'Address' in address:
            address = address.split('Address')[-1]
            if address:
                address = address.strip()
                supplier['address_en'] = address
        elif address and 'Địa chỉ' in address:
            address = address.split('Địa chỉ')[-1]
            if address:
                address = address.strip()
                supplier['address_en'] = address
        elif address and 'Head Office' in address:
            address = address.split('Head Office')[-1]
            if address:
                address = address.strip()
                supplier['address_en'] = address
        elif address and 'Ho Chi Minh' in address:
            address = address.split('Ho Chi Minh')[-1]
            if address:
                address = address.strip()
                supplier['address_en'] = address
        elif address and 'Ho Chi Minh Office' in address:
            address = address.split('Ho Chi Minh Office')[-1]
            if address:
                address = address.strip()
                supplier['address_en'] = address
        office_phone = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Telephone')]/..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("string(//li[@class='last']/p/b/b[contains(text(), 'Tel')]/../..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Tel')]/..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Đt')]/..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("string(//li[@class='last']/p/strong[contains(text(), 'Tel')]/..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("string(//li[@class='last']/p/b[contains(text(), 'Điện')]/..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("string(//li[@class='last']/p/span/b[contains(text(), 'Telephone')]/..)").extract_first()
        if not office_phone:
            office_phone = response.xpath("//li[@class='last']/p/span[contains(text(), 'Tel')]/text()").extract_first()
        if not office_phone:
            office_phone = response.xpath("//li[@class='last']/p/b[contains(text(), 'Phone')]/text()").extract_first()
        if not office_phone:
            office_phone = response.xpath("//li[@class='last']/p[contains(text(), 'Tel')]/text()").extract_first()
        if office_phone and ':' in office_phone:
            office_phone = office_phone.split(':')[-1]
            if office_phone:
                office_phone = office_phone.strip()
                supplier['office_phone'] = office_phone
        elif office_phone and 'Tel' in office_phone:
            office_phone = office_phone.split('Tel')[-1]
            if office_phone:
                office_phone = office_phone.strip()
                supplier['office_phone'] = office_phone
        elif office_phone and 'Telephone' in office_phone:
            office_phone = office_phone.split('Telephone')[-1]
            if office_phone:
                office_phone = office_phone.strip()
                supplier['office_phone'] = office_phone
        elif office_phone and 'Điện thoại' in office_phone:
            office_phone = office_phone.split('Điện thoại')[-1]
            if office_phone:
                office_phone = office_phone.strip()
                supplier['office_phone'] = office_phone
        elif office_phone and 'Phone' in office_phone:
            office_phone = office_phone.split('Phone')[-1]
            if office_phone:
                office_phone = office_phone.strip()
                supplier['office_phone'] = office_phone
        elif office_phone and 'Đt' in office_phone:
            office_phone = office_phone.split('Đt')[-1]
            if office_phone:
                office_phone = office_phone.strip()
                supplier['office_phone'] = office_phone
        self.supplier_to_json(self.name, response.url, supplier)
        yield supplier

    def supplier_to_json(self, spidername, url, supplier):
        dirname = spidername+'_suppliers/'
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        md5 = hashlib.md5()
        md5.update(url.encode("utf-8"))
        hash_str = md5.hexdigest()
        filename = dirname+hash_str+".json"
        with open(filename, 'w') as f:
            json.dump( supplier, f, ensure_ascii=False)
