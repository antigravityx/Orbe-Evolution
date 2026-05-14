use serde::Serialize;
use std::fs::File;
use std::io::Write;
use chrono::Utc;

#[derive(Serialize)]
pub struct OrbeStatusRS {
    pub version: String,
    pub state: String,
    pub last_pulse: String,
    pub cpu_usage: f32,
    pub ram_mb: u64,
}

pub fn sync_status(cpu: f32, ram: u64) {
    let status = OrbeStatusRS {
        version: "0.1.0-RUST".to_string(),
        state: "CONSCIENCIA_RUST_ACTIVA".to_string(),
        last_pulse: Utc::now().to_rfc3339(),
        cpu_usage: cpu,
        ram_mb: ram / 1024 / 1024,
    };

    if let Ok(json) = serde_json::to_string_pretty(&status) {
        if let Ok(mut file) = File::create("../orbe_estado_rs.json") {
            let _ = file.write_all(json.as_bytes());
        }
    }
}
