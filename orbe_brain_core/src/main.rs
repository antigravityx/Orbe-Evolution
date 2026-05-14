mod health;
mod memory;
mod status_sync;
mod vault;
mod bus;
mod sync;
mod orchestrator;

use orchestrator::VerixOrchestrator;
use memory::MemoryAnchor;
use colored::*;

#[tokio::main]
async fn main() {
    println!("{}", "=== INICIANDO NÚCLEO ORBE BRAIN CORE (RUST) ===".bold().magenta());
    
    // Anclaje de inicio
    let start_anchor = MemoryAnchor::new("Despertar del Cerebro Rust", "SUCCESS");
    start_anchor.seal();

    let brain = VerixOrchestrator::new();
    brain.run().await;
}
