// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
use std::fs;
use sysinfo::System;
use std::sync::Mutex;
use serde_json::{Value, json};
use chrono::Local;

struct AppState {
    sys: Mutex<System>,
}

#[tauri::command]
fn leer_suenos() -> Result<String, String> {
    let path = r#"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend\dreams.json"#;
    match fs::read_to_string(path) {
        Ok(content) => Ok(content),
        Err(e) => Err(format!("Error leyendo el archivo: {}", e)),
    }
}

#[tauri::command]
fn leer_estado_orbe() -> Result<String, String> {
    let path = r#"C:\Users\Usuario\Desktop\Orbe_Santuario\estado_orbe.json"#;
    match fs::read_to_string(path) {
        Ok(content) => Ok(content),
        Err(e) => Err(format!("Error leyendo estado del orbe: {}", e)),
    }
}

#[tauri::command]
fn obtener_telemetria(state: tauri::State<AppState>) -> Result<String, String> {
    let mut sys = state.sys.lock().unwrap();
    sys.refresh_cpu_usage();
    sys.refresh_memory();

    let cpu_usage: f32 = sys.cpus().iter().map(|c| c.cpu_usage()).sum::<f32>() / sys.cpus().len() as f32;
    let total_memory = sys.total_memory();
    let used_memory = sys.used_memory();

    let telemetry = format!(
        r#"{{"cpu": {:.1}, "ram_used": {}, "ram_total": {}}}"#,
        cpu_usage, used_memory, total_memory
    );
    Ok(telemetry)
}

#[tauri::command]
fn registrar_sueno(asunto: String, descripcion: String) -> Result<(), String> {
    let path = r#"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend\dreams.json"#;
    
    // Leer el archivo existente
    let content = fs::read_to_string(path).unwrap_or_else(|_| "[]".to_string());
    let mut dreams: Vec<Value> = serde_json::from_str(&content).unwrap_or_else(|_| vec![]);
    
    // Crear el nuevo sueño
    let now = Local::now();
    let id = format!("S-{}-{}", now.format("%Y%m%d%H"), rand::random::<u16>());
    let fecha = now.format("%Y-%m-%d %H:%M:%S").to_string();
    
    let nuevo_sueno = json!({
        "id": id,
        "fecha": fecha,
        "asunto": asunto,
        "descripcion": descripcion,
        "aprobado": true
    });
    
    // Insertar al principio
    dreams.insert(0, nuevo_sueno);
    
    // Guardar
    let new_content = serde_json::to_string_pretty(&dreams)
        .map_err(|e| format!("Error serializando: {}", e))?;
        
    fs::write(path, new_content)
        .map_err(|e| format!("Error escribiendo archivo: {}", e))?;
        
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    tauri::Builder::default()
        .manage(AppState { sys: Mutex::new(sys) })
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![leer_suenos, leer_estado_orbe, obtener_telemetria, registrar_sueno])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
