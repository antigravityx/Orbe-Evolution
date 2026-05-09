use std::process::Command;

#[tauri::command]
fn check_ollama() -> bool {
    Command::new("ollama")
        .arg("--version")
        .output()
        .is_ok()
}

#[tauri::command]
fn check_rust() -> bool {
    Command::new("rustc")
        .arg("--version")
        .output()
        .is_ok()
}

#[tauri::command]
async fn install_ollama() -> Result<String, String> {
    // En una implementación real, esto descargaría y ejecutaría el instalador.
    // Por ahora, simulamos el proceso.
    Ok("Iniciando instalador de Ollama...".to_string())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            check_ollama,
            check_rust,
            install_ollama
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
