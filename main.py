from bs4 import BeautifulSoup
from flask import Flask, render_template
import requests


app = Flask(__name__)
def procurar(categoria):
    produtos = []
    # url = "https://scrapingsandbox.com/infinite-scroll" #caso não de para ler todos os produtos pela página inicial :P
    url = "https://scrapingsandbox.com/"
    resposta = requests.get(url)
    if resposta.status_code == 200:
        soup = BeautifulSoup(resposta.text,"html.parser")
        cards = soup.find_all("a",class_="product-card")
        for i in cards:
            buffer = i.find("inline-flex")
            if categoria == buffer[0].get_text(strip=True):

                nome = i.find("div", class_="product-name")
                nome = nome.get_text(strip=True)
                preco = i.find("span", class_="price")
                preco = preco.get_text(strip=True)
                avl = i.find("span", class_="rating")
                avl = avl.get_text(strip=True)
                link = i.select("a.href")
                url = f"https://scrapingsandbox.com/{link}/"


                registro = {
                    "nome": nome,
                    "categoria": categoria,
                    "preco": preco,
                    "avaliacao": avl,
                    "link": url
                }
                produtos.append(registro)
        return produtos
    return False

@app.route("/")
def inicio():
    return render_template("index.html")
@app.route("/resultados/<categoria>")
def resultados(categoria):
    result = procurar(categoria)
    if not result:
        return "Erro ao procurar os produtos..."
    tamanho = len(result)
    for i in result:
        # colocar aqui as coisas fodas

    return render_template("resultados.html",quantidade=tamanho,)

if __name__ =="__main__":
    app.run(debug=True)