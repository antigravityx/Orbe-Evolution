import os
import json
from datetime import datetime

# --- CONFIGURACIÓN DEL SOLDADO ---
AURA_ROOT = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Verix_Aura"
DATA_SOURCE = r"C:\Users\Usuario\Desktop\curriculum 2026"
FRONTEND_DATA = os.path.join(AURA_ROOT, "frontend", "src", "data")

def fusionar_aura():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Soldado Aura-Funder iniciando ritual de fusión...")
    
    # Crear directorio de datos en el frontend si no existe
    os.makedirs(FRONTEND_DATA, exist_ok=True)
    
    # Datos extraídos (Simulando la memoria del soldado)
    resume_data = {
        "identidad": {
            "nombre": "Oromé Jose Maria",
            "dni": "37.343.496",
            "edad": "34",
            "estado_civil": "Soltero",
            "nacimiento": "Buenos Aires",
            "direccion": "Barrio Jardín, Calle Las Teresitas 5662",
            "telefono": "3794-593954"
        },
        "experiencia": [
            {"puesto": "Chapa y Pintura", "empresa": "Martunin", "desc": "Mantenimiento estético automotriz."},
            {"puesto": "Servicio de Mantenimiento", "empresa": "Coca Cola", "desc": "Operaciones preventivas y correctivas."},
            {"puesto": "Carga y Descarga", "empresa": "Mercadería Marca Silvia", "desc": "Logística de productos."}
        ],
        "formacion": {
            "primario": "Completo",
            "secundario": "En Curso"
        },
        "objetivo": "Desenvolverme en un puesto de trabajo con eficiencia y responsabilidad.",
        "disponibilidad": "Full Time"
    }
    
    # Sellar los datos en el frontend
    output_path = os.path.join(FRONTEND_DATA, "resume_data.json")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(resume_data, f, indent=4, ensure_ascii=False)
        
    print(f"[OK] Aura sellada en: {output_path}")

if __name__ == "__main__":
    fusionar_aura()
