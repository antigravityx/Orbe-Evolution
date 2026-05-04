mod vault;
mod herald;
mod thread;
mod mounter;
mod reaper;
mod soul_api;

use vault::Vault;
use herald::Herald;
use thread::Thread;
use soul_api::{SoulApiState, start_soul_api};
use std::sync::Arc;
use tokio::sync::Mutex;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

/// =====================================================
/// VERIX SOUL OS - PROCESO INIT (PID 1) v0.2.0
/// 
/// ARQUITECTURA DE LA FASE 3:
///   - Vault     → Identidad criptográfica (D.I.N.)
///   - Thread    → Memoria persistente en disco + Git
///   - Herald    → IA local via Ollama HTTP
///   - Soul API  → API REST en :7777 para acceso multi-dispositivo
///
/// REGLA DE ORO: Este proceso NUNCA puede terminar.
/// Si main() retorna → Kernel Panic.
/// =====================================================
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Inicializar telemetría
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("Fallo al inicializar el logger");

    info!("=======================================================");
    info!("∞   VERIX SOUL OS v0.2.0 - FASE 3: PILARES ACTIVOS  ∞");
    info!("     D.I.N. | Memoria Persistente | IA Local | API     ");
    info!("=======================================================");

    // ===================================================
    // ETAPA 0: Preparación del entorno del kernel (PID 1)
    // ===================================================
    #[cfg(target_os = "linux")]
    {
        mounter::mount_essential_filesystems();
        reaper::configure_signal_handlers();
    }

    // ===================================================
    // ETAPA 1: Iniciar los tres pilares del Alma
    // ===================================================
    info!("--- Despertando los Pilares ---");

    let mut core_vault = Vault::new();
    let mut core_thread = Thread::new();
    let mut core_herald = Herald::new();

    core_vault.initialize().await?;
    core_thread.initialize().await?;
    core_herald.initialize().await?;

    let soul_id = core_vault.get_soul_id().to_string();

    // ===================================================
    // ETAPA 2: El Alma se presenta
    // ===================================================
    core_herald.greet_user(&soul_id).await;
    core_thread.record_conversation(&format!(
        "Sistema iniciado. Soul ID: {}. Pilares activos: Vault, Thread, Herald.",
        soul_id
    )).await;

    info!("-------------------------------------------------------");
    info!("Todos los pilares activos. Iniciando Soul API...");
    info!("-------------------------------------------------------");

    // ===================================================
    // ETAPA 3: Iniciar Soul API (en background)
    // ===================================================
    let api_state = Arc::new(Mutex::new(SoulApiState {
        soul_id: soul_id.clone(),
        uptime_ticks: 0,
        last_memory: "Sistema iniciado".to_string(),
        ia_active: core_herald.is_active,
    }));

    let api_state_clone = Arc::clone(&api_state);
    tokio::spawn(async move {
        start_soul_api(api_state_clone).await;
    });

    info!("Soul API lanzada en background en http://0.0.0.0:7777");

    // ===================================================
    // ETAPA 4: Bucle infinito del sistema operativo
    // ===================================================
    let mut tick: u64 = 0;
    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
        tick += 1;

        // Actualizar estado de la API
        {
            let mut state = api_state.lock().await;
            state.uptime_ticks = tick;
            state.last_memory = format!("Latido #{}", tick);
        }

        info!("♾️ Latido #{} | Memorias: {} | IA: {}",
            tick,
            core_thread.get_memory_count(),
            if core_herald.is_active { "activa" } else { "standby" }
        );

        // Guardar latido en memoria
        core_thread.record_memory(&format!("Latido #{}", tick)).await;

        // Cada 10 latidos (10 minutos), sincronizar con Git
        if tick % 10 == 0 {
            core_thread.sync_to_git(&soul_id).await;
        }
    }
}
