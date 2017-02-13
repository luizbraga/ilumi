# -*- coding: utf-8 -*-

XPATH = {
    'lista_urls': (
        '//ul[contains(@class, "resultado_da_busca")]//li'
    ),
    'paginacao': (
        '//a[@class="proximo fundo-cor-produto"]'
    ),
    'conteudo': (
        '//div[contains(@class, "materia-conteudo") or '
        'contains(@class, "corpo-materia") or '
        'contains(@class, "corpo")]'
        '//div//p'
    )
}
