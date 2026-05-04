use serde::{Deserialize, Serialize};
use tracing::{info, warn};
use std::path::PathBuf;
use chrono::Utc;

/// Registro de memoria del Alma
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MemoryEntry {
    pub timestamp: String,
    pub content: String,
    pub entry_type: MemoryType,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub enum MemoryType {
    SystemEvent,
    Conversation,
    Heartbeat,
    Discovery,
}

/// The Thread: Memoria Contextual con persistencia en disco y sincronización Git
pub struct Thread {
    pub is_syncing: bool,
    soul_data_path: PathBuf,
    memory_log: Vec<MemoryEntry>,
}

impl Thread {
    pub fn new() -> Self {
        // Ruta de la cápsula del alma (en Linux: /soul, en dev: ./soul_data)
        let soul_path = if cfg!(target_os = "linux") {
            PathBuf::from("/soul")
        } else {
            PathBuf::from("./soul_data")
        };

        Self {
            is_syncing: false,
            soul_data_path: soul_path,
            memory_log: Vec::new(),
        }
    }

    pub async fn initialize(&mut self) -> anyhow::Result<()> {
        info!("🕸️ Iniciando The Thread (Memoria Contextual + Persistencia)...");

        // Crear el directorio de la cápsula del alma si no existe
        tokio::fs::create_dir_all(&self.soul_data_path).await?;
        let memories_path = self.soul_data_path.join("memories.json");
        tokio::fs::create_dir_all(self.soul_data_path.join("conversations")).await?;

        // Cargar memorias previas si existen
        if memories_path.exists() {
            match tokio::fs::read_to_string(&memories_path).await {
                Ok(content) => {
                    if let Ok(entries) = serde_json::from_str::<Vec<MemoryEntry>>(&content) {
                        let count = entries.len();
                        self.memory_log = entries;
                        info!("  ✓ {} memorias cargadas del alma.", count);
                    }
                }
                Err(e) => warn!("  No se pudieron cargar memorias previas: {}", e),
            }
        } else {
            info!("  → Primera vez: creando nueva cápsula del alma.");
        }

        info!("  📂 Cápsula del alma en: {:?}", self.soul_data_path);
        info!("📡 The Thread listo. Memoria inmutable activa.");
        self.is_syncing = true;
        Ok(())
    }

    /// Guarda una nueva memoria en el registro del alma
    pub async fn record_memory(&mut self, content: &str) {
        self.record_typed_memory(content, MemoryType::SystemEvent).await;
    }

    pub async fn record_conversation(&mut self, content: &str) {
        self.record_typed_memory(content, MemoryType::Conversation).await;
    }

    async fn record_typed_memory(&mut self, content: &str, entry_type: MemoryType) {
        let entry = MemoryEntry {
            timestamp: Utc::now().to_rfc3339(),
            content: content.to_string(),
            entry_type,
        };

        info!("💾 [THREAD] Memoria sellada: '{}'", content);
        self.memory_log.push(entry);

        // Persistir en disco inmediatamente
        if let Err(e) = self.flush_to_disk().await {
            warn!("  Fallo al persistir memoria: {}", e);
        }
    }

    /// Escribe todas las memorias al disco
    async fn flush_to_disk(&self) -> anyhow::Result<()> {
        let path = self.soul_data_path.join("memories.json");
        let json = serde_json::to_string_pretty(&self.memory_log)?;
        tokio::fs::write(&path, json).await?;
        Ok(())
    }

    /// Sincroniza la cápsula del alma con el repositorio Git remoto
    pub async fn sync_to_git(&self, soul_id: &str) {
        info!("🔄 [THREAD] Sincronizando alma con repositorio remoto...");

        // Usar git CLI para máxima compatibilidad en el OS mínimo
        let timestamp = Utc::now().format("%Y-%m-%d %H:%M:%S UTC");
        let commit_msg = format!("Latido del Alma - {} - {}", soul_id, timestamp);

        let git_dir = self.soul_data_path.clone();

        tokio::spawn(async move {
            // Inicializar repo si no existe
            let _ = tokio::process::Command::new("git")
                .args(["init"])
                .current_dir(&git_dir)
                .output()
                .await;

            // Stage all changes
            let add_result = tokio::process::Command::new("git")
                .args(["add", "."])
                .current_dir(&git_dir)
                .output()
                .await;

            // Commit
            if add_result.is_ok() {
                let commit_result = tokio::process::Command::new("git")
                    .args(["commit", "-m", &commit_msg, "--allow-empty"])
                    .current_dir(&git_dir)
                    .output()
                    .await;

                match commit_result {
                    Ok(out) if out.status.success() => {
                        info!("  ✓ Memoria sellada en Git: {}", commit_msg);
                    }
                    _ => {
                        warn!("  Git commit: nada nuevo que sincronizar.");
                    }
                }
            }
        });
    }

    pub fn get_memory_count(&self) -> usize {
        self.memory_log.len()
    }
}
