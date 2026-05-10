use axum::{
    routing::post,
    Router,
    Json,
};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;
use tower_http::cors::{Any, CorsLayer};

#[derive(Deserialize)]
struct ActionRequest {
    actionId: u32,
}

#[derive(Serialize)]
struct ActionResponse {
    message: String,
}

async fn handle_action(Json(payload): Json<ActionRequest>) -> Json<ActionResponse> {
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
