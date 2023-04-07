import json
import re
from abc import ABC
from urllib.parse import urlsplit, urlparse, parse_qs
from scrapy import Selector
import scrapy
from scrapy_splash import SplashRequest
from bot_cotacao.items import BotCotacaoItem
from bot_cotacao.utils import extract_image_info


def extract_data_layer(script_text):
    # Define the regular expression to extract the JSON object
    pattern = re.compile(r'dataLayer.push\((.*?)\);', re.DOTALL)

    # Use the regular expression to extract the JSON object
    match = pattern.search(script_text)
    if match:
        json_str = match.group(1)
        data = json.loads(json_str)  # Convert the string to a dictionary
        return data
    else:
        return {}


class CecSpiderCotacao(scrapy.Spider, ABC):
    name = "cec_spider"

    def __init__(self, df_links=None, **kwargs):
        super().__init__(**kwargs)
        self.df = df_links.copy()
        self.start_urls = df_links[df_links.columns[1]].to_list() # ['https://www.cec.com.br/metais-e-acessorios/assentos/assento-sanitario-em-polipropileno-soft-close-suite-branco?produto=1289759', ]

    # allowed_domains = ['cec.com.br']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_page_category, args={'wait': 10}, meta={'base_link': url})

    def parse_page_category(self, response, **kwargs):
        item = BotCotacaoItem()
        sel = Selector(response=response)
        item['link'] = response.meta.get('base_link')
        item['disponibilidade'] = 'Indisponível'
        item['site'] = "{0.scheme}://{0.netloc}/".format(urlsplit(response.url))
        parsed_url = urlparse(item['link'])
        query_params = parse_qs(parsed_url.query)
        item['ID'] = query_params['produto'][0]
        item['Produto'] = self.df[self.df['Link C&C'].str.startswith(response.meta.get('base_link'))]['Produto'].iloc[0]

        item['imagens'] = [{'image_url': '', 'fmt': '', 'file_name': ''}]

        if response.url.find('produto-indisponivel') == -1:  # produto ao menos existe no site

            match = extract_data_layer(response.text)
            item['ID'] = match.get('productId', '')

            preco_normal = match.get('productPriceFrom', 0.0)
            preco_promocao = match.get('productPriceTo', 0.0)

            preco_normal = preco_promocao if preco_normal < preco_promocao else preco_normal

            # item['preco_promocao'] = item['preco_normal'] = item['unidade'] = ''
            if not sel.xpath(".//h5[text()='Produto Indisponível']/text()").get():
                image_url = sel.css(
                    'div.product-figure div.product-img-zoom img#Body_Body_imgStandardAB::attr(data-zoom-image)'
                ).get()
                file_name, fmt_img = extract_image_info(image_url)
                item['imagens'] = [{'image_url': image_url, 'fmt': fmt_img, 'file_name': file_name}]

                item['disponibilidade'] = 'Disponível'
                item['preco_promocao'] = preco_promocao
                item['preco_normal'] = preco_normal
                item['unidade'] = sel.css('.product-price > .price span::text').get('')
            else:
                ...
        else:
            ...
        yield item
