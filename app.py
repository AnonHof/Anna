from flask import Flask, render_template, request, jsonify, make_response
import pusher
import mysql.connector
import datetime
import pytz

app = Flask(__name__)

pusher_client = pusher.Pusher(
    app_id='1864237',
    key='fe0a6fda0635d4db01ce',
    secret='e5c4c8f921f883404989',
    cluster='us2',
    ssl=True
)

def get_db_connection():
    con = mysql.connector.connect(
        host="185.232.14.52",
        database="u760464709_tst_sep",
        user="u760464709_tst_sep_usr",
        password="dJ0CIAFF="
    )
    return con

@app.route("/")
def index():
    return render_template("Inicio.html")

# Ruta para manejar la creación y edición de contactos
@app.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        id_contacto = request.form.get("id_contacto")
        correo = request.form["email"]
        nombre = request.form["nombre"]
        asunto = request.form["asunto"]

        con = get_db_connection()
        cursor = con.cursor()

        if id_contacto:
            sql = """
            UPDATE tst0_contacto
            SET Correo_Electronico = %s, Nombre = %s, Asunto = %s
            WHERE Id_Contacto = %s
            """
            val = (correo, nombre, asunto, id_contacto)
            cursor.execute(sql, val)
        else:
            sql = "INSERT INTO tst0_contacto (Correo_Electronico, Nombre, Asunto) VALUES (%s, %s, %s)"
            val = (correo, nombre, asunto)
            cursor.execute(sql, val)

        con.commit()
        con.close()

        pusher_client.trigger("registrosTiempoReal", "registroTiempoReal", {
            "email": correo,
            "nombre": nombre,
            "asunto": asunto,
            "id_contacto": id_contacto if id_contacto else cursor.lastrowid
        })

    return render_template("contacto.html")

@app.route("/buscar")
def buscar():
    con = get_db_connection()
    cursor = con.cursor()
    search_query = request.args.get("q", "")
    if search_query:
        cursor.execute("SELECT * FROM tst0_contacto WHERE Correo_Electronico LIKE %s OR Nombre LIKE %s ORDER BY Id_Contacto DESC", (f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("SELECT * FROM tst0_contacto ORDER BY Id_Contacto DESC")
    
    registros = cursor.fetchall()
    con.close()

    registros_list = [{"Id_Contacto": r[0], "Correo_Electronico": r[1], "Nombre": r[2], "Asunto": r[3]} for r in registros]
    return jsonify(registros_list)

@app.route("/eliminar_contacto", methods=["POST"])
def eliminar_contacto():
    con = get_db_connection()
    if not con.is_connected():
        con.reconnect()

    id_contacto = request.form["id"]

    cursor = con.cursor()
    sql = "DELETE FROM tst0_contacto WHERE Id_Contacto = %s"
    val = (id_contacto,)

    cursor.execute(sql, val)
    con.commit()
    con.close()

    pusher_client.trigger("registrosTiempoReal", "registroEliminado", {"id": id_contacto})

    return jsonify({"message": "Contacto eliminado correctamente"})

@app.route("/obtener_contacto", methods=["GET"])
def obtener_contacto():
    id_contacto = request.args.get("id")
    con = get_db_connection()
    cursor = con.cursor(dictionary=True)
    
    sql = "SELECT * FROM tst0_contacto WHERE Id_Contacto = %s"
    cursor.execute(sql, (id_contacto,))
    
    contacto = cursor.fetchone()
    con.close()
    
    return jsonify(contacto)

if __name__ == "__main__":
    app.run(debug=True)
