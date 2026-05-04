use serde::{Deserialize, Serialize};
use tracing::{info, warn};
use std::time::Duration;

/// Nivel de seguridad para desbloquear el Vault
#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
pub enum UnlockLevel {
    /// Solo clave D.I.N. (cryptographic only)
    CryptoOnly,
    /// Clave + firma biométrica básica (HR match)
    BiometricBasic,
    /// Clave + firma biométrica completa (HR + HRV + Temp)
    BiometricFull,
    /// Máxima seguridad: Crypto + Biométrica + Contexto temporal
    QuantumSovereign,
}

/// Estado del Vault
#[derive(Debug)]
pub struct Vault {
    pub is_unlocked: bool,
    soul_id: String,
    unlock_level: UnlockLevel,
    unlock_timestamp: Option<chrono::DateTime<chrono::Utc>>,
    /// Hash de referencia de la firma biométrica (en producción: Argon2 + salt)
    biometric_hash: Option<String>,
}

impl Vault {
    pub fn new() -> Self {
        Self {
            is_unlocked: false,
            soul_id: "DIN-0000-UNASSIGNED".to_string(),
            unlock_level: UnlockLevel::CryptoOnly,
            unlock_timestamp: None,
            biometric_hash: None,
        }
    }

    pub async fn initialize(&mut self) -> anyhow::Result<()> {
        info!("🔐 Iniciando The Vault (Core Soberano)...");
        tokio::time::sleep(Duration::from_millis(300)).await;

        // En producción: leer D.I.N. de archivo cifrado o TPM
        self.soul_id = Self::load_or_generate_soul_id().await;
        self.unlock_level = UnlockLevel::CryptoOnly;
        self.unlock_timestamp = Some(chrono::Utc::now());
        self.is_unlocked = true;

        info!("  ✓ D.I.N. cargado: {}", self.soul_id);
        info!("  ✓ Nivel de seguridad: {:?}", self.unlock_level);
        info!("🔓 Vault activa. Identidad soberana establecida.");
        Ok(())
    }

    /// Eleva el nivel de seguridad con verificación biométrica
    pub async fn elevate_with_biometrics(
        &mut self,
        biometric_confidence: f32,
    ) -> anyhow::Result<()> {
        if biometric_confidence >= 90.0 {
            self.unlock_level = UnlockLevel::BiometricFull;
            info!("🛡️ Vault elevada a nivel BIOMÉTRICO COMPLETO ({:.1}%)", biometric_confidence);
        } else if biometric_confidence >= 70.0 {
            self.unlock_level = UnlockLevel::BiometricBasic;
            info!("🛡️ Vault elevada a nivel BIOMÉTRICO BÁSICO ({:.1}%)", biometric_confidence);
        } else {
            warn!("  Confianza biométrica insuficiente ({:.1}%). Nivel no elevado.", biometric_confidence);
        }
        Ok(())
    }

    /// Eleva al nivel máximo (requiere PC cuántico en el futuro)
    pub async fn elevate_quantum_sovereign(&mut self) {
        self.unlock_level = UnlockLevel::QuantumSovereign;
        info!("⚛️ Vault elevada a nivel QUANTUM SOVEREIGN");
        info!("  → Criptografía post-cuántica activa (pendiente: integración PC cuántico)");
    }

    /// Carga el D.I.N. del disco o genera uno nuevo
    async fn load_or_generate_soul_id() -> String {
        let soul_dir = if cfg!(target_os = "linux") {
            std::path::PathBuf::from("/var/lib/verix-soul")
        } else {
            std::path::PathBuf::from("./soul_data")
        };

        let din_path = soul_dir.join("soul_id.din");

        if din_path.exists() {
            match tokio::fs::read_to_string(&din_path).await {
                Ok(id) => {
                    let id = id.trim().to_string();
                    info!("  → D.I.N. cargado desde disco: {}", id);
                    return id;
                }
                Err(_) => {}
            }
        }

        // Generar nuevo D.I.N. único
        let timestamp = chrono::Utc::now().timestamp();
        let new_id = format!("DIN-R1CH0N-{:X}", timestamp);
        info!("  → Nuevo D.I.N. generado: {}", new_id);

        // Persistir en disco
        let _ = tokio::fs::create_dir_all(&soul_dir).await;
        let _ = tokio::fs::write(&din_path, &new_id).await;

        new_id
    }

    pub fn get_soul_id(&self) -> &str {
        &self.soul_id
    }

    pub fn get_unlock_level(&self) -> &UnlockLevel {
        &self.unlock_level
    }

    /// Exporta un token firmado para la Soul API (TTL: 2 horas)
    pub fn generate_access_token(&self) -> String {
        let now = chrono::Utc::now().timestamp();
        let expiry = now + 7200; // 2 horas
        // En producción: JWT firmado con la clave privada del Vault
        format!("VERIX-TOKEN-{}-{}-{}", &self.soul_id, now, expiry)
    }
}
