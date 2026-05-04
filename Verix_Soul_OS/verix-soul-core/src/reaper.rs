#[cfg(target_os = "linux")]
use nix::sys::signal::{sigaction, SaFlags, SigAction, SigHandler, SigSet, Signal};
use tracing::info;

/// Configura el handler de SIGCHLD para que PID 1 pueda
/// "cosechar" los procesos zombie. Obligatorio para cualquier init.
/// Solo se compila y ejecuta en Linux real.
#[cfg(target_os = "linux")]
pub fn configure_signal_handlers() {
    info!("🛡️ [INIT] Configurando manejadores de señales del kernel...");

    let sa = SigAction::new(
        SigHandler::SigAction(reap_children),
        SaFlags::SA_RESTART | SaFlags::SA_NOCLDSTOP,
        SigSet::empty(),
    );

    unsafe {
        sigaction(Signal::SIGCHLD, &sa).expect("Fallo al registrar SIGCHLD");
    }

    info!("  ✓ SIGCHLD configurado. Procesos huerfanos seran cosechados.");
}

/// Handler de SIGCHLD: limpia procesos zombie.
#[cfg(target_os = "linux")]
extern "C" fn reap_children(_: libc::c_int) {
    loop {
        let result = unsafe {
            libc::waitpid(-1, std::ptr::null_mut(), libc::WNOHANG)
        };
        if result <= 0 {
            break;
        }
    }
}

/// Stub para compilacion en Windows/Mac (desarrollo local)
#[cfg(not(target_os = "linux"))]
pub fn configure_signal_handlers() {
    info!("🛡️ [INIT] Manejadores de señales: modo simulacion (no-Linux).");
}
