from urllib.parse import urlsplit
import pandas as pd
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from bot_cotacao.spiders.spider_c_e_c import CecSpiderCotacao
from bot_cotacao.spiders.spider_leroy_merlin import LeroySpiderCotacao
from bot_cotacao.spiders.spider_telha_norte import TelhaNorteSpiderCotacao
from bot_cotacao.spiders.spider_yamamura import YamamuraSpiderCotacao
from bot_cotacao.spiders.spider_sodimac import SodimacSpiderCotacao
from join_scrapper import join_all_results

spyder_by_site = {
    'https://www.sodimac.com.br/': SodimacSpiderCotacao,
    'https://www.yamamura.com.br/': YamamuraSpiderCotacao,
    'https://www.cec.com.br/': CecSpiderCotacao,
    'https://www.leroymerlin.com.br/': LeroySpiderCotacao,
    'https://www.telhanorte.com.br/': TelhaNorteSpiderCotacao
}

skip_cols = ['Marca', 'Unidade', 'Preço', 'Loja', 'Link']

file_base = "Fast 2.0 v3 - banco preços.xlsx"

df = pd.read_excel(file_base, sheet_name='Preços', skiprows=1)
df.drop(columns=skip_cols, inplace=True)
df.dropna(subset='Produto', inplace=True)

links_by_site = {}
columns_by_site = df.filter(like='Link ').columns

for col in columns_by_site:
    aux_df = df[df[col] == df[col]][['Produto', col]]

    base_url = "{0.scheme}://{0.netloc}/".format(urlsplit(aux_df.iloc[0][1]))
    links_by_site.update({base_url: aux_df})

process = CrawlerProcess(get_project_settings())

if __name__ == '__main__':

    # Adiciona o spider ao processo do rastreador
    for site, df_links in links_by_site.items():
        spyder = spyder_by_site.get(site)
        if spyder:
            process.crawl(spyder, df_links)

    # Execute o processo do rastreador
    process.start()

    # Agrupa os resultados num único arquivo
    join_all_results()
