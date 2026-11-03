# WebScrapingCatalogue

Catálogo de produtos do https://scrapingsandbox.com/ feito com Flask,
requests e BeautifulSoup.

## Como rodar

    pip install -r requirements.txt
    python main.py

Depois abra http://127.0.0.1:5000 no navegador.

A primeira pesquisa demora um pouco, porque o programa lê 100 páginas
do site (o progresso aparece no terminal). As próximas pesquisas são
instantâneas, porque os produtos ficam salvos na memória.
