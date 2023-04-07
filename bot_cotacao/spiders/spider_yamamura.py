import re
from abc import ABC
from urllib.parse import urlsplit
import scrapy
from scrapy import Selector
from scrapy_splash import SplashRequest
from bot_cotacao.items import BotCotacaoItem
from bot_cotacao.utils import extract_image_info


class YamamuraSpiderCotacao(scrapy.Spider, ABC):
    name = "yamamura_spider"
    allowed_domains = ['yamamura.com.br']

    def __init__(self, df_links=None, **kwargs):
        super().__init__(**kwargs)
        self.df = df_links.copy()
        self.start_urls = df_links[df_links.columns[1]].to_list()[:10]

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_page_category, args={'wait': 10}, meta={'base_link': url})

    def parse_page_category(self, response, **kwargs):
        sel = Selector(response=response)
        item = BotCotacaoItem()

        image_url = sel.css('img.image.Image::attr(src)').get()

        file_name, fmt_img = extract_image_info(image_url)

        item['imagens'] = [{'image_url': image_url, 'fmt': fmt_img, 'file_name': file_name}]

        item['Produto'] = \
            self.df[
                self.df[
                    'Link Yamamura (Apenas para produtos Yamamura)'
                ].str.startswith(response.meta.get('base_link'))]['Produto'].iloc[0]
        disponivel = sel.xpath('//strong[starts-with(text(), "0") and contains(text(),"resultados")]').get()
        item['link'] = response.url
        item['site'] = "{0.scheme}://{0.netloc}/".format(urlsplit(response.url))
        item['unidade'] = item['ID'] = item['preco_promocao'] = item['preco_normal'] = item['disponibilidade'] = ''

        if disponivel is None:
            price_container = sel.css('div.priceContainer')

            sale_price = re.findall(r'\d+', price_container.css('strong.sale-price span::text').get())

            instant_price = re.findall(r'\d+', price_container.css('span.instant-price::text').get())

            preco_normal = float(''.join(sale_price)) / 100.0
            preco_promocao = float(''.join(instant_price)) / 100.0

            product_id = sel.css('span.fabricante > b::text').get()
            item['ID'] = product_id

            item['preco_promocao'] = preco_promocao
            item['preco_normal'] = preco_normal
            item['unidade'] = 'un'
            item['disponibilidade'] = "Disponível"  # '' if disponivel is None else "Disponível"

        yield item
