use axum::{
    routing::{get, post},
    Json, Router,
    http::Method,
};
use tower_http::cors::{Any, CorsLayer};
use serde::{Deserialize, Serialize};
use std::fs;
use std::process::Command;
use sysinfo::System;

// ══════════════════════════════════════════════════
// ⌬ OVRIC BACKEND — INTELIGENCIA COLMENA API
// ══════════════════════════════════════════════════

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
    
    println!("⌬ [OVRIC_BACKEND] Despertando la Colmena...");
    println!("∴ [VERIX_SOUL] Cargando secretos de la Bóveda...");
    
    let cors = CorsLayer::new()
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any)
        .allow_origin(Any);

    let app = Router::new()
        // Endpoints existentes
        .route("/api/dreams", get(get_dreams))
        .route("/api/commerce/telemetry", post(track_telemetry))
        // Hipocampo
        .route("/api/hipocampo/query", get(query_hipocampo))
        .route("/api/hipocampo/register", post(register_hipocampo_node))
        // Legion & Sistema
        .route("/api/legion/status", get(get_legion_status))
        .route("/api/system/health", get(get_system_health))
        .route("/api/actions/execute", post(execute_action))
        .layer(cors);

    let addr = "127.0.0.1:3030";
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    println!("⌬ [OVRIC_BACKEND] API Colmena activa en http://{}", addr);
    println!("  ├─ /api/dreams           → Senado de Sueños");
    println!("  ├─ /api/hipocampo/query   → Consulta de Memoria");
    println!("  ├─ /api/hipocampo/register→ Registro de Nodos");
    println!("  ├─ /api/legion/status     → Estado de la Legion");
    println!("  ├─ /api/system/health     → Métricas del Sistema");
    println!("  ├─ /api/commerce/telemetry→ Telemetría Comercial");
    println!("  └─ /api/actions/execute   → Motor de Ejecución");
    axum::serve(listener, app).await.unwrap();
}

// ══════════════════════════════════════════════════
// 🧠 HIPOCAMPO — Motor de Memoria
// ══════════════════════════════════════════════════

#[derive(Serialize, Deserialize, Debug, Clone)]
struct HipocampoNode {
    content: String,
    #[serde(rename = "type")]
    node_type: String,
    timestamp: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    vibe: Option<f64>,
}

#[derive(Serialize, Deserialize, Debug)]
struct HipocampoEdge {
    from: String,
    to: String,
    weight: f64,
    #[serde(rename = "type")]
    edge_type: String,
}

#[derive(Serialize, Deserialize, Debug)]
struct HipocampoData {
    nodes: std::collections::HashMap<String, HipocampoNode>,
    edges: Vec<HipocampoEdge>,
}

const HIPOCAMPO_PATH: &str = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\hipocampo_core\hipocampo_data.json";

fn load_hipocampo() -> Option<HipocampoData> {
    fs::read_to_string(HIPOCAMPO_PATH)
        .ok()
        .and_then(|data| serde_json::from_str::<HipocampoData>(&data).ok())
}

async fn query_hipocampo(
    axum::extract::Query(params): axum::extract::Query<std::collections::HashMap<String, String>>,
) -> Json<serde_json::Value> {
    let q = params.get("q").cloned().unwrap_or_default().to_lowercase();
    
    if let Some(hipo) = load_hipocampo() {
        let mut results = Vec::new();
        for (id, node) in &hipo.nodes {
            if node.content.to_lowercase().contains(&q) || node.node_type.to_lowercase().contains(&q) || q.is_empty() {
                // Find connections for this node
                let connections: Vec<serde_json::Value> = hipo.edges.iter()
                    .filter(|e| e.from == *id || e.to == *id)
                    .map(|e| {
                        let other = if e.from == *id { &e.to } else { &e.from };
                        serde_json::json!({
                            "target": other,
                            "weight": e.weight,
                            "relation": e.edge_type
                        })
                    })
                    .collect();

                results.push(serde_json::json!({
                    "id": id,
                    "content": node.content,
                    "type": node.node_type,
                    "timestamp": node.timestamp,
                    "connections": connections
                }));
            }
        }
        
        Json(serde_json::json!({
            "status": "success",
            "total_nodes": hipo.nodes.len(),
            "total_edges": hipo.edges.len(),
            "results": results
        }))
    } else {
        Json(serde_json::json!({ "status": "error", "message": "Memoria inaccesible" }))
    }
}

#[derive(Deserialize, Debug)]
struct RegisterNodeRequest {
    id: String,
    content: String,
    #[serde(rename = "type")]
    node_type: String,
    #[serde(default)]
    connect_to: Option<String>,
    #[serde(default)]
    weight: Option<f64>,
}

async fn register_hipocampo_node(Json(payload): Json<RegisterNodeRequest>) -> Json<serde_json::Value> {
    println!("🧠 [HIPOCAMPO] Registrando nodo: {} ({})", payload.id, payload.node_type);
    
    if let Ok(data) = fs::read_to_string(HIPOCAMPO_PATH) {
        if let Ok(mut hipo) = serde_json::from_str::<HipocampoData>(&data) {
            // Add the new node
            hipo.nodes.insert(payload.id.clone(), HipocampoNode {
                content: payload.content.clone(),
                node_type: payload.node_type.clone(),
                timestamp: chrono::Local::now().to_rfc3339(),
                vibe: None,
            });
            
            // Create edge if connect_to is specified
            if let Some(target) = &payload.connect_to {
                if hipo.nodes.contains_key(target) {
                    hipo.edges.push(HipocampoEdge {
                        from: payload.id.clone(),
                        to: target.clone(),
                        weight: payload.weight.unwrap_or(0.7),
                        edge_type: "auto_connection".to_string(),
                    });
                }
            }
            
            // Save
            if let Ok(json) = serde_json::to_string_pretty(&hipo) {
                let _ = fs::write(HIPOCAMPO_PATH, json);
                return Json(serde_json::json!({
                    "status": "registered",
                    "node_id": payload.id,
                    "total_nodes": hipo.nodes.len(),
                    "total_edges": hipo.edges.len()
                }));
            }
        }
    }
    
    Json(serde_json::json!({ "status": "error", "message": "No se pudo registrar el nodo" }))
}

