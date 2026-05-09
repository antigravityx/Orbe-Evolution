mod health;
mod memory;

use health::SystemHealth;
use memory::MemoryAnchor;
use std::time::Duration;
use tokio::time::sleep;
use colored::*;

#[tokio::main]
async fn main() {
    println!("{}", "=== INICIANDO NÚCLEO ORBE BRAIN CORE (RUST) ===".bold().magenta());
    
    // Anclaje de inicio
    let start_anchor = MemoryAnchor::new("Despertar del Cerebro Rust", "SUCCESS");
    start_anchor.seal();

    loop {
        // 1. Monitoreo de Salud
        let status = SystemHealth::collect();
        status.report();

        // 2. Simulación de procesamiento paralelo
        tokio::spawn(async {
            // Aquí irían tareas pesadas de discernimiento o limpieza de archivos
            // Por ahora solo un latido de vida
        });

        // 3. Espera para el siguiente ciclo
        sleep(Duration::from_secs(10)).await;
        println!("\n{}", "--- Latido de Vida ---".dimmed());
    }
}
