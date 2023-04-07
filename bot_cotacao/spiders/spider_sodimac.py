import json
import re
from abc import ABC
from urllib.parse import urlsplit, parse_qs, urlparse
import scrapy
from scrapy import Selector
from scrapy_splash import SplashRequest
from bot_cotacao.items import BotCotacaoItem
from bot_cotacao.utils import extract_image_info


def extract_data_layer(script_text):
    regex = r"(:?\{.*\})<\/script>"
    pattern = re.compile(regex, re.DOTALL)

    match = pattern.search(script_text)
    if match:
        json_str = match.group(1)
        json_str = json_str.replace('\n', '').replace('@', '')
        data = json.loads(json_str)
        return data
    else:
        return {}


class SodimacSpiderCotacao(scrapy.Spider, ABC):
    name = "sodimac_spider"
    allowed_domains = ['sodimac.com.br']

    def __init__(self, df_links=None, **kwargs):
        super().__init__(**kwargs)
        self.df = df_links.copy()
        self.start_urls = self.df[self.df.columns[1]].to_list()

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse, args={'wait': 10}, meta={'base_link': url})

    def parse(self, response, **kwargs):
        meta = response.meta.copy()
        sel = Selector(response=response)

        script_txt = sel.css('script#__NEXT_DATA__').get()

        data = extract_data_layer(script_txt)
        product_props = data['props']['pageProps']['productProps']
        product = product_props['result']['variants'][0]
        product_id = product.get('id')

        # fmt_img = parse_qs(urlparse(sel.css(f'#pdpMainImage-{product_id}::attr(src)').get()).query)['fmt'][0]
        meta['product_imgs'] = [sel.css(f'#pdpMainImage-{product_id}::attr(src)').get()]  # : f".{fmt_img}"}]

        url_api = 'https://www.sodimac.com.br/s/search/v2/sobr/product-details?productId={product_id}'
        yield SplashRequest(
            url_api.format(product_id=product_id), callback=self.parse_page_product, args={'wait': 10}, meta=meta
        )

    def parse_page_product(self, response, **kwargs):
        data_json = response.json().get('productDetailsJson')[0]

        item = BotCotacaoItem()

        item['Produto'] = \
        self.df[self.df['Link Sodimac'].str.startswith(response.meta.get('base_link'))]['Produto'].iloc[0]
        # disponivel = sel.xpath('//strong[starts-with(text(), "0") and contains(text(),"resultados")]').get()
        item['link'] = response.meta.get('base_link')

        first_image_url = response.meta.get('product_imgs')[0]

        fmt_img = f".{parse_qs(urlparse(first_image_url).query)['fmt'][0]}"

        image_url = "{0.scheme}://{0.netloc}{0.path}".format(urlsplit(first_image_url))

        item['site'] = "{0.scheme}://{0.netloc}/".format(urlsplit(response.url))


        file_name, _ = extract_image_info(image_url)

        item['imagens'] = [{'image_url': image_url, 'fmt': fmt_img, 'file_name': file_name}]

        item['ID'] = data_json.get('productId', '')

        item['preco_normal'] = data_json.get('NORMAL', '')
        item['preco_promocao'] = data_json.get('EVENT', data_json.get('NORMAL', ''))
        item['unidade'] = data_json.get('PriceFormat', '').lower()

        if item['preco_normal'] != '':
            item['disponibilidade'] = "Disponível"

        yield item
