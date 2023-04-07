import json
import re
from abc import ABC
from urllib.parse import urlsplit
import scrapy
from scrapy import Selector
from scrapy_splash import SplashRequest
from bot_cotacao.items import BotCotacaoItem
from bot_cotacao.utils import extract_image_info


def convert_str_price_to_float(integer: str, decimals: str):
    integer = str(integer).replace('.', '')
    decimals = str(decimals).replace('.', '')
    return float(f'{integer}.{decimals}')


class LeroySpiderCotacao(scrapy.Spider, ABC):
    name = "leroy_merlin_spider"

    def __init__(self, df_links=None, **kwargs):
        super().__init__(**kwargs)
        self.df = df_links.copy()
        self.start_urls = df_links[df_links.columns[1]].to_list()
        self.splash_args = {'wait': 10}

        self.regex = r"\[.*}}]"

    def extract_data_layer(self, script_text):

        pattern = re.compile(self.regex, re.MULTILINE | re.DOTALL)

        # Use the regular expression to extract the JSON object
        match = pattern.search(script_text.replace('&quot;', '\"'))
        if match:
            json_str = match.group(0)
            data = json.loads(json_str)  # Convert the string to a dictionary
            return data
        else:
            return {}

    allowed_domains = ['leroymerlin.com.br']

    def start_requests(self):

        # yield SplashRequest(main_url, self.parse, args={'wait': 0.5})
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_page, args=self.splash_args, meta={'base_link': url})

    def parse_page(self, response, **kwargs):
        sel = Selector(response=response)
        item = BotCotacaoItem()
        item['Produto'] = self.df[self.df['Link Leroy'].str.startswith(response.meta.get('base_link'))]['Produto'].iloc[0]
        item['link'] = response.url
        item['site'] = "{0.scheme}://{0.netloc}/".format(urlsplit(response.url))
        product_id = sel.css('.item > div.badge-product-code::attr(content)').get()
        item['ID'] = product_id
        item['disponibilidade'] = 'Indisponível'

        data_product_by_id = response.css(f".wrapper-padding[data-product-id='{product_id}']")

        dict_product_by_id = json.loads(data_product_by_id.attrib.get('data-skus'))

        # nesse caso existe imagem do produto ainda que o produto esteja indisponível
        image_url = data_product_by_id.xpath('//img/@src').get()
        file_name, fmt_img = extract_image_info(image_url)

        item['imagens'] = [{'image_url': image_url, 'fmt': fmt_img, 'file_name': file_name}]

        qtd_de_precos = len(dict_product_by_id)
        if dict_product_by_id[0].get('price').get('to') is not None:

            unit = sel.css('div.product-price-tag > div::attr(data-unit)').extract_first()
            matchs_prices = self.extract_data_layer(data_product_by_id.extract_first())

            product_price_tag = sel.css('div.product-price-tag').xpath(".//div[@class='price-tag-wrapper']")

            preco_normal_real = product_price_tag.attrib.get("data-from-price-integers", 0)
            preco_normal_cents = product_price_tag.attrib.get("data-from-price-decimals", 0)

            preco_normal = convert_str_price_to_float(preco_normal_real, preco_normal_cents)

            preco_promocao = preco_normal

            if matchs_prices:
                # Decide pelo menor preço quando o produto tem preços diferentes a depender da loja parceira.
                min_price = min(
                    matchs_prices,
                    key=lambda p: convert_str_price_to_float(p['price']['to']['integers'], p['price']['to']['decimals'])

                )
                preco_promocao = convert_str_price_to_float(min_price['price']['to']['integers'],
                                                            min_price['price']['to']['decimals'])

            preco_normal = preco_normal if preco_promocao <= preco_normal else preco_promocao

            item['preco_promocao'] = preco_promocao
            item['preco_normal'] = preco_normal
            item['unidade'] = unit
            if item['preco_normal'] != '':
                item['disponibilidade'] = 'Disponível'

        yield item
