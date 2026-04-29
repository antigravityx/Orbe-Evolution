// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::fs;

#[tauri::command]
fn leer_suenos() -> Result<String, String> {
    let path = r#"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend\dreams.json"#;
    match fs::read_to_string(path) {
        Ok(content) => Ok(content),
        Err(e) => Err(format!("Error leyendo el archivo: {}", e)),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![leer_suenos])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
