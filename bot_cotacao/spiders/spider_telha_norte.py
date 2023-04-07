import re
from abc import ABC
from urllib.parse import urlsplit
import scrapy
from scrapy_splash import SplashRequest

from bot_cotacao.items import BotCotacaoItem
from bot_cotacao.utils import extract_image_info


class TelhaNorteSpiderCotacao(scrapy.Spider, ABC):
    name = "telha_norte_spider"

    def __init__(self, df_links=None, **kwargs):
        super().__init__(**kwargs)
        self.base_url = 'https://www.telhanorte.com.br/api/catalog_system/pub/products/search/?fq=productId:{}'
        self.df = df_links.copy()
        self.start_urls = df_links[df_links.columns[1]].to_list()

    def start_requests(self):

        for url in self.start_urls:
            regex = r"(?:(\d+))\/p"
            product_id = re.search(regex, url).group(1)

            yield SplashRequest(self.base_url.format(product_id), self.parse_page_category, args={'wait': 10},
                                meta={'base_link': url})

    def parse_page_category(self, response, **kwargs):
        item = BotCotacaoItem()

        data = response.json()[0]
        item_data = data['items'][0]
        image_url = item_data['images'][0]['imageUrl']
        file_name, fmt_img = extract_image_info(image_url)

        item['imagens'] = [{'image_url': image_url, 'fmt': fmt_img, 'file_name': file_name}]

        item['Produto'] = self.df[self.df['Link Telhanorte'].str.startswith(response.meta.get('base_link'))]['Produto'].iloc[0]
        # response.meta.get('base_link')]
        item['ID'] = data.get('productId')
        item['link'] = data.get('link')
        item['site'] = "{0.scheme}://{0.netloc}/".format(urlsplit(response.url))
        items = data.get('items')[0]
        sellers = items.get('sellers')
        first_seller = sellers[0]
        commertial_offer = first_seller.get('commertialOffer')
        price = commertial_offer.get('Price')

        list_price = commertial_offer.get('ListPrice')
        if price <= list_price:
            item['preco_normal'] = list_price
            item['preco_promocao'] = price
        else:
            item['preco_normal'] = price
            item['preco_promocao'] = list_price
        item['unidade'] = items.get('measurementUnit')

        item['disponibilidade'] = 'Disponível' if commertial_offer.get('IsAvailable') else ''

        # Omite os preços caso o produto esteja indisponível
        if item['disponibilidade'] == '':
            item['preco_promocao'] = ''
            item['preco_normal'] = ''
            item['unidade'] = ''

        yield item
