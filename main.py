from bs4 import BeautifulSoup
from flask import Flask, render_template, request
import requests
import time


app = Flask(__name__)

# Quantidade de produtos que serão lidos do site
QTD_PAGINAS = 100

# Guarda os produtos depois da primeira coleta
produtos_salvos = []

# Faz o site achar que o acesso vem de um navegador
CABECALHO = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"}


# Baixa uma página, tentando até 3 vezes se der erro
def baixar(link):
    for tentativa in range(1, 4):
        try:
            resposta = requests.get(link, headers=CABECALHO, timeout=10)
            if resposta.status_code == 200:
                return resposta
            print(f"  {link} respondeu {resposta.status_code} (tentativa {tentativa} de 3)")
        except requests.RequestException as erro:
            print(f"  Falha ao acessar {link}: {erro} (tentativa {tentativa} de 3)")
        time.sleep(2 * tentativa)
    return None


# Lê os 24 produtos da página inicial
def ler_pagina_inicial():
    produtos = []
    url = "https://scrapingsandbox.com/"
    resposta = baixar(url)
    if resposta is not None:
        soup = BeautifulSoup(resposta.text, "html.parser")
        cards = soup.find_all("a", class_="product-card")
        for i in cards:
            buffer = i.find("span", class_="category")
            categoria = buffer.get_text(strip=True)

            nome = i.find("h3", class_="product-name")
            nome = nome.get_text(strip=True)

            # Tira o "$" e transforma em número
            preco = i.find("span", class_="price")
            preco = preco.get_text(strip=True)
            preco = float(preco.replace("$", ""))

            avl = i.find("span", class_="rating")
            avl = avl.get_text(strip=True)
            avl = float(avl)

            link = i["href"]
            link = f"https://scrapingsandbox.com{link}"

            registro = {
                "nome": nome,
                "categoria": categoria,
                "preco": preco,
                "avaliacao": avl,
                "link": link
            }
            produtos.append(registro)
    return produtos


# Paginação: lê a página individual de um produto (/product/25, /product/26...)
def ler_pagina_produto(numero):
    link = f"https://scrapingsandbox.com/product/{numero}"
    resposta = baixar(link)
    if resposta is None:
        return None

    soup = BeautifulSoup(resposta.text, "html.parser")

    titulo = soup.find("h1")
    nome = titulo.get_text(strip=True)

    # A categoria fica logo acima do nome
    div_acima = titulo.find_previous_sibling("div")
    categoria = div_acima.find("span", attrs={"data-slot": "badge"}).get_text(strip=True)

    # A avaliação fica logo abaixo do nome
    div_abaixo = titulo.find_next_sibling("div")
    avl = float(div_abaixo.find("span").get_text(strip=True))

    preco = soup.find("span", class_="text-3xl").get_text(strip=True)
    preco = float(preco.replace("$", ""))

    registro = {
        "nome": nome,
        "categoria": categoria,
        "preco": preco,
        "avaliacao": avl,
        "link": link
    }
    return registro


# Junta os produtos da página inicial com os das outras páginas
def coletar_todos():
    if len(produtos_salvos) > 0:
        return produtos_salvos

    for produto in ler_pagina_inicial():
        produtos_salvos.append(produto)

    for numero in range(25, QTD_PAGINAS + 1):
        produto = ler_pagina_produto(numero)
        if produto is not None:
            produtos_salvos.append(produto)
            print(f"Página {numero} de {QTD_PAGINAS} lida")
        else:
            print(f"Página {numero} de {QTD_PAGINAS} FALHOU")

    print(f"Coleta terminada: {len(produtos_salvos)} produtos de {QTD_PAGINAS}")

    return produtos_salvos


# Filtra os produtos pela categoria escolhida
def procurar(categoria):
    todos = coletar_todos()

    if len(todos) == 0:
        return False

    produtos_filtrados = []
    for produto in todos:
        if categoria == "All Categories" or produto["categoria"] == categoria:
            produtos_filtrados.append(produto)
    return produtos_filtrados


# Página inicial
@app.route("/")
def inicio():
    return render_template("index.html")


# Página de resultados
@app.route("/resultados", methods=["POST"])
def resultados():
    categoria = request.form["categoria"]

    result = procurar(categoria)

    if result is False:
        return "Erro ao acessar o Scraping Sandbox. Verifique a internet."

    tamanho = len(result)

    # Análises: menor preço, maior preço, melhor avaliação e média
    menor = None
    maior = None
    melhor = None
    soma = 0

    for i in result:
        soma = soma + i["preco"]

        if menor is None or i["preco"] < menor["preco"]:
            menor = i

        if maior is None or i["preco"] > maior["preco"]:
            maior = i

        if melhor is None or i["avaliacao"] > melhor["avaliacao"]:
            melhor = i

    # Evita divisão por zero
    if tamanho > 0:
        media = soma / tamanho
    else:
        media = 0

    return render_template(
        "resultados.html",
        categoria=categoria,
        quantidade=tamanho,
        menor=menor,
        maior=maior,
        media=media,
        melhor=melhor,
        produtos=result,
        total=len(produtos_salvos)
    )


if __name__ == "__main__":
    app.run(debug=True)
