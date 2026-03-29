use sysinfo::System;
use chrono::Local;
use std::thread;
use std::time::Duration;
use rand::Rng;
use std::fs::OpenOptions;
use std::io::Write;

mod senado;

fn main() {
    log_print("∴ [VERIX_SUENOS] Bóveda Subconsciente Iniciada...".to_string());
    log_print("∴ [VERIX_SUENOS] Monitoreando saturación térmica y ciclos de Memoria Madre.".to_string());
    
    let mut sys = System::new_all();
    let mut ciclo = 1;

    loop {
        sys.refresh_cpu_usage();
        thread::sleep(Duration::from_millis(1000));
        sys.refresh_cpu_usage();

        let mut uso_promedio = 0.0;
        let cpus = sys.cpus();
        if !cpus.is_empty() {
            uso_promedio = cpus.iter().map(|cpu| cpu.cpu_usage()).sum::<f32>() / cpus.len() as f32;
        }

        if uso_promedio > 70.0 {
            log_print(format!("CPU alta ({:.1}%). Postergando sueño.", uso_promedio));
            thread::sleep(Duration::from_secs(30));
            continue;
        }

        log_print(format!("--- INICIANDO CICLO REM #{} (CPU: {:.1}%) ---", ciclo, uso_promedio));

        // Envolver el debate en un pequeño delay simulado para "releer"
        thread::sleep(Duration::from_secs(2));
        senado::iniciar_debate(ciclo);

        ciclo += 1;
        
        let random_sleep = rand::thread_rng().gen_range(1..=3);
        log_print(format!("Fin del ciclo REM. Próximo sueño en {} minutos...\n", random_sleep));
        thread::sleep(Duration::from_secs(random_sleep * 60));
    }
}

pub fn log_print(msg: String) {
    let ts = Local::now().format("%Y-%m-%d %H:%M:%S");
    let log_line = format!("{} | {}", ts, msg);
    
    // Imprimir en consola para Antigravity
    println!("{}", log_line);

    // Persistir en archivo para independencia
    let log_path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\suenos.log";
    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open(log_path) {
        let _ = writeln!(file, "{}", log_line);
    }
}

