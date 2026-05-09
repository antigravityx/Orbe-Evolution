use axum::{
    routing::get,
    Json, Router,
    http::Method,
};
use tower_http::cors::{Any, CorsLayer};
use serde::{Deserialize, Serialize};
use std::fs;

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Sueno {
    id: String,
    asunto: String,
    descripcion: String,
    aprobado: bool,
    fecha: String,
}

#[derive(Deserialize, Debug, Clone)]
struct SuenoInternal {
    id: String,
    asunto: String,
    descripcion: String,
}

#[tokio::main]
async fn main() {
    // Cargar variables de entorno del Santuario
    dotenvy::dotenv().ok();
    
    println!("∴ [VERIX_SOUL] Cargando secretos de la Bóveda...");
    let cors = CorsLayer::new()
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any)
        .allow_origin(Any);

    let app = Router::new()
        .route("/api/dreams", get(get_dreams))
        .route("/api/commerce/telemetry", axum::routing::post(track_telemetry))
        .layer(cors);

    let addr = "127.0.0.1:3030";
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    println!("∴ [VERIX_BACKEND] API de Sueños corriendo en http://{}", addr);
    axum::serve(listener, app).await.unwrap();
}

#[derive(Deserialize, Debug)]
struct CommerceEvent {
    event_type: String,
    product_id: String,
    metadata: Option<String>,
}

async fn track_telemetry(Json(payload): Json<CommerceEvent>) -> Json<serde_json::Value> {
    println!("∴ [COMMERCE_TELEMETRY] Event: {} | Product: {}", payload.event_type, payload.product_id);
    
    // Log to file
    let log_path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\commerce.log";
    let log_entry = format!("{} | {} | {}\n", 
        chrono::Local::now().format("%Y-%m-%d %H:%M:%S"),
        payload.event_type,
        payload.product_id
    );
    
    let _ = fs::OpenOptions::new()
        .create(true)
        .append(true)
        .open(log_path)
        .map(|mut f| {
            use std::io::Write;
            let _ = f.write_all(log_entry.as_bytes());
        });

    Json(serde_json::json!({ "status": "recorded" }))
}

async fn get_dreams() -> Json<Vec<Sueno>> {
    let mut all_dreams = Vec::new();

    // 1. Read discarded dreams (JSON)
    let colchon_path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\colchon_de_suenos.json";
    if let Ok(data) = fs::read_to_string(colchon_path) {
        if let Ok(json_dreams) = serde_json::from_str::<Vec<SuenoInternal>>(&data) {
             for d in json_dreams {
                 all_dreams.push(Sueno {
                     id: d.id,
                     asunto: d.asunto,
                     descripcion: d.descripcion,
                     aprobado: false,
                     fecha: "Desconocida".to_string(),
                 });
             }
        }
    }

    // 2. Read approved dreams (MD)
    let diario_path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\diario_de_suenos.md";
    if let Ok(content) = fs::read_to_string(diario_path) {
        let entries: Vec<&str> = content.split("---").collect();
        for entry in entries {
            if entry.trim().is_empty() { continue; }
            
            let mut id = String::new();
            let mut asunto = String::new();
            let mut descripcion = String::new();
            let mut fecha = String::new();

            for line in entry.lines() {
                let line = line.trim();
                if line.contains("Fecha:") {
                    if let Some(pos) = line.find("Fecha: ") {
                        fecha = line[pos + 7..].to_string();
                    }
                }
                if line.contains("**Sueño ID:**") {
                    id = line.replace("**Sueño ID:**", "").trim().replace("`", "");
                }
                if line.contains("**Asunto:**") {
                    asunto = line.replace("**Asunto:**", "").trim().to_string();
                }
                if line.contains("> **Epifanía:**") {
                    descripcion = line.replace("> **Epifanía:**", "").trim().to_string();
                }
            }

            if !id.is_empty() {
                all_dreams.push(Sueno {
                    id, asunto, descripcion, aprobado: true, fecha
                });
            }
        }
    }

    Json(all_dreams)
}

