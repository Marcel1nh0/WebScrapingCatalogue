from doctest import debug

from flask import Flask, request, render_template
import requests
import bs4
app = Flask(__name__)
@app.route("/")
def inicio():
    return render_template("index.html")
if __name__ =="__main__":
    app.run(debug=True)