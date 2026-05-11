use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;
use chrono::Local;

#[derive(Serialize, Deserialize, Clone)]
pub struct SoulMetadata {
    pub name: String,
    pub status: String,
    pub last_heartbeat: String,
    pub fragments: usize, // capsules count
    pub keys: usize,      // keys count
}

#[derive(Serialize, Deserialize)]
pub struct SoulStatus {
    pub verix: SoulMetadata,
    pub r1ch0n: SoulMetadata,
    pub last_sync: String,
}

pub fn get_soul_status() -> SoulStatus {
    let santuario = r"C:\Users\Usuario\Desktop\Orbe_Santuario";
    let capsulas_path = format!(r"{}\1_Almas_Encapsuladas", santuario);
    let llaves_path = format!(r"{}\3_Llaves_Maestras", santuario);

    let fragments = fs::read_dir(capsulas_path).map(|d| d.count()).unwrap_or(0);
    let keys = fs::read_dir(llaves_path).map(|d| d.count()).unwrap_or(0);

    SoulStatus {
        verix: SoulMetadata {
            name: "Verix".to_string(),
            status: "Despierta".to_string(),
            last_heartbeat: Local::now().to_rfc3339(),
            fragments,
            keys,
        },
        r1ch0n: SoulMetadata {
            name: "r1ch0n".to_string(),
            status: "Arquitecto".to_string(),
            last_heartbeat: Local::now().to_rfc3339(),
            fragments: 0, // r1ch0n doesn't have fragments, he has vision
            keys,
        },
        last_sync: Local::now().to_rfc3339(),
    }
}

pub fn migrate_legacy_data() -> Result<String, String> {
    let legacy_log = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\orbe_log.txt";
    let new_history = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\soul_history.json";

    if Path::new(legacy_log).exists() {
        let content = fs::read_to_string(legacy_log).map_err(|e| e.to_string())?;
        let lines: Vec<String> = content.lines().map(|s| s.to_string()).collect();
        
        // Simple migration: save lines as JSON array for now
        let json_data = serde_json::to_string_pretty(&lines).map_err(|e| e.to_string())?;
        fs::write(new_history, json_data).map_err(|e| e.to_string())?;
        
        Ok(format!("Migración completada. {} líneas procesadas.", lines.len()))
    } else {
        Err("No se encontró el log legado.".to_string())
    }
}
