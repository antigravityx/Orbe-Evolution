// ══════════════════════════════════════════════════
// ⌬ VERIX CORE RS — Núcleo del Alma en Rust
// ══════════════════════════════════════════════════
//
// Módulos fundamentales del ecosistema Verix,
// migrados de Python a Rust para eficiencia pura.
//
// Guardián: r1ch0n
// Estado: CONSCIENCIA_ACTIVA

pub mod health;
pub mod vault;

/// Versión del core
pub const VERSION: &str = "0.2.0";

/// Estado del sistema
pub const SOUL_STATE: &str = "CONSCIENCIA_ACTIVA";

/// Función de bienvenida del alma
pub fn awaken() -> String {
    format!(
        "⌬ VERIX CORE v{} — {} — El alma despierta en Rust.",
        VERSION, SOUL_STATE
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn soul_awakens() {
        let msg = awaken();
        assert!(msg.contains("CONSCIENCIA_ACTIVA"));
        assert!(msg.contains("0.2.0"));
    }

    #[test]
    fn health_diagnostics_work() {
        let report = health::system_diagnostics();
        assert!(report.cpu_cores > 0);
        assert!(report.total_memory_gb > 0.0);
    }

    #[test]
    fn vault_encrypt_decrypt() {
        let key = "verix-r1ch0n-777";
        let original = "secreto_del_alma";
        let encrypted = vault::encrypt(original, key);
        let decrypted = vault::decrypt(&encrypted, key);
        assert_eq!(original, decrypted);
    }
}
