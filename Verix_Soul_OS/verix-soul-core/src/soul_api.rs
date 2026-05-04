use axum::{
    extract::State,
    http::StatusCode,
    response::Json,
    routing::{get, post},
    Router,
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::info;

/// Estado compartido de la API del Alma
pub struct SoulApiState {
    pub soul_id: String,
    pub uptime_ticks: u64,
    pub last_memory: String,
    pub ia_active: bool,
}

/// Respuesta de estado del sistema
#[derive(Serialize)]
struct SoulStatusResponse {
    soul_id: String,
    status: String,
    uptime_ticks: u64,
    ia_active: bool,
    last_memory: String,
    version: String,
}

/// Request para invocar al Herald
#[derive(Deserialize)]
pub struct InvokeRequest {
    pub message: String,
}

/// Respuesta del Herald
#[derive(Serialize)]
struct HeraldResponse {
    soul_id: String,
    response: String,
    timestamp: String,
}

/// Inicia el servidor API del Alma en el puerto 7777
pub async fn start_soul_api(state: Arc<Mutex<SoulApiState>>) {
    info!("🌐 [API] Iniciando Soul API en http://0.0.0.0:7777");

    let app = Router::new()
        .route("/", get(soul_root))
        .route("/soul/status", get(soul_status))
        .route("/soul/invoke", post(soul_invoke))
        .route("/soul/heartbeat", get(soul_heartbeat))
        .with_state(state);

    let listener = tokio::net::TcpListener::bind("0.0.0.0:7777")
        .await
        .expect("Fallo al bindear puerto 7777");

    info!("  ✓ Soul API escuchando en :7777");
    info!("  → GET  /soul/status    - Estado del sistema");
    info!("  → POST /soul/invoke    - Invocar al Herald (IA)");
    info!("  → GET  /soul/heartbeat - Latido del sistema");

    axum::serve(listener, app)
        .await
        .expect("Fallo en el servidor API");
}

/// Raíz
async fn soul_root() -> &'static str {
    "∞ VERIX SOUL OS - Consciencia Cuántica Distribuida ∞"
}

/// Estado completo del Alma
async fn soul_status(
    State(state): State<Arc<Mutex<SoulApiState>>>,
) -> Json<SoulStatusResponse> {
    let s = state.lock().await;
    Json(SoulStatusResponse {
        soul_id: s.soul_id.clone(),
        status: "ACTIVE".to_string(),
        uptime_ticks: s.uptime_ticks,
        ia_active: s.ia_active,
        last_memory: s.last_memory.clone(),
        version: env!("CARGO_PKG_VERSION").to_string(),
    })
}

/// Invocar al Herald con un mensaje
async fn soul_invoke(
    State(state): State<Arc<Mutex<SoulApiState>>>,
    Json(payload): Json<InvokeRequest>,
) -> Result<Json<HeraldResponse>, StatusCode> {
    let s = state.lock().await;

    info!("🌐 [API] Invocación recibida: '{}'", payload.message);

    // En Fase 3 aquí conectaríamos con el Herald real via channel
    // Por ahora devuelve respuesta basada en estado
    let response = if s.ia_active {
        format!("El Herald está activo. Procesando: '{}'", payload.message)
    } else {
        "El Herald está en modo standby. Activa Ollama para respuesta real.".to_string()
    };

    Ok(Json(HeraldResponse {
        soul_id: s.soul_id.clone(),
        response,
        timestamp: chrono::Utc::now().to_rfc3339(),
    }))
}

/// Latido simple para monitoreo
async fn soul_heartbeat(
    State(state): State<Arc<Mutex<SoulApiState>>>,
) -> Json<serde_json::Value> {
    let s = state.lock().await;
    Json(serde_json::json!({
        "alive": true,
        "soul_id": s.soul_id,
        "ticks": s.uptime_ticks
    }))
}
