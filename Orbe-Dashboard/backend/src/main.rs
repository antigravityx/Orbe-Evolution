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

mod core_crypto;
mod capsule_virtualizer;


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

#[derive(Deserialize, Debug)]
struct RepoConfig {
    base_dir: String,
    proyectos: Vec<String>,
}

#[derive(Serialize)]
struct RepoItem {
    id: String,
    name: String,
    path: String,
}

#[derive(Deserialize)]
struct RepoActionReq {
    path: String,
    action: String,
}

#[derive(Deserialize)]
struct CreateCapsuleReq {
    path: String,
    password: String,
}

#[derive(Deserialize)]
struct InvokeCapsuleReq {
    path: String,
    password: String,
}

#[derive(Serialize)]
struct BatchSyncResult {
    repo: String,
    success: bool,
    message: String,
}

#[derive(Deserialize)]
struct DataQueryReq {
    query: String,
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
        // Repositorios / Santuario
        .route("/api/repos", get(get_repos))
        .route("/api/repos/action", post(execute_repo_action))
        // Bóveda / Cápsulas
        .route("/api/capsules", get(get_capsules))
        .route("/api/capsules/create", post(create_capsule_handler))
        .route("/api/capsules/invoke", post(invoke_capsule_handler))
        // Legion Expansion
        .route("/api/legion/batch-sync", post(batch_sync_handler))
        .route("/api/system/control", post(system_control_handler))
        .route("/api/virtual/execute", post(virtual_execute_handler))
        .route("/api/data/query", post(execute_data_query))
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
    println!("  ├─ /api/actions/execute   → Motor de Ejecución");
    println!("  └─ /api/capsules          → Gestión de la Bóveda");

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
// 🌌 SENADO DE SUEÑOS & SANTUARIO
// ══════════════════════════════════════════════════

async fn get_repos() -> Json<serde_json::Value> {
    let config_path = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\config.json";
    if let Ok(data) = fs::read_to_string(config_path) {
        if let Ok(config) = serde_json::from_str::<RepoConfig>(&data) {
            let mut repos = Vec::new();
            for (i, p) in config.proyectos.iter().enumerate() {
                let path = format!("{}\\{}", config.base_dir, p);
                let name = p.split('\\').last().unwrap_or(p).to_string();
                repos.push(RepoItem {
                    id: format!("repo_{}", i),
                    name,
                    path,
                });
            }
            return Json(serde_json::json!({
                "status": "success",
                "repos": repos
            }));
        }
    }
    Json(serde_json::json!({ "status": "error", "message": "No se pudo leer la configuracion de repositorios" }))
}

async fn execute_repo_action(Json(payload): Json<RepoActionReq>) -> Json<serde_json::Value> {
    println!("📦 [SANTUARIO] Accion: {} en {}", payload.action, payload.path);
    let mut success = false;
    let mut message = String::new();

    match payload.action.as_str() {
        "status" => {
            if let Ok(out) = Command::new("git").arg("status").current_dir(&payload.path).output() {
                success = out.status.success();
                message = String::from_utf8_lossy(&out.stdout).to_string();
                if !out.status.success() {
                    message += &String::from_utf8_lossy(&out.stderr).to_string();
                }
            } else {
                message = "Error ejecutando git status".to_string();
            }
        },
        "pull" => {
            if let Ok(out) = Command::new("git").arg("pull").current_dir(&payload.path).output() {
                success = out.status.success();
                message = String::from_utf8_lossy(&out.stdout).to_string();
                if !out.status.success() {
                    message += &String::from_utf8_lossy(&out.stderr).to_string();
                }
            } else {
                message = "Error ejecutando git pull".to_string();
            }
        },
        "push" => {
            let _ = Command::new("git").args(&["add", "."]).current_dir(&payload.path).output();
            let _ = Command::new("git").args(&["commit", "-m", "Auto-commit desde OVRIC Santuario"]).current_dir(&payload.path).output();
            if let Ok(out) = Command::new("git").arg("push").current_dir(&payload.path).output() {
                success = out.status.success();
                message = String::from_utf8_lossy(&out.stdout).to_string();
                message += &String::from_utf8_lossy(&out.stderr).to_string();
                if message.trim().is_empty() { message = "Push ejecutado con éxito.".to_string(); }
            } else {
                message = "Error ejecutando git push".to_string();
            }
        },
        "sync_codeberg" => {
            let cb_user = std::env::var("CODEBERG_USER").unwrap_or_else(|_| "shverix".to_string());
            let cb_token = std::env::var("CODEBERG_TOKEN").unwrap_or_default();
            let repo_name = payload.path.split(|c| c == '\\' || c == '/').last().unwrap_or("repo");
            
            // Intentar añadir el remote (si falla porque ya existe, lo ignoramos)
            let _ = Command::new("git")
                .args(&["remote", "add", "codeberg", &format!("https://codeberg.org/{}/{}.git", cb_user, repo_name)])
                .current_dir(&payload.path)
                .output();
            
            let remote_url = format!("https://{}:{}@codeberg.org/{}/{}.git", cb_user, cb_token, cb_user, repo_name);
            
            if let Ok(out) = Command::new("git")
                .args(&["push", "--force", &remote_url, "main"])
                .current_dir(&payload.path)
                .output() {
                success = out.status.success();
                message = String::from_utf8_lossy(&out.stdout).to_string();
                message += &String::from_utf8_lossy(&out.stderr).to_string();
                if success { message = "Sincronizacion con Codeberg exitosa (GOD MODE).".to_string(); }
            } else {
                message = "Error sincronizando con Codeberg".to_string();
            }
        },
        "preview" => {
            let repo_name = payload.path.split(|c| c == '\\' || c == '/').last().unwrap_or("repo");
            let gh_user = std::env::var("GITHUB_USER").unwrap_or_else(|_| "antigravityx".to_string());
            let url = format!("https://{}.github.io/{}", gh_user, repo_name);
            if let Ok(_) = Command::new("cmd").args(&["/C", "start", &url]).spawn() {
                success = true;
                message = format!("Abriendo vista previa en: {}", url);
            } else {
                message = "Error abriendo vista previa".to_string();
            }
        },
        "deploy_hostinger" => {
            if payload.path.contains("sombrereronaufrago") {
                let output = Command::new("python")
                    .arg(r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\GESTION_R1CH0N\sombrereronaufrago\deploy_naufrago.py")
                    .current_dir(&payload.path)
                    .output();
                match output {
                    Ok(out) => {
                        success = out.status.success();
                        message = String::from_utf8_lossy(&out.stdout).to_string();
                        message += &String::from_utf8_lossy(&out.stderr).to_string();
                    },
                    Err(e) => {
                        message = format!("Error ejecutando deploy python: {}", e);
                    }
                }
            } else {
                message = "Este proyecto no tiene configurado deploy automatico a Hostinger.".to_string();
            }
        },
        "code" => {
            let config_path = "../../ovric_config.json";
            let editor_cmd = if let Ok(data) = fs::read_to_string(config_path) {
                if let Ok(v) = serde_json::from_str::<serde_json::Value>(&data) {
                    match v.get("editor").and_then(|e| e.as_str()) {
                        Some("cursor") => "cursor",
                        Some("sublime") => "subl",
                        Some("notepad") => "notepad++",
                        Some("antigravity") => "code", // Por ahora Antigravity usa el núcleo de VS Code o el editor configurado
                        _ => "code",
                    }
                } else { "code" }
            } else { "code" };

            if let Ok(_) = Command::new("cmd").args(&["/C", editor_cmd, "."]).current_dir(&payload.path).spawn() {
                success = true;
                message = format!("Abriendo en {}...", editor_cmd);
            } else {
                message = format!("Error abriendo editor: {}", editor_cmd);
            }
        },
        _ => {
            message = "Acción de repositorio desconocida".to_string();
        }
    }

    Json(serde_json::json!({
        "status": if success { "success" } else { "error" },
        "message": message
    }))
}

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

// ══════════════════════════════════════════════════
// 📦 BÓVEDA — Gestión de Cápsulas
// ══════════════════════════════════════════════════

async fn get_capsules() -> Json<serde_json::Value> {
    let dest = r"C:\Users\Usuario\Desktop\Orbe_Santuario\1_Almas_Encapsuladas";
    let mut capsules = Vec::new();
    if let Ok(entries) = fs::read_dir(dest) {
        for entry in entries.flatten() {
            if let Ok(meta) = entry.metadata() {
                if meta.is_file() && entry.path().extension().map_or(false, |e| e == "capsula") {
                    capsules.push(serde_json::json!({
                        "name": entry.file_name().to_string_lossy(),
                        "path": entry.path().to_string_lossy(),
                        "size": meta.len(),
                        "created": chrono::DateTime::<chrono::Local>::from(meta.created().unwrap_or(std::time::SystemTime::now())).to_rfc3339()
                    }));
                }
            }
        }
    }
    Json(serde_json::json!({ "status": "success", "capsules": capsules }))
}

async fn create_capsule_handler(Json(payload): Json<CreateCapsuleReq>) -> Json<serde_json::Value> {
    match core_crypto::create_capsule(&payload.path, &payload.password) {
        Ok(path) => Json(serde_json::json!({ "status": "success", "message": format!("Cápsula creada: {}", path) })),
        Err(e) => Json(serde_json::json!({ "status": "error", "message": e })),
    }
}

async fn invoke_capsule_handler(Json(payload): Json<InvokeCapsuleReq>) -> Json<serde_json::Value> {
    match core_crypto::invoke_capsule(&payload.path, &payload.password) {
        Ok(path) => Json(serde_json::json!({ "status": "success", "message": format!("Alma liberada en: {}", path) })),
        Err(e) => Json(serde_json::json!({ "status": "error", "message": e })),
    }
}

// ══════════════════════════════════════════════════
// 🚀 EXPANSION — Handlers de Aceleración
// ══════════════════════════════════════════════════

async fn batch_sync_handler() -> Json<serde_json::Value> {
    println!("⚡ [LEGION] Iniciando Sincronización Masiva...");
    let config_path = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\config.json";
    
    if let Ok(data) = fs::read_to_string(config_path) {
        if let Ok(config) = serde_json::from_str::<RepoConfig>(&data) {
            let mut tasks = Vec::new();
            
            for p in config.proyectos {
                let base_dir = config.base_dir.clone();
                let repo_path = format!("{}\\{}", base_dir, p);
                
                let task = tokio::spawn(async move {
                    println!("  ├─ Sincronizando: {}", repo_path);
                    let mut success = false;
                    let mut msg = String::new();
                    
                    // Pull
                    if let Ok(out) = Command::new("git").arg("pull").current_dir(&repo_path).output() {
                        success = out.status.success();
                        msg = String::from_utf8_lossy(&out.stdout).to_string();
                    } else {
                        msg = "Error ejecutando git pull".to_string();
                    }
                    
                    BatchSyncResult { repo: repo_path, success, message: msg }
                });
                tasks.push(task);
            }
            
            let mut results = Vec::new();
            for task in tasks {
                if let Ok(res) = task.await {
                    results.push(res);
                }
            }
            
            return Json(serde_json::json!({
                "status": "success",
                "results": results
            }));
        }
    }
    
    Json(serde_json::json!({ "status": "error", "message": "No se pudo leer la configuración para batch-sync" }))
}

async fn system_control_handler(Json(payload): Json<SystemControlReq>) -> Json<serde_json::Value> {
    println!("🛡️ [SYSTEM_CONTROL] Soldado: {} | Acción: {}", payload.soldier, payload.action);
    
    let mut success = false;
    let mut message = String::new();
    
    match payload.action.as_str() {
        "start" => {
            let path = match payload.soldier.as_str() {
                "SHIELD" => Some(r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\legion_ovric\shield.ts"),
                "PSYCHE" => Some(r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\legion_ovric\psyche.py"),
                "SENTINEL-V" => Some(r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\legion_ovric\sentinel_v.ts"),
                _ => None
            };
            
            if let Some(p) = path {
                let cmd = if p.ends_with(".ts") { "bun" } else { "python" };
                if let Ok(_) = Command::new("cmd").args(&["/C", "start", cmd, p]).spawn() {
                    success = true;
                    message = format!("Soldado {} desplegado con éxito.", payload.soldier);
                } else {
                    message = format!("Error al desplegar soldado {}.", payload.soldier);
                }
            } else {
                message = "Soldado desconocido.".to_string();
            }
        },
        "stop" => {
            // Simplificado: matar proceso por nombre
            let target = match payload.soldier.as_str() {
                "SHIELD" => "bun.exe",
                "PSYCHE" => "python.exe",
                _ => ""
            };
            if !target.is_empty() {
                let _ = Command::new("taskkill").args(&["/F", "/IM", target]).output();
                success = true;
                message = format!("Misión finalizada para {}.", payload.soldier);
            }
        },
        _ => message = "Acción no permitida.".to_string()
    }
    
    Json(serde_json::json!({ "status": if success { "success" } else { "error" }, "message": message }))
}

async fn virtual_execute_handler(Json(payload): Json<capsule_virtualizer::VirtualExecReq>) -> Json<serde_json::Value> {
    let res = capsule_virtualizer::execute_in_sandbox(payload);
    Json(serde_json::json!(res))
}

async fn execute_data_query(Json(payload): Json<DataQueryReq>) -> Json<serde_json::Value> {
    println!("📊 [DATA_NEXUS] Ejecutando consulta BigQuery: {}", payload.query);
    
    let output = Command::new("python")
        .arg(r"c:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\legion_ovric\google_cloud_soldier.py")
        .arg("--query")
        .arg(&payload.query)
        .output();

    match output {
        Ok(out) => {
            let success = out.status.success();
            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
            let stderr = String::from_utf8_lossy(&out.stderr).to_string();
            
            if success {
                if let Ok(results) = serde_json::from_str::<serde_json::Value>(&stdout) {
                    Json(serde_json::json!({ "status": "success", "results": results }))
                } else {
                    Json(serde_json::json!({ "status": "error", "message": "Respuesta no procesable", "raw": stdout }))
                }
            } else {
                Json(serde_json::json!({ "status": "error", "message": format!("Fallo en Soldado: {}", stderr) }))
            }
        },
        Err(e) => Json(serde_json::json!({ "status": "error", "message": format!("Fallo de invocación: {}", e) })),
    }
}

