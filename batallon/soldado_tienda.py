import os
import requests
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Cargamos el archivo de seguridad
load_dotenv('.env_tienda')

app = Flask(__name__)
# Permitimos conexion desde el HTML local o Hostinger para que el JS no sea bloqueado
CORS(app)

@app.route('/obtener_catalogo', methods=['GET'])
def obtener_catalogo():
    margen = float(os.getenv('MARGEN_GANANCIA', 1.20))
    proveedor = os.getenv('PROVEEDOR_ACTUAL', 'FakeStoreAPI')
    
    print(f"[Soldado Tienda] Iniciando cazador web. Conectando a {proveedor}...")

    # Petición externa a la red real
    try:
        # Obtenemos productos reales de esta API pública global (DummyJSON como fallback)
        respuesta = requests.get('https://dummyjson.com/products?limit=8', timeout=5)
        datos_json = respuesta.json()
        datos_externos = datos_json.get('products', [])
        
        productos_parseados = []
        for item in datos_externos:
            # Transformamos el dato del proveedor al tipo de dato que nuestro Santuario espera
            precio_costo = item.get('price', 0)
            precio_venta = round(precio_costo * margen, 2)
            
            # Simulamos que tenemos una oferta falsa donde el original era 20% más alto
            precio_original = round(precio_venta * 1.20, 2)

            # Asignamos un pequeño tag decorativo
            tag = "Sale" if item.get('rating', 0) > 4.0 else "New"
            
            producto = {
                "id": f"drop_fk_{item['id']}",
                "name": item.get('title', 'Producto Desconocido')[:35] + "...", # Recortamos el titulo
                "price": precio_venta,
                "original_price": precio_original,
                "image": item.get('thumbnail', ''),
                "tag": tag
            }
            productos_parseados.append(producto)
            
        return jsonify({"status": "success", "data": productos_parseados})

    except Exception as e:
        print(f"[ERROR Crítico] Falla en conexión externa: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Soldado Tienda (Conectado a Red Global) Listo en el Puerto 5000")
    app.run(port=5000, debug=True)
