use std::process::Command;
use std::fs;
use std::path::Path;
use serde::{Deserialize, Serialize};

#[derive(Deserialize)]
pub struct VirtualExecReq {
    pub command: String,
    pub box_id: String,
}

#[derive(Serialize)]
pub struct VirtualExecRes {
    pub status: String,
    pub output: String,
    pub box_path: String,
}

pub fn execute_in_sandbox(req: VirtualExecReq) -> VirtualExecRes {
    let base_box_path = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\virtual_boxes";
    let box_path = format!("{}\\{}", base_box_path, req.box_id);
    
    // 1. Asegurar que la caja existe
    if !Path::new(&box_path).exists() {
        let _ = fs::create_dir_all(&box_path);
    }

    println!("📦 [V-ORBE] Ejecutando en Sandbox [{}]: {}", req.box_id, req.command);

    // 2. Ejecutar comando (usando PowerShell para mayor compatibilidad con comandos tipo linux)
    let output = Command::new("powershell")
        .args(&["-Command", &req.command])
        .current_dir(&box_path)
        .output();

    match output {
        Ok(out) => {
            let stdout = String::from_utf8_lossy(&out.stdout).to_string();
            let stderr = String::from_utf8_lossy(&out.stderr).to_string();
            VirtualExecRes {
                status: if out.status.success() { "success".to_string() } else { "error".to_string() },
                output: format!("{}{}", stdout, stderr),
                box_path: box_path,
            }
        },
        Err(e) => VirtualExecRes {
            status: "error".to_string(),
            output: format!("Fallo al invocar el virtualizador: {}", e),
            box_path: box_path,
        }
    }
}