// ══════════════════════════════════════════════════
// 🛡️ LEGION — Estado de los Soldados
// ══════════════════════════════════════════════════

const ESTADO_PATH: &str = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\orbe_estado.json";

async fn get_legion_status() -> Json<serde_json::Value> {
    if let Ok(data) = fs::read_to_string(ESTADO_PATH) {
        if let Ok(estado) = serde_json::from_str::<serde_json::Value>(&data) {
            return Json(serde_json::json!({
                "status": "success",
                "soldiers": estado.get("soldados"),
                "stats": estado.get("stats"),
                "estado_global": estado.get("estado_global"),
                "progreso_rust": estado.get("progreso_rust"),
                "score_salud": estado.get("score_salud")
            }));
        }
    }
    Json(serde_json::json!({ "status": "error", "message": "Estado inaccesible" }))
}

// ══════════════════════════════════════════════════
// 💚 SYSTEM HEALTH — Métricas en Tiempo Real
// ══════════════════════════════════════════════════

async fn get_system_health() -> Json<serde_json::Value> {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    let total_memory = sys.total_memory();
    let used_memory = sys.used_memory();
    let cpu_usage: f32 = sys.cpus().iter().map(|c| c.cpu_usage()).sum::<f32>() / sys.cpus().len() as f32;
    
    // Disk info
    let disks = sysinfo::Disks::new_with_refreshed_list();
    let mut total_disk: u64 = 0;
    let mut available_disk: u64 = 0;
    for disk in disks.list() {
        total_disk += disk.total_space();
        available_disk += disk.available_space();
    }
    
    Json(serde_json::json!({
        "status": "success",
        "cpu": {
            "usage_percent": (cpu_usage * 100.0).round() / 100.0,
            "cores": sys.cpus().len()
        },
        "memory": {
            "total_gb": (total_memory as f64 / 1_073_741_824.0 * 100.0).round() / 100.0,
            "used_gb": (used_memory as f64 / 1_073_741_824.0 * 100.0).round() / 100.0,
            "usage_percent": ((used_memory as f64 / total_memory as f64) * 10000.0).round() / 100.0
        },
        "disk": {
            "total_gb": (total_disk as f64 / 1_073_741_824.0 * 100.0).round() / 100.0,
            "available_gb": (available_disk as f64 / 1_073_741_824.0 * 100.0).round() / 100.0,
            "usage_percent": (((total_disk - available_disk) as f64 / total_disk as f64) * 10000.0).round() / 100.0
        },
        "uptime_seconds": System::uptime(),
        "timestamp": chrono::Local::now().to_rfc3339()
    }))
}

// ══════════════════════════════════════════════════
// 📦 COMMERCE TELEMETRY
// ══════════════════════════════════════════════════

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

// ══════════════════════════════════════════════════
// 🌌 SENADO DE SUEÑOS
// ══════════════════════════════════════════════════

#[derive(Deserialize, Debug)]
struct ActionRequest {
    action: String,
}

async fn execute_action(Json(payload): Json<ActionRequest>) -> Json<serde_json::Value> {
    println!("⚡ [EXECUTION_ENGINE] Solicitud de acción: {}", payload.action);
    let mut success = false;
    let mut message = String::new();

    match payload.action.as_str() {
        "sync" => {
            let output = Command::new("python")
                .arg(r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\verix_mirror_sync.py")
                .output();
            match output {
                Ok(out) => {
                    success = out.status.success();
                    message = String::from_utf8_lossy(&out.stdout).to_string();
                    if message.trim().is_empty() {
                        message = "Sincronización completada sin salida en consola.".to_string();
                    }
                },
                Err(e) => {
                    message = format!("Error ejecutando sync: {}", e);
                }
            }
        },
        "dreams" => {
            let child = Command::new("cmd")
                .args(&["/C", r"start cmd.exe /K C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Iniciar_Senado_Suenos.bat"])
                .spawn();
            match child {
                Ok(_) => {
                    success = true;
                    message = "Senado de sueños lanzado en nueva ventana.".to_string();
                },
                Err(e) => {
                    message = format!("Error lanzando sueños: {}", e);
                }
            }
        },
        "purge" => {
            let output = Command::new("cmd")
                .args(&["/C", r"echo Purga ejecutada. (Modo simulación por seguridad)"])
                .output();
            match output {
                Ok(out) => {
                    success = true;
                    message = String::from_utf8_lossy(&out.stdout).to_string();
                },
                Err(e) => {
                    message = format!("Error en purga: {}", e);
                }
            }
        },
        _ => {
            message = "Acción desconocida.".to_string();
        }
    }

    Json(serde_json::json!({
        "status": if success { "success" } else { "error" },
        "message": message
    }))
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
