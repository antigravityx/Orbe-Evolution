use axum::{
    routing::post,
    Router,
    Json,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};

mod core_crypto;

#[derive(Deserialize)]
struct ActionRequest {
    actionId: u32,
    payload: Option<String>,
    password: Option<String>,
}

#[derive(Serialize)]
struct ActionResponse {
    message: String,
}

async fn handle_action(Json(payload): Json<ActionRequest>) -> Json<ActionResponse> {
    if payload.actionId == 1 {
        let target = payload.payload.unwrap_or_default();
        let pass = payload.password.unwrap_or_default();
        if target.is_empty() || pass.is_empty() {
            return Json(ActionResponse { message: "[ERROR]: Ruta o contraseña vacías.".to_string() });
        }

        match core_crypto::create_capsule(&target, &pass) {
            Ok(ruta_capsula) => {
                let message = format!("[RUST NATIVO]: ¡Cápsula forjada con puro código Rust en tiempo récord!\n[OK] Sellado en: {}", ruta_capsula);
                return Json(ActionResponse { message });
            }
            Err(e) => {
                let message = format!("[ERROR RUST]: Fallo en forja de cápsula: {}", e);
                return Json(ActionResponse { message });
            }
        }
    }

    let message = format!(
        "Acción {} procesada por el servidor Axum en Rust. Orbe está listo y conectado al metal puro.",
        payload.actionId
    );
    Json(ActionResponse { message })
}

#[tokio::main]
async fn main() {
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods(Any)
        .allow_headers(Any);

    let app = Router::new()
        .route("/api/action", post(handle_action))
        .layer(cors);

    let addr = SocketAddr::from(([127, 0, 0, 1], 3000));
    println!("Servidor Verix NextGen API corriendo en http://{}", addr);

    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
