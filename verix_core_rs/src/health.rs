// ══════════════════════════════════════════════════
// 💚 VERIX HEALTH — Sanitario del Sistema
// ══════════════════════════════════════════════════
//
// Migrado desde: temp_health_soldier.py
// Misión: Monitoreo de recursos, limpieza y optimización.

use serde::{Deserialize, Serialize};
use sysinfo::System;
use std::path::Path;
use std::fs;

/// Reporte completo de salud del sistema
#[derive(Debug, Serialize, Deserialize)]
pub struct HealthReport {
    pub cpu_usage_percent: f32,
    pub cpu_cores: usize,
    pub total_memory_gb: f64,
    pub used_memory_gb: f64,
    pub memory_usage_percent: f64,
    pub total_disk_gb: f64,
    pub available_disk_gb: f64,
    pub disk_usage_percent: f64,
    pub uptime_seconds: u64,
    pub temp_files_found: usize,
    pub recoverable_mb: f64,
    pub timestamp: String,
}

/// Resultado de un escaneo de archivos temporales
#[derive(Debug, Serialize, Deserialize)]
pub struct TempScanResult {
    pub files: Vec<String>,
    pub total_size_mb: f64,
    pub count: usize,
}

/// Resultado de una purga
#[derive(Debug, Serialize, Deserialize)]
pub struct PurgeResult {
    pub files_deleted: usize,
    pub space_recovered_mb: f64,
    pub errors: Vec<String>,
}

/// Obtiene un diagnóstico completo del sistema
pub fn system_diagnostics() -> HealthReport {
    let mut sys = System::new_all();
    sys.refresh_all();

    let total_memory = sys.total_memory();
    let used_memory = sys.used_memory();
    let cpu_usage: f32 = if sys.cpus().is_empty() {
        0.0
    } else {
        sys.cpus().iter().map(|c| c.cpu_usage()).sum::<f32>() / sys.cpus().len() as f32
    };

    // Disk
    let disks = sysinfo::Disks::new_with_refreshed_list();
    let mut total_disk: u64 = 0;
    let mut available_disk: u64 = 0;
    for disk in disks.list() {
        total_disk += disk.total_space();
        available_disk += disk.available_space();
    }

    // Quick temp scan
    let temp_scan = scan_temp_files(r"C:\Users\Usuario\AppData\Local\Temp");

    HealthReport {
        cpu_usage_percent: (cpu_usage * 100.0).round() / 100.0,
        cpu_cores: sys.cpus().len(),
        total_memory_gb: round2(total_memory as f64 / 1_073_741_824.0),
        used_memory_gb: round2(used_memory as f64 / 1_073_741_824.0),
        memory_usage_percent: round2(used_memory as f64 / total_memory as f64 * 100.0),
        total_disk_gb: round2(total_disk as f64 / 1_073_741_824.0),
        available_disk_gb: round2(available_disk as f64 / 1_073_741_824.0),
        disk_usage_percent: round2((total_disk - available_disk) as f64 / total_disk as f64 * 100.0),
        uptime_seconds: System::uptime(),
        temp_files_found: temp_scan.count,
        recoverable_mb: temp_scan.total_size_mb,
        timestamp: chrono::Local::now().to_rfc3339(),
    }
}

/// Escanea archivos temporales en un directorio
pub fn scan_temp_files(path: &str) -> TempScanResult {
    let mut files = Vec::new();
    let mut total_size: u64 = 0;

    if let Ok(entries) = fs::read_dir(path) {
        for entry in entries.flatten() {
            if let Ok(meta) = entry.metadata() {
                if meta.is_file() {
                    let size = meta.len();
                    total_size += size;
                    if let Some(name) = entry.path().to_str() {
                        files.push(name.to_string());
                    }
                }
            }
        }
    }

    TempScanResult {
        count: files.len(),
        total_size_mb: round2(total_size as f64 / 1_048_576.0),
        files,
    }
}

/// Purga archivos temporales de un directorio
pub fn purge_temp(path: &str) -> PurgeResult {
    let scan = scan_temp_files(path);
    let mut deleted = 0;
    let mut errors = Vec::new();
    let mut recovered: u64 = 0;

    for file_path in &scan.files {
        let p = Path::new(file_path);
        if let Ok(meta) = fs::metadata(p) {
            let size = meta.len();
            match fs::remove_file(p) {
                Ok(_) => {
                    deleted += 1;
                    recovered += size;
                }
                Err(e) => {
                    errors.push(format!("{}: {}", file_path, e));
                }
            }
        }
    }

    PurgeResult {
        files_deleted: deleted,
        space_recovered_mb: round2(recovered as f64 / 1_048_576.0),
        errors,
    }
}

/// Genera un reporte de salud en formato JSON string
pub fn health_report_json() -> String {
    let report = system_diagnostics();
    serde_json::to_string_pretty(&report).unwrap_or_else(|_| "{}".to_string())
}

fn round2(v: f64) -> f64 {
    (v * 100.0).round() / 100.0
}
