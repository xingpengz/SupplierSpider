# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class SupplierspiderItem(scrapy.Item):
    # define the fields for your item here like:
    country_id = scrapy.Field()
    name_foreign = scrapy.Field()
    name_en = scrapy.Field()
    foreign_keywords = scrapy.Field()
    english_keywords = scrapy.Field()
    office_phone = scrapy.Field()
    description_en = scrapy.Field()
    email = scrapy.Field()
    address_en = scrapy.Field()
    website = scrapy.Field()
    status = scrapy.Field()

