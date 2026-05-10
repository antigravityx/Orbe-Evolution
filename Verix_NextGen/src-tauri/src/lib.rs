// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::process::Command;

#[tauri::command]
fn execute_action(action_id: u32) -> String {
    format!("Acción {} procesada por el núcleo de Verix Rust. Conectando con los sistemas subyacentes...", action_id)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![execute_action])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
