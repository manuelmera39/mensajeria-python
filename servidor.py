from flask import Flask, request, jsonify
from datetime import datetime
import uuid
import os

app = Flask(__name__)

# -------------------------------
# RUTA BASE
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

        # ACEPTA AMBOS FORMATOS (cliente antiguo y nuevo)
        de = datos.get("de") or datos.get("origen") or "desconocido"
        para = datos.get("para") or datos.get("destino") or "desconocido"

        # NORMALIZAR (CLAVE)
        de = de.lower()
        para = para.lower()

        nuevo_mensaje = {
            "id": str(uuid.uuid4()),
            "de": de,
            "para": para,
            "mensaje": datos.get("mensaje", ""),
            "hora": datetime.now().strftime("%H:%M"),
            "leido": False
        }

        mensajes.append(nuevo_mensaje)

        # mantener máximo 50 mensajes
        if len(mensajes) > 50:
            mensajes.pop(0)

        print("Mensaje guardado:", nuevo_mensaje)

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
        destino = destino.lower()

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
        nombre = nombre.lower()

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
# ARRANQUE LOCAL
# -------------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("Servidor listo")
    app.run(host="0.0.0.0", port=port)
