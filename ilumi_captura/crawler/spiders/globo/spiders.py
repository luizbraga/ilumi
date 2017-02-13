# -*- coding: utf-8 -*-

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request

from crawler.spiders.globo.constants import XPATH
from crawler.loaders import NoticiaLoader


class GloboSpider(CrawlSpider):
    name = 'captura-globo'
    start_urls = ['http://www.globo.com/busca']
    fonte = 'globo'
    pagina = 1

    def __init__(self, individuo='', *args, **kwargs):
        super(GloboSpider, self).__init__(*args, **kwargs)
        self.individuo = individuo

    def parse(self, response):
        self.url_busca = response.url + '/?q={}'.format(self.individuo)

        yield Request(
            url=self.url_busca,
            method='GET',
            callback=self.obter_links
        )

    def obter_links(self, response):
        for link in response.xpath(XPATH['lista_urls']):
            # Obter conteudo das noticias
            yield Request(
                url='http:'+link.xpath('.//@href').extract()[0],
                method='GET',
                callback=self.get_real_url)

        paginacao = response.xpath(XPATH['paginacao'])
        if paginacao:
            self.pagina += 1
            yield Request(
                url=self.url_busca+'&page={}'.format(self.pagina),
                method='GET',
                callback=self.obter_links)

    def get_real_url(self, response):
        real_url = response.xpath(
            '//meta[contains(@content, "http")]/@content').extract()[0]

        if real_url:
            headers = {
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': (
                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) '
                    'AppleWebKit/537.36 (KHTML, like Gecko) '
                    'Chrome/53.0.2785.143 Safari/537.36'),
                'Referer': response.url,
                'Accept': ('text/html,application/xhtml+xml,'
                           'application/xml;q=0.9,image/webp,*/*;q=0.8'),
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'en-US,en;q=0.8,pt;q=0.6',
            }
            yield Request(
                url=real_url.partition('URL=')[-1].replace('\'', ''),
                method='GET',
                headers=headers,
                callback=self.extrair_noticia)

    def extrair_noticia(self, response):
        if ('examenegocios' not in response.url and
            'epocanegocios' not in response.url and
            'videos' not in response.url and
            'opiniao' not in response.url and
            'globoplay' not in response.url and
            'blog' not in response.url and
                'mimimi' not in response.url):
            noticia = NoticiaLoader(selector=response)
            noticia.add_value('url', response.url)

            if 'epoca' in response.url:
                noticia.add_value('fonte', 'epoca')
                if 'epocanegocios' in response.url:
                    noticia.add_xpath(
                        'titulo', '//h1[@class="titulo"]/text()')
                    noticia.add_xpath(
                        'data_publicacao',
                        '//p[@class="data"]/text()')
                    noticia.add_value(
                        'autor', '')
                    noticia.add_xpath(
                        'conteudo',
                        '//article[@class="conteudo"]/p')
                else:
                    titulo = response.xpath(
                        '//h1[@class="titulo-item"]/text()'
                        ).extract()[0].strip()
                    titulo = titulo + ' - ' + response.xpath(
                        '//h3[@class="chamada"]/text()'
                        ).extract()[0].strip()
                    autor = response.xpath(
                        '//div[@class="autor"]/text()'
                        ).extract()[0].strip()
                    conteudo = ''.join(
                        response.xpath(XPATH['conteudo']).extract())
                    data_publicacao = ' '.join(response.xpath(
                        '//div[@class="data"]/text()'
                        ).extract()[0].strip().split(
                            ' - ')[:2])

                    noticia.add_value('titulo', titulo)
                    noticia.add_value('autor', autor)
                    noticia.add_value('conteudo', conteudo)
                    noticia.add_value('data_publicacao', data_publicacao)
                yield noticia.load_item()
            # elif 'extra.globo.com':
            #     noticia.add_value('fonte', 'extra')
            #     noticia.add_xpath(
            #         'titulo', '//h1[@property="na:headline"]/text()')
            #     noticia.add_xpath(
            #         'data_publicacao',
            #         '//time[@property="na:datePublished"]/text()')
            #     noticia.add_xpath(
            #         'autor', '//span[@class="author"]/text()')
            #     noticia.add_xpath(
            #         'conteudo',
            #         '//div[@class="story"]/p')
            #     yield noticia.load_item()
            elif 'g1' in response.url:
                noticia.add_value('fonte', 'g1')

                if 'globo.com/politica' in response.url:
                    noticia.add_xpath(
                        'titulo', '//h1[@class="content-head__title"]/text()')
                    noticia.add_xpath(
                        'data_publicacao',
                        '//time[@itemprop="datePublished"]/text()')
                    noticia.add_xpath(
                        'autor', '//span[@itemprop="creator"]/text()')
                    noticia.add_xpath(
                        'conteudo',
                        '//p[contains(@class, "content-text__container")]')
                elif 'globo.com/economia/' in response.url:
                    noticia.add_xpath(
                        'titulo', '//h1[@class="content-head__title"]')
                    noticia.add_xpath(
                        'conteudo',
                        '//p[contains(@class, "content-text__container")]')
                    noticia.add_xpath(
                        'autor',
                        '//span[@itemprop="creator"]/text()')
                    noticia.add_xpath(
                        'data_publicacao',
                        '//time[@itemprop="datePublished"]/text()')
                else:
                    noticia.add_xpath(
                        'titulo', '//h1[@class="entry-title"]')
                    noticia.add_xpath(
                        'data_publicacao', '//abbr[@class="published"]/text()')

                    if 'jornal-nacional' in response.url:
                        noticia.add_xpath(
                            'conteudo',
                            '//div[contains(@class, "materia-conteudo")]/p')
                        noticia.add_value(
                            'autor', '')
                    elif 'bom-dia-brasil' in response.url:
                        noticia.add_xpath(
                            'conteudo',
                            '//div[contains(@class, "materia-conteudo")]//p')
                        noticia.add_value(
                            'autor', '')
                    elif 'hora1' in response.url:
                        noticia.add_xpath(
                            'conteudo',
                            '//div[contains(@class, "materia-conteudo")]/p')
                        noticia.add_xpath(
                            'autor',
                            '//p[@class="vcard author"]//strong/text()')
                    elif 'jornal-da-globo' in response.url:
                        noticia.add_value(
                            'autor', '')
                        noticia.add_xpath(
                            'conteudo',
                            '//div[contains(@class, "materia-conteudo")]/p')
                    else:
                        noticia.add_xpath(
                            'autor', '//p[@class="vcard author"]//strong')
                        noticia.add_xpath(
                            'conteudo', '//div[@id="materia-letra"]//p')
                yield noticia.load_item()

            elif 'oglobo' in response.url:
                noticia.add_xpath(
                    'titulo', '//div[@class="head-materia"]//h1/text()')
                noticia.add_xpath(
                    'conteudo',
                    '//div[contains(@class, "corpo")]/p/text()')
                noticia.add_xpath(
                    'data_publicacao',
                    '//span[@class="data-cadastro"]/time/text()')
                noticia.add_xpath(
                    'autor',
                    '//span[@class="autor"]/text()')
                noticia.add_value('fonte', 'oglobo')

                yield noticia.load_item()
