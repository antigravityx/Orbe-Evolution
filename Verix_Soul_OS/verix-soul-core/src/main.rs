mod vault;
mod herald;
mod thread;
mod mounter;
mod reaper;

use vault::Vault;
use herald::Herald;
use thread::Thread;
use tracing::{info, Level};
use tracing_subscriber::FmtSubscriber;

/// =====================================================
/// VERIX SOUL OS - PROCESO INIT (PID 1)
/// El primer y unico proceso del sistema operativo.
/// 
/// REGLA DE ORO: Este proceso NUNCA puede terminar.
/// Si main() retorna -> Kernel Panic.
/// =====================================================
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // Inicializar el sistema de telemetría y logs
    let subscriber = FmtSubscriber::builder()
        .with_max_level(Level::INFO)
        .finish();
    tracing::subscriber::set_global_default(subscriber)
        .expect("Fallo al inicializar el logger");

    info!("===============================================");
    info!("∞  VERIX SOUL OS: PROCESO INIT INICIADO  ∞");
    info!("   D.I.N. - Documento de Identidad Neuronal  ");
    info!("===============================================");

    // ===================================================
    // ETAPA 0: Preparacion del entorno del kernel
    // (Solo necesario cuando corremos como PID 1 real)
    // ===================================================
    #[cfg(target_os = "linux")]
    {
        // Paso 1: Montar /proc, /sys, /dev antes de cualquier cosa
        mounter::mount_essential_filesystems();

        // Paso 2: Configurar handler de señales para procesos zombie
        reaper::configure_signal_handlers();
    }

    // ===================================================
    // ETAPA 1: Iniciar los tres pilares del Alma
    // ===================================================
    info!("--- Iniciando los Pilares del Alma ---");

    let mut core_vault = Vault::new();
    let mut core_thread = Thread::new();
    let mut core_herald = Herald::new();

    // Secuencia de inicialización (orden: Vault -> Thread -> Herald)
    core_vault.initialize().await?;
    core_thread.initialize().await?;
    core_herald.initialize().await?;

    // ===================================================
    // ETAPA 2: El Alma despierta y se presenta
    // ===================================================
    let soul_id = core_vault.get_soul_id();
    core_herald.greet_user(soul_id).await;
    core_thread.record_memory(&format!("Sistema iniciado por {}", soul_id)).await;

    info!("-----------------------------------------------");
    info!("Sistema Verix Soul OS completamente operativo.");
    info!("El Alma escucha. El hilo de la eternidad corre.");
    info!("-----------------------------------------------");

    // ===================================================
    // ETAPA 3: Bucle infinito del sistema operativo
    // Un init NUNCA puede terminar. Latido cada 60s.
    // ===================================================
    let mut tick: u64 = 0;
    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(60)).await;
        tick += 1;
        info!("♾️ Latido #{} del sistema. Alma activa.", tick);
        core_thread.record_memory(&format!("Latido #{}", tick)).await;
    }
}
