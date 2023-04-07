# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BotCotacaoItem(scrapy.Item):
    # define the fields for your item here like:
    Produto = scrapy.Field()
    ID = scrapy.Field()
    site = scrapy.Field()
    link = scrapy.Field()
    disponibilidade = scrapy.Field()
    preco_promocao = scrapy.Field()
    preco_normal = scrapy.Field()
    unidade = scrapy.Field()
    imagens = scrapy.Field()
