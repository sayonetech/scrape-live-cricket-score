import scrapy


class SayscoreItem(scrapy.Item):
    match_details = scrapy.Field()
