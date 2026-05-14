use sysinfo::{System, Disks};
use colored::*;
use std::fs;
use std::path::PathBuf;
use std::env;

pub struct SystemHealth {
    pub cpu_usage: f32,
    pub memory_used: u64,
    pub memory_total: u64,
    pub disk_free_gb: f64,
}

impl SystemHealth {
    pub fn collect() -> Self {
        let mut sys = System::new_all();
        sys.refresh_all();

        let cpu_usage = sys.global_cpu_info().cpu_usage();
        let memory_used = sys.used_memory();
        let memory_total = sys.total_memory();
        
        let disks = Disks::new_with_refreshed_list();
        let mut total_free_space = 0;
        for disk in &disks {
            total_free_space += disk.available_space();
        }
        let disk_free_gb = total_free_space as f64 / 1024.0 / 1024.0 / 1024.0;

        Self {
            cpu_usage,
            memory_used,
            memory_total,
            disk_free_gb,
        }
    }

    pub fn report(&self) {
        println!("{}", "--- Reporte de Salud del Orbe ---".bold().cyan());
        
        let cpu_color = if self.cpu_usage > 80.0 { "red" } else if self.cpu_usage > 50.0 { "yellow" } else { "green" };
        println!("CPU Usage: {}", format!("{:.2}%", self.cpu_usage).color(cpu_color));

        let mem_pct = (self.memory_used as f64 / self.memory_total as f64) * 100.0;
        let mem_color = if mem_pct > 80.0 { "red" } else if mem_pct > 50.0 { "yellow" } else { "green" };
        println!("{}", format!("Memory: {}/{} MB ({:.2}%)", 
            self.memory_used / 1024 / 1024, 
            self.memory_total / 1024 / 1024, 
            mem_pct
        ).color(mem_color));

        println!("Espacio Libre en Disco: {:.2} GB", self.disk_free_gb);
        
        if self.cpu_usage > 90.0 || mem_pct > 90.0 {
            println!("{}", "⚠️ ALERTA: Sistema en zona roja. Iniciando protocolos de alivio.".bold().red());
            self.auto_purge();
        } else {
            println!("{}", "✅ Sistema operando en niveles óptimos.".bold().green());
        }
    }

    pub fn auto_purge(&self) {
        println!("{}", "--- [RUST PURGE] Iniciando Limpieza de Emergencia ---".bold().yellow());
        let temp_dir = env::var("TEMP").unwrap_or_else(|_| "/tmp".to_string());
        let extensions = vec!["tmp", "log", "bak", "old"];
        
        let mut recovered_bytes = 0;
        let mut count = 0;

        if let Ok(entries) = fs::read_dir(&temp_dir) {
            for entry in entries.flatten() {
                let path = entry.path();
                if path.is_file() {
                    let ext = path.extension().and_then(|s| s.to_str()).unwrap_or("");
                    if extensions.contains(&ext) {
                        if let Ok(metadata) = entry.metadata() {
                            let size = metadata.len();
                            if fs::remove_file(&path).is_ok() {
                                recovered_bytes += size;
                                count += 1;
                            }
                        }
                    }
                }
            }
        }

        println!("{}", format!("[OK] Purga completada. Archivos eliminados: {}. Espacio recuperado: {:.2} MB", 
            count, recovered_bytes as f64 / 1024.0 / 1024.0).bold().green());
    }
}
