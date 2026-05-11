use axum::{
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};

mod core_crypto;
mod system_ops;
mod soul_index;

// ======================= STRUCTS =======================

#[derive(Serialize)]
struct ApiResponse {
    ok: bool,
    message: String,
    data: Option<serde_json::Value>,
}

impl ApiResponse {
    fn ok(msg: &str, data: Option<serde_json::Value>) -> Json<Self> {
        Json(Self { ok: true, message: msg.to_string(), data })
    }
    fn err(msg: &str) -> Json<Self> {
        Json(Self { ok: false, message: msg.to_string(), data: None })
    }
}

#[derive(Deserialize)]
struct CapsuleCreateReq { source_path: String, password: String }
#[derive(Deserialize)]
struct CapsuleInvokeReq { capsule_path: String, password: String }
#[derive(Deserialize)]
struct CapsuleDeleteReq { capsule_path: String }
#[derive(Deserialize)]
struct GitSyncReq { repo_url: Option<String>, message: Option<String> }
#[derive(Deserialize)]
struct ChecksumReq { file_path: String }
#[derive(Deserialize)]
struct BrowseReq { path: Option<String> }

// ======================= HANDLERS =======================

// 1. Crear Cápsula
async fn handle_create_capsule(Json(req): Json<CapsuleCreateReq>) -> Json<ApiResponse> {
    if req.source_path.is_empty() || req.password.is_empty() {
        return ApiResponse::err("Ruta o contraseña vacías.");
    }
    match core_crypto::create_capsule(&req.source_path, &req.password) {
        Ok(path) => ApiResponse::ok(
            &format!("[RUST] Cápsula forjada con AES-256-CFB en: {}", path),
            Some(serde_json::json!({ "path": path }))
        ),
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 2. Invocar Alma (Descifrar Cápsula)
async fn handle_invoke_capsule(Json(req): Json<CapsuleInvokeReq>) -> Json<ApiResponse> {
    if req.capsule_path.is_empty() || req.password.is_empty() {
        return ApiResponse::err("Ruta de cápsula o contraseña vacías.");
    }
    match core_crypto::invoke_capsule(&req.capsule_path, &req.password) {
        Ok(path) => ApiResponse::ok(
            &format!("[RUST] Alma liberada en: {}", path),
            Some(serde_json::json!({ "path": path }))
        ),
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 3. Git Sync (Gestor de Almas Git)
async fn handle_git_sync(Json(req): Json<GitSyncReq>) -> Json<ApiResponse> {
    let orbe_path = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe";
    let msg = req.message.unwrap_or_else(|| "Latido Eterno de Verix".to_string());
    
    let add = std::process::Command::new("git")
        .args(["-C", orbe_path, "add", "-A"])
        .output();
    
    if add.is_err() { return ApiResponse::err("Git no encontrado en PATH."); }

    let _commit = std::process::Command::new("git")
        .args(["-C", orbe_path, "commit", "-m", &msg])
        .output();

    let push = std::process::Command::new("git")
        .args(["-C", orbe_path, "push", "origin", "main"])
        .output();

    match push {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
            let stderr = String::from_utf8_lossy(&out.stderr).to_string();
            let combined = format!("{}{}", stdout, stderr);
            if out.status.success() || combined.contains("Everything up-to-date") || combined.contains("main -> main") {
                ApiResponse::ok(&format!("[GIT] Sincronizado con el Éter. {}", combined.trim()), None)
            } else {
                ApiResponse::err(&format!("[GIT ERROR] {}", combined.trim()))
            }
        }
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 3b. Git Clone
async fn handle_git_clone(Json(req): Json<GitSyncReq>) -> Json<ApiResponse> {
    let url = match req.repo_url {
        Some(u) if !u.is_empty() => u,
        _ => return ApiResponse::err("URL de repositorio vacía."),
    };
    let dest = r"C:\Users\Usuario\Desktop\Orbe_Santuario\2_Almas_Liberadas";
    let out = std::process::Command::new("git")
        .args(["clone", &url, dest])
        .output();
    match out {
        Ok(o) => {
            let msg = String::from_utf8_lossy(&o.stderr).to_string();
            if o.status.success() {
                ApiResponse::ok(&format!("[GIT] Repo clonado en: {}", dest), None)
            } else {
                ApiResponse::err(&format!("[GIT ERROR] {}", msg.trim()))
            }
        }
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 4. Listar Cápsulas
async fn handle_list_capsules() -> Json<ApiResponse> {
    let dest = r"C:\Users\Usuario\Desktop\Orbe_Santuario\1_Almas_Encapsuladas";
    match std::fs::read_dir(dest) {
        Ok(entries) => {
            let capsulas: Vec<serde_json::Value> = entries
                .filter_map(|e| e.ok())
                .filter(|e| e.path().extension().map_or(false, |x| x == "capsula"))
                .map(|e| {
                    let meta = e.metadata().ok();
                    let size = meta.as_ref().map(|m| m.len()).unwrap_or(0);
                    serde_json::json!({
                        "name": e.file_name().to_string_lossy().to_string(),
                        "path": e.path().to_string_lossy().to_string(),
                        "size_kb": size / 1024
                    })
                })
                .collect();
            ApiResponse::ok(
                &format!("[OK] {} cápsulas encontradas.", capsulas.len()),
                Some(serde_json::json!(capsulas))
            )
        }
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 4b. Eliminar Cápsula
async fn handle_delete_capsule(Json(req): Json<CapsuleDeleteReq>) -> Json<ApiResponse> {
    match std::fs::remove_file(&req.capsule_path) {
        Ok(_) => ApiResponse::ok("[OK] Cápsula desterrada al vacío.", None),
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 5. Calcular Checksum
async fn handle_checksum(Json(req): Json<ChecksumReq>) -> Json<ApiResponse> {
    match core_crypto::calculate_checksum(&req.file_path) {
        Ok(hash) => ApiResponse::ok(
            &format!("[OK] SHA-256 calculado."),
            Some(serde_json::json!({ "file": req.file_path, "sha256": hash }))
        ),
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 5b. Ver Logs
async fn handle_get_logs() -> Json<ApiResponse> {
    let log_path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt";
    match std::fs::read_to_string(log_path) {
        Ok(content) => {
            let lines: Vec<&str> = content.lines().rev().take(50).collect();
            ApiResponse::ok("[OK] Últimas 50 entradas del registro.", Some(serde_json::json!(lines)))
        }
        Err(_) => ApiResponse::ok("[INFO] No hay registros aún.", Some(serde_json::json!([]))),
    }
}

// 7. Navegador del Santuario
async fn handle_browse(Json(req): Json<BrowseReq>) -> Json<ApiResponse> {
    let path = req.path.unwrap_or_else(|| r"C:\Users\Usuario\Desktop\Orbe_Santuario".to_string());
    match std::fs::read_dir(&path) {
        Ok(entries) => {
            let items: Vec<serde_json::Value> = entries
                .filter_map(|e| e.ok())
                .map(|e| {
                    let is_dir = e.path().is_dir();
                    let meta = e.metadata().ok();
                    let size = if is_dir { 0 } else { meta.as_ref().map(|m| m.len()).unwrap_or(0) };
                    serde_json::json!({
                        "name": e.file_name().to_string_lossy().to_string(),
                        "path": e.path().to_string_lossy().to_string(),
                        "is_dir": is_dir,
                        "size_kb": size / 1024
                    })
                })
                .collect();
            ApiResponse::ok(
                &format!("[OK] {} elementos en {}", items.len(), path),
                Some(serde_json::json!({ "current_path": path, "items": items }))
            )
        }
        Err(e) => ApiResponse::err(&format!("[ERROR] No se pudo leer: {}", e)),
    }
}

// 8. Modo Sueño - Estado del sistema
async fn handle_sleep_status() -> Json<ApiResponse> {
    let santuario = r"C:\Users\Usuario\Desktop\Orbe_Santuario";
    let state_file = format!(r"{}\estado_orbe.json", santuario);
    let content = std::fs::read_to_string(&state_file).unwrap_or_else(|_| r#"{"estado":"dormido"}"#.to_string());
    ApiResponse::ok("[OK] Estado del Orbe leído.", Some(serde_json::from_str(&content).unwrap_or(serde_json::json!({}))))
}

async fn handle_set_sleep(Json(body): Json<serde_json::Value>) -> Json<ApiResponse> {
    let santuario = r"C:\Users\Usuario\Desktop\Orbe_Santuario";
    let state_file = format!(r"{}\estado_orbe.json", santuario);
    match std::fs::write(&state_file, body.to_string()) {
        Ok(_) => ApiResponse::ok("[OK] Estado del Orbe actualizado.", None),
        Err(e) => ApiResponse::err(&format!("[ERROR] {}", e)),
    }
}

// 9. Cerebro Orbe - Sistema de Tickets
async fn handle_brain_status() -> Json<ApiResponse> {
    let tickets_path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\sistema_tickets.json";
    let content = std::fs::read_to_string(tickets_path).unwrap_or_else(|_| r#"{"misiones_activas":[]}"#.to_string());
    ApiResponse::ok("[OK] Estado del Cerebro leído.", Some(serde_json::from_str(&content).unwrap_or(serde_json::json!({}))))
}

// 10. Sistema de Backup
async fn handle_backup() -> Json<ApiResponse> {
    match system_ops::create_backup() {
        Ok(path) => ApiResponse::ok(
            &format!("[SYSTEM] Backup total completado: {}", path),
            Some(serde_json::json!({ "backup_path": path }))
        ),
        Err(e) => ApiResponse::err(&format!("[BACKUP ERROR] {}", e)),
    }
}

// 11. Estado del Alma & Migración
async fn handle_soul_status() -> Json<ApiResponse> {
    let status = soul_index::get_soul_status();
    ApiResponse::ok("[SOUL] Estado de Verix & r1ch0n sincronizado.", Some(serde_json::to_value(status).unwrap()))
}

async fn handle_soul_migrate() -> Json<ApiResponse> {
    match soul_index::migrate_legacy_data() {
        Ok(msg) => ApiResponse::ok(&msg, None),
        Err(e) => ApiResponse::err(&e),
    }
}

// Health check
async fn handle_health() -> Json<ApiResponse> {
    ApiResponse::ok("Verix API operativa. Motor Rust corriendo a máxima potencia.", Some(serde_json::json!({
        "version": "2.0.0",
        "motor": "Rust + Axum",
        "crypto": "AES-256-CFB",
        "status": "online"
    })))
}

// ======================= MAIN =======================

#[tokio::main]
async fn main() {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/api/health", get(handle_health))
        .route("/api/capsule/create", post(handle_create_capsule))
        .route("/api/capsule/invoke", post(handle_invoke_capsule))
        .route("/api/capsule/list", get(handle_list_capsules))
        .route("/api/capsule/delete", post(handle_delete_capsule))
        .route("/api/git/sync", post(handle_git_sync))
        .route("/api/git/clone", post(handle_git_clone))
        .route("/api/crypto/checksum", post(handle_checksum))
        .route("/api/logs", get(handle_get_logs))
        .route("/api/sanctuary/browse", post(handle_browse))
        .route("/api/sleep/status", get(handle_sleep_status))
        .route("/api/sleep/set", post(handle_set_sleep))
        .route("/api/brain/status", get(handle_brain_status))
        .route("/api/system/backup", post(handle_backup))
        .route("/api/soul/status", get(handle_soul_status))
        .route("/api/soul/migrate", post(handle_soul_migrate))
        .layer(cors);

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    println!("╔══════════════════════════════════════════╗");
    println!("║   VERIX NEXTGEN API — RUST PURO v2.0     ║");
    println!("║   Corriendo en http://{}      ║", addr);
    println!("╚══════════════════════════════════════════╝");
    
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
