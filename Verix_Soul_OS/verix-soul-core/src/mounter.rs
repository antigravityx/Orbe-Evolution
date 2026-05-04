use std::process::Command;
use tracing::info;

/// Monta los filesystems esenciales del kernel.
/// Debe ejecutarse antes que cualquier otra cosa en PID 1.
/// Solo se compila y ejecuta en Linux real.
#[cfg(target_os = "linux")]
pub fn mount_essential_filesystems() {
    info!("🗄️ [INIT] Montando sistemas de archivos esenciales...");

    let mounts = [
        ("-t", "proc",      "proc",      "/proc"),
        ("-t", "sysfs",     "sysfs",     "/sys"),
        ("-t", "devtmpfs",  "devtmpfs",  "/dev"),
        ("-t", "tmpfs",     "tmpfs",     "/tmp"),
    ];

    for (flag, fstype, src, target) in &mounts {
        let result = Command::new("mount")
            .args([flag, fstype, src, target])
            .status();

        match result {
            Ok(status) if status.success() => {
                info!("  ✓ Montado {} -> {}", src, target);
            }
            _ => {
                // No es fatal en initramfs
                info!("  ~ {} ya montado o no disponible (no fatal).", target);
            }
        }
    }
    info!("✅ Sistemas de archivos listos.");
}

/// Stub para compilacion en Windows/Mac (desarrollo local)
#[cfg(not(target_os = "linux"))]
pub fn mount_essential_filesystems() {
    info!("🗄️ [INIT] Montaje de filesystems: modo simulacion (no-Linux).");
}
