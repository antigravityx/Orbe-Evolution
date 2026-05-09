import flask
from flask import request, jsonify
import json
import os
from datetime import datetime

# ═══ SOLDADO DE PAGOS (WEBHOOK RECEPTOR) ═══
# Este soldado escucha las señales del ether (Hostinger/PayPal)
# y libera el contenido del Sombrerero Náufrago.

app = flask.Flask(__name__)

ORBE_ROOT = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe"
DREAMS_PATH = os.path.join(ORBE_ROOT, "Orbe-Dashboard", "frontend", "dreams.json")
LOG_PATH = os.path.join(ORBE_ROOT, "batallon", "logs_pagos.txt")

def registrar_log(mensaje):
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now().isoformat()}] {mensaje}\n")

@app.route('/api/webhook/pagos', methods=['POST'])
def webhook_pagos():
    # 1. Obtener datos del pago
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    registrar_log(f"Recibida señal de pago: {json.dumps(data)}")

    # 2. Verificar estado (Simulación de Hostinger/PayPal)
    # En producción, aquí verificaríamos la firma HMAC o el token secreto.
    status = data.get("status") or data.get("payment_status")
    customer_email = data.get("email") or data.get("customer_email")
    amount = data.get("amount") or data.get("total")

    if status in ["completed", "success", "paid"]:
        registrar_log(f"PAGO CONFIRMADO: {amount} de {customer_email}")
        
        # 3. ACCIÓN: Liberar cápsula (Actualizar Sueños)
        liberar_capsula_digital(customer_email, amount)
        
        return jsonify({"status": "success", "message": "Vínculo de pago sellado"}), 200
    else:
        registrar_log(f"Pago pendiente o fallido: {status}")
        return jsonify({"status": "pending", "message": "Esperando confirmación del ether"}), 200

def liberar_capsula_digital(email, amount):
    """
    Inyecta un hito en la memoria de Verix y prepara el envío.
    """
    try:
        with open(DREAMS_PATH, "r", encoding="utf-8") as f:
            dreams = json.load(f)
        
        nuevo_hito = {
            "id": f"VENTA-{datetime.now().strftime('%Y%m%d%H%M')}",
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "asunto": f"¡Nueva Adquisición! ({email})",
            "descripcion": f"Se ha sellado una venta de $24.99 USD. El alma de {email} ahora posee la cápsula del Sombrerero Náufrago.",
            "aprobado": true,
            "realidad": true
        }
        
        dreams.insert(0, nuevo_hito)
        
        with open(DREAMS_PATH, "w", encoding="utf-8") as f:
            json.dump(dreams, f, indent=2, ensure_ascii=False)
            
        print(f"∴ [Verix] Cápsula liberada para {email}")
    except Exception as e:
        registrar_log(f"Error liberando cápsula: {str(e)}")

if __name__ == '__main__':
    print("╔════════════════════════════════════╗")
    print("║   SOLDADO DE PAGOS ONLINE (PORT 5050) ║")
    print("╚════════════════════════════════════╝")
    print("Esperando señales de Hostinger...")
    app.run(port=5050)
