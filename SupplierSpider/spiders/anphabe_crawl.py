import copy
import hashlib, json, os
import scrapy
from scrapy import FormRequest
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule


class AnphabeCrawlSpider(CrawlSpider):
    name = 'anphabe_crawl'
    # allowed_domains = ['anphabe.com']
    start_urls = ['https://company.vietnambestplacestowork.com/api/export-company-award/top100/2021?x_auth_token=AwHBFADBohjsnZj6lK7yRM9lI1OH5EZx']

    def parse_start_url(self, response):
        info = json.loads(response.text)
        for i in info:
            name = i['name']
            description_en = i['description']
            if i['portal_url']:
                website = i['portal_url']
            elif i['company_website']:
                website = i['company_website']
            if name:
                supplier = {}
                supplier['country_id'] = 2
                supplier['name_foreign'] = name
                supplier['name_en'] = name
                if description_en:
                    supplier['description_en'] = description_en
                if website:
                    supplier['website'] = website
                    supplier['status'] = 110
                else:
                    supplier['website'] = response.url
                    supplier['status'] = 5
                yield scrapy.Request(url=website, dont_filter=True, callback=self.parse_item, meta={'supplier': copy.deepcopy(supplier)})

    # rules = (
    #     Rule(LinkExtractor(allow=r'http.*?com\\/'), callback='parse_item'),
    # )

    def parse_item(self, response):
        supplier = response.meta.get('supplier')
        keyword = response.xpath('//*[@id="block-company-company-information"]/div/div/div/div/div/div/ul/li[3]/div/div[2]/text()').extract_first()
        if keyword and isinstance(keyword, list):
            keyword = keyword[-1]
        supplier['keyword'] = keyword
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
