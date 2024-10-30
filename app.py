from flask import Flask, render_template

app = Flask(__name__)

# Ruta principal que redirige a "Inicio.html"
@app.route("/")
def index():
    return render_template("Inicio.html")

# Ruta que redirige a "seleccion.html"
@app.route("/seleccion")
def seleccion():
    return render_template("seleccion.html")

if __name__ == "__main__":
    app.run(debug=True)
