use std::fs;
use std::process::Command;
use sysinfo::{System, Disks};
use std::sync::Mutex;
use serde_json::{Value, json};
use chrono::Local;

struct AppState {
    sys: Mutex<System>,
}

#[tauri::command]
fn minimizar_ventana(window: tauri::Window) {
    let _ = window.minimize();
}

#[tauri::command]
fn cerrar_ventana(window: tauri::Window) {
    let _ = window.close();
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
fn marcar_realidad(id: String) -> Result<(), String> {
    let path = r#"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend\dreams.json"#;
    let content = fs::read_to_string(path).map_err(|e| e.to_string())?;
    let mut dreams: Vec<Value> = serde_json::from_str(&content).map_err(|e| e.to_string())?;
    
    for dream in dreams.iter_mut() {
        if dream["id"] == id {
            dream["realidad"] = json!(true);
            break;
        }
    }
    
    fs::write(path, serde_json::to_string_pretty(&dreams).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn leer_estado_orbe() -> Result<String, String> {
    let path = r#"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\orbe_estado.json"#;
    match fs::read_to_string(path) {
        Ok(content) => Ok(content),
        Err(e) => Err(format!("Error leyendo estado: {}", e)),
    }
}

#[tauri::command]
fn obtener_telemetria(state: tauri::State<AppState>) -> Result<String, String> {
    let mut sys = state.sys.lock().unwrap();
    sys.refresh_cpu_usage();
    sys.refresh_memory();

    let cpu_usage = sys.global_cpu_info().cpu_usage();
    let total_memory = sys.total_memory();
    let used_memory = sys.used_memory();

    // Telemetría de discos
    let disks = Disks::new_with_refreshed_list();
    let mut disk_total = 0;
    let mut disk_available = 0;
    for disk in &disks {
        disk_total += disk.total_space();
        disk_available += disk.available_space();
    }
    let disk_used = disk_total - disk_available;

    let telemetry = json!({
        "cpu": cpu_usage,
        "ram_used": used_memory,
        "ram_total": total_memory,
        "disk_used": disk_used,
        "disk_total": disk_total
    });

    Ok(telemetry.to_string())
}

#[tauri::command]
fn registrar_sueno(asunto: String, descripcion: String) -> Result<(), String> {
    let path = r#"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\Orbe-Dashboard\frontend\dreams.json"#;
    let content = fs::read_to_string(path).unwrap_or_else(|_| "[]".to_string());
    let mut dreams: Vec<Value> = serde_json::from_str(&content).unwrap_or_else(|_| vec![]);
    
    let now = Local::now();
    let id = format!("S-{}-{}", now.format("%Y%m%d%H"), rand::random::<u16>());
    
    dreams.insert(0, json!({
        "id": id,
        "fecha": now.format("%Y-%m-%d %H:%M:%S").to_string(),
        "asunto": asunto,
        "descripcion": descripcion,
        "aprobado": true,
        "realidad": false
    }));
    
    fs::write(path, serde_json::to_string_pretty(&dreams).map_err(|e| e.to_string())?).map_err(|e| e.to_string())?;
    Ok(())
}

/// Traduce comandos Linux a PowerShell y los ejecuta
fn traducir_comando(cmd: &str) -> (String, Vec<String>) {
    let parts: Vec<&str> = cmd.trim().splitn(2, ' ').collect();
    let base = parts[0].to_lowercase();
    let args_str = if parts.len() > 1 { parts[1] } else { "" };

    match base.as_str() {
        "ls"    => ("powershell".into(), vec!["-Command".into(), format!("Get-ChildItem {} | Format-Table -AutoSize | Out-String -Width 200", args_str)]),
        "ll"    => ("powershell".into(), vec!["-Command".into(), format!("Get-ChildItem {} | Format-Table Mode,LastWriteTime,Length,Name -AutoSize | Out-String -Width 200", args_str)]),
        "pwd"   => ("powershell".into(), vec!["-Command".into(), "(Get-Location).Path".into()]),
        "clear" => ("powershell".into(), vec!["-Command".into(), "echo CLEAR_TERMINAL".into()]),
        "cat"   => ("powershell".into(), vec!["-Command".into(), format!("Get-Content {}", args_str)]),
        "mkdir" => ("powershell".into(), vec!["-Command".into(), format!("New-Item -ItemType Directory -Path '{}'", args_str)]),
        "rm"    => ("powershell".into(), vec!["-Command".into(), format!("Remove-Item -Recurse -Force '{}'", args_str)]),
        "cp"    => ("powershell".into(), vec!["-Command".into(), format!("Copy-Item {}", args_str)]),
        "mv"    => ("powershell".into(), vec!["-Command".into(), format!("Move-Item {}", args_str)]),
        "echo"  => ("powershell".into(), vec!["-Command".into(), format!("echo {}", args_str)]),
        "grep"  => ("powershell".into(), vec!["-Command".into(), format!("Select-String {}", args_str)]),
        "df"    => ("powershell".into(), vec!["-Command".into(), "Get-PSDrive -PSProvider FileSystem | Format-Table Name,Used,Free -AutoSize | Out-String -Width 200".into()]),
        "ps"    => ("powershell".into(), vec!["-Command".into(), "Get-Process | Sort-Object CPU -Descending | Select-Object -First 20 | Format-Table -AutoSize | Out-String -Width 200".into()]),
        "kill"  => ("powershell".into(), vec!["-Command".into(), format!("Stop-Process -Id {}", args_str)]),
        "whoami"=> ("powershell".into(), vec!["-Command".into(), "[System.Environment]::UserName".into()]),
        "uname" => ("powershell".into(), vec!["-Command".into(), "$env:OS + ' ' + [System.Environment]::OSVersion.VersionString".into()]),
        "date"  => ("powershell".into(), vec!["-Command".into(), "Get-Date".into()]),
        "find"  => ("powershell".into(), vec!["-Command".into(), format!("Get-ChildItem -Recurse -Filter {}", args_str)]),
        // Pasar directo a PowerShell si no hay traducción
        _       => ("powershell".into(), vec!["-Command".into(), cmd.to_string()]),
    }
}

#[tauri::command]
fn ejecutar_comando(comando: String) -> Result<String, String> {
    if comando.trim().is_empty() {
        return Ok(String::new());
    }
    
    // Comandos internos de la Orbe-Console
    if comando.trim() == "orbe --help" {
        return Ok("╔══════════════════════════════╗\n║   ORBE-CONSOLE COMANDOS      ║\n╠══════════════════════════════╣\n║ ls / ll    → listar dir      ║\n║ pwd        → ruta actual     ║\n║ cat <file> → leer archivo    ║\n║ mkdir <n>  → crear carpeta   ║\n║ rm <n>     → eliminar        ║\n║ ps         → procesos activos║\n║ df         → espacio discos  ║\n║ whoami     → identidad       ║\n║ date       → fecha actual    ║\n║ clear      → limpiar pantalla║\n║ orbe --help → este menu      ║\n╚══════════════════════════════╝".into());
    }

    let (program, args) = traducir_comando(&comando);
    
    match Command::new(&program).args(&args).output() {
        Ok(output) => {
            let stdout = String::from_utf8_lossy(&output.stdout).to_string();
            let stderr = String::from_utf8_lossy(&output.stderr).to_string();
            if !stderr.is_empty() && stdout.is_empty() {
                Err(stderr.trim().to_string())
            } else {
                Ok(stdout.trim_end().to_string())
            }
        }
        Err(e) => Err(format!("Error ejecutando comando: {}", e)),
    }
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    let mut sys = System::new_all();
    sys.refresh_all();
    
    tauri::Builder::default()
        .manage(AppState { sys: Mutex::new(sys) })
        .plugin(tauri_plugin_opener::init())
        .invoke_handler(tauri::generate_handler![
            leer_suenos, 
            leer_estado_orbe, 
            obtener_telemetria, 
            registrar_sueno, 
            marcar_realidad,
            minimizar_ventana,
            cerrar_ventana,
            ejecutar_comando
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
