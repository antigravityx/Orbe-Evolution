use crate::health::SystemHealth;
use crate::bus::MessageBus;
use crate::vault::VerixVault;
use crate::status_sync;
use std::process::Command;
use std::time::Duration;
use tokio::time::sleep;
use colored::*;
use serde_json::json;
use std::path::Path;

pub struct VerixOrchestrator {
    pub name: String,
}

impl VerixOrchestrator {
    pub fn new() -> Self {
        Self { name: "Cerebro-Rust".to_string() }
    }

    pub async fn run(&self) {
        println!("{}", "--- [ORCHESTRATOR] Cerebro de Rust Iniciado ---".bold().magenta());

        loop {
            // 1. Diagnóstico de Salud
            let health = SystemHealth::collect();
            health.report();
            
            // Sincronizar estado para la UI
            status_sync::sync_status(health.cpu_usage, health.memory_used);

            // 2. Procesar Bus de Mensajes
            self.process_bus().await;

            // 3. Verificar Agenda (Placeholder por ahora)
            // self.check_agenda().await;

            // Latido
            sleep(Duration::from_secs(30)).await;
        }
    }

    async fn process_bus(&self) {
        let messages = MessageBus::read_for("CEREBRO");
        if messages.is_empty() { return; }

        println!("{}", format!("--- [BUS] Procesando {} mensajes ---", messages.len()).dimmed());

        for msg in messages {
            println!("📩 Recibido: {} de {}", msg.msg_type, msg.origin);
            
            match msg.msg_type.as_str() {
                "ALERTA" => {
                    println!("{}", format!("⚠️ ALERTA RECIBIDA: {}", msg.content).bold().red());
                    // Protocolo de emergencia
                },
                "ORDEN" => {
                    self.dispatch_order(&msg.content).await;
                },
                "HEARTBEAT" => {
                    // Actualizar estado del soldado en la memoria (futuro)
                },
                _ => {}
            }
            
            MessageBus::mark_read(&msg.id, "CEREBRO");
        }
    }

    async fn dispatch_order(&self, order: &str) {
        match order {
            "SYNC_GITHUB" => {
                let sync = crate::sync::VerixSync::new();
                let msg = format!("Cerebro-Rust Sync: {}", Utc::now().to_rfc3339());
                sync.instant_sync(&msg, "."); // El path root del Orbe
            },
            "PURGE_TEMP" => {
                let health = SystemHealth::collect();
                health.auto_purge();
            },
            _ => {
                println!("Desconocido: {}", order);
            }
        }
    }
}

use chrono::Utc;
