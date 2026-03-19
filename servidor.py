from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import os

app = Flask(__name__)

# -------------------------------
# RUTA BASE (IMPORTANTE)
# -------------------------------
@app.route("/")
def home():
    return "Servidor activo"


# almacenamiento en memoria
mensajes = []
eventos_lectura = []


# -------------------------------
# ENVIAR MENSAJE
# -------------------------------
@app.route("/enviar", methods=["POST"])
def enviar():
    try:
        datos = request.get_json(force=True)

        if not datos:
            return jsonify({"error": "Datos vacíos"}), 400

        nuevo_mensaje = {
            "id": str(uuid.uuid4()),
            "de": datos.get("de", "DESCONOCIDO"),
            "para": datos.get("para", "DESCONOCIDO"),
            "mensaje": datos.get("mensaje", ""),
            "hora": datetime.now().strftime("%H:%M"),
            "leido": False
        }

        mensajes.append(nuevo_mensaje)

        # mantener máximo 10 mensajes
        if len(mensajes) > 10:
            mensajes.pop(0)

        print("Mensaje recibido:", nuevo_mensaje)

        return jsonify({"estado": "ok"})

    except Exception as e:
        print("Error en /enviar:", e)
        return jsonify({"error": "Fallo interno"}), 500


# -------------------------------
# LEER MENSAJES
# -------------------------------
@app.route("/leer/<destino>", methods=["GET"])
def leer(destino):
    try:
        resultado = [
            m for m in mensajes
            if m["para"] == destino and not m["leido"]
        ]
        return jsonify(resultado)

    except Exception as e:
        print("Error en /leer:", e)
        return jsonify([])


# -------------------------------
# CONFIRMAR LECTURA
# -------------------------------
@app.route("/confirmar", methods=["POST"])
def confirmar():
    try:
        datos = request.get_json(force=True)
        mensaje_id = datos.get("id")

        for m in mensajes:
            if m["id"] == mensaje_id:
                m["leido"] = True

                eventos_lectura.append({
                    "de": m["de"],
                    "para": m["para"],
                    "hora": datetime.now().strftime("%H:%M")
                })

                print("Mensaje leído:", m)
                break

        return jsonify({"estado": "ok"})

    except Exception as e:
        print("Error en /confirmar:", e)
        return jsonify({"error": "Fallo interno"}), 500


# -------------------------------
# CONSULTAR LECTURAS
# -------------------------------
@app.route("/lecturas/<nombre>", methods=["GET"])
def lecturas(nombre):
    try:
        global eventos_lectura

        resultado = [e for e in eventos_lectura if e["de"] == nombre]

        eventos_lectura = [
            e for e in eventos_lectura if e["de"] != nombre
        ]

        return jsonify(resultado)

    except Exception as e:
        print("Error en /lecturas:", e)
        return jsonify([])


# -------------------------------
# ARRANQUE (LOCAL)
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("Servidor listo")
    app.run(host="0.0.0.0", port=port)
