mod vault;
mod herald;
mod thread;
mod mounter;
mod reaper;
mod soul_api;
mod biometrics;

use vault::Vault;
use herald::Herald;
use thread::Thread;
use biometrics::{BiometricSensor, BiometricMode};
use soul_api::{SoulApiState, start_soul_api};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

/// =====================================================
/// VERIX SOUL OS - PROCESO INIT (PID 1) v0.3.0
///
/// ARQUITECTURA FASE 4 - TODOS LOS PILARES ACTIVOS:
///   - Vault        → Identidad D.I.N. con niveles de seguridad
///   - Thread       → Memoria persistente + Git sync
///   - Herald       → IA local via Ollama
///   - Soul API     → REST API en :7777
///   - Biometrics   → Sensores BLE + reconocimiento biométrico
///                    (simulado en VM, real en Raspberry Pi)
///
/// REGLA DE ORO: Este proceso NUNCA puede terminar.
/// =====================================================
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)?;

    info!("=======================================================");
    info!("∞   VERIX SOUL OS v0.3.0 - FASE 4: BIOSENSORES ∞");
    info!("    D.I.N. | Memoria | IA | API | Biometría           ");
    info!("=======================================================");

    // ===================================================
    // ETAPA 0: Kernel prep (solo PID 1 en Linux real)
    // ===================================================
    #[cfg(target_os = "linux")]
    {
        mounter::mount_essential_filesystems();
        reaper::configure_signal_handlers();
    }

    // ===================================================
    // ETAPA 1: Iniciar los cinco pilares en secuencia
    // ===================================================
    info!("--- Despertando los Cinco Pilares del Alma ---");

    let mut core_vault   = Vault::new();
    let mut core_thread  = Thread::new();
    let mut core_herald  = Herald::new();
    let mut core_bio     = BiometricSensor::new_simulated();

    core_vault.initialize().await?;
    core_thread.initialize().await?;
    core_herald.initialize().await?;

    let soul_id = core_vault.get_soul_id().to_string();

    // ===================================================
    // ETAPA 2: Calibración biométrica inicial (baseline)
    // Leer 15 muestras para establecer firma de referencia
    // ===================================================
    info!("--- Calibrando sensores biométricos (baseline)... ---");
    for i in 0..15 {
        let snap = core_bio.read_sample(&soul_id).await;
        if i == 7 {
            info!("  💓 HR referencia: {} BPM", snap.heart_rate_bpm.unwrap_or(0));
        }
        tokio::time::sleep(tokio::time::Duration::from_millis(200)).await;
    }
    core_bio.update_baseline(&soul_id);

    // Elevar Vault con la confianza biométrica inicial
    if let Some(baseline) = &core_bio.baseline_signature {
        core_vault.elevate_with_biometrics(baseline.confidence_score).await?;
    }

    // ===================================================
    // ETAPA 3: El Alma despierta
    // ===================================================
    core_herald.greet_user(&soul_id).await;
    core_thread.record_conversation(&format!(
        "Sistema v0.3.0 iniciado. Soul: {}. Nivel seguridad: {:?}. Biometría: activa.",
        soul_id,
        core_vault.get_unlock_level()
    )).await;

    // ===================================================
    // ETAPA 4: Soul API en background
    // ===================================================
    let api_state = Arc::new(Mutex::new(SoulApiState {
        soul_id: soul_id.clone(),
        uptime_ticks: 0,
        last_memory: "Sistema iniciado con biometría".to_string(),
        ia_active: core_herald.is_active,
    }));

    let api_state_clone = Arc::clone(&api_state);
    tokio::spawn(async move {
        start_soul_api(api_state_clone).await;
    });

    info!("=======================================================");
    info!("∞ Verix Soul OS v0.3.0 completamente operativo.");
    info!("  Soul ID   : {}", soul_id);
    info!("  Seguridad : {:?}", core_vault.get_unlock_level());
    info!("  API       : http://0.0.0.0:7777");
    info!("  Biometría : Modo simulación (→ BLE real con Raspberry Pi)");
    info!("=======================================================");

    // ===================================================
    // ETAPA 5: Bucle principal — Latido del Alma
    // ===================================================
    let mut tick: u64 = 0;

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(30)).await;
        tick += 1;

        // Leer muestra biométrica continua
        let snap = core_bio.read_sample(&soul_id).await;

        // Verificar portador cada 5 ticks (2.5 min)
        if tick % 5 == 0 {
            if let Some(result) = core_bio.verify_bearer(&soul_id, 70.0) {
                if result.recognized {
                    info!("✅ Portador verificado: {} ({:.1}%)", soul_id, result.confidence);
                } else {
                    info!("⚠️ Portador no reconocido. Confianza: {:.1}%", result.confidence);
                }
            }

            // Actualizar baseline con nuevas muestras
            core_bio.update_baseline(&soul_id);
        }

        // Actualizar estado de la API
        {
            let mut state = api_state.lock().await;
            state.uptime_ticks = tick;
            state.last_memory = format!(
                "Latido #{} | HR: {} BPM",
                tick,
                snap.heart_rate_bpm.unwrap_or(0)
            );
        }

        info!(
            "♾️ Latido #{} | HR: {} BPM | Memorias: {} | IA: {}",
            tick,
            snap.heart_rate_bpm.unwrap_or(0),
            core_thread.get_memory_count(),
            if core_herald.is_active { "activa" } else { "standby" }
        );

        core_thread.record_memory(&format!(
            "Latido #{} | HR:{} BPM",
            tick,
            snap.heart_rate_bpm.unwrap_or(0)
        )).await;

        // Sync Git cada 20 ticks (10 minutos)
        if tick % 20 == 0 {
            core_thread.sync_to_git(&soul_id).await;
        }
    }
}
