from time import sleep
import openpyxl
import scrapy
from PIL.Image import LANCZOS
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline
from bot_cotacao.utils import BASE_DIR


class BotCotacaoPipeline:
    def __init__(self):
        self.workbook = openpyxl.Workbook()
        self.sheet = self.workbook.active
        self.sheet.append(
            ['Produto', 'ID', 'Site', 'Link', 'Disponibilidade', 'Preço Promoção', 'Preço Normal', 'Unidade']
        )
        # self.row = 1

    def process_item(self, item, spider):
        row_data = [
            item.get('Produto', ''),
            item.get('ID', ''),
            item.get('site', ''),
            item.get('link', ''),
            item.get('disponibilidade', 'Indisponível'),
            item.get('preco_promocao', ''),
            item.get('preco_normal', ''),
            item.get('unidade', '')

        ]
        self.sheet.append(row_data)
        # self.row += 1
        return item

    def close_spider(self, spider):
        sleep(3)
        self.workbook.save(f'{spider.name}_output.xlsx')


class ImagesPipelineProduct(ImagesPipeline):

    def get_media_requests(self, item, info):
        for images in item['imagens']:
            if images.get('image_url') is None or images.get('image_url') == '':
                raise DropItem("Item contains no images")
            yield scrapy.Request(images.get('image_url'))#, meta={'meta': images.copy()})

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        # adapter = ItemAdapter(item)
        # adapter['image_paths'] = image_paths

        for ok, result in results:
            if ok:
                image_path = result['path']
                full_path = (BASE_DIR.parent / info.spider.settings.get('IMAGES_STORE') / image_path)
                print(f"Caminho completo do arquivo de imagem: {full_path}")

                with self._Image.open(full_path) as image:
                    width, height = image.size
                    if width > 400:
                        # ratio = width / height
                        new_width = new_height = 400
                        # int(new_width / ratio)
                        image = image.resize((new_width, new_height), LANCZOS)
                        image.save(full_path, format=image.format)

        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        spider_name = info.spider.name.split('_spider')[0]
        data_image = item['imagens'][0]

        return f"{spider_name}/{item['ID']}_{item['Produto'].split()[0].upper()}{data_image['fmt']}"

