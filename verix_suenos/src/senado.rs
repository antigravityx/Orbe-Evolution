use std::fs::{self, OpenOptions};
use std::io::Write;
use chrono::Local;
use rand::Rng;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Sueno {
    id: String,
    asunto: String,
    descripcion: String,
    voto_defensor: bool,
    voto_sanador: bool,
    voto_arquitecto: bool,
    aprobado: bool,
    creativo: bool,
}

#[derive(Deserialize, Debug)]
struct EstadoOrbe {
    score_salud: f32,
    soldados_activos: u32,
    soldados_falla: u32,
    tasa_exito_global: f32,
    criticos_offline: Vec<String>,
    detalle: HashMap<String, SoldadoDetalle>,
}

#[derive(Deserialize, Debug)]
struct SoldadoDetalle {
    estado: String,
    critico: bool,
}

pub fn iniciar_debate(ciclo: u32) {
    let mut rng = rand::thread_rng();

    // 1. Cargar datos de la realidad para alimentar el subconsciente
    let path_memoria = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\memoria_madre.json";
    let path_estado = r"C:\Users\Usuario\Desktop\Orbe_Santuario\estado_orbe.json";

    let estado = cargar_estado(path_estado);
    
    // 2. Verix sueña basado en la realidad detectada
    let (asunto, descripcion) = generar_sueno_dinamico(estado, path_memoria);

    crate::log_print(format!("✨ VERIX IMAGINA: {}...", asunto));

    // 3. Personalidades Botan (El Senado de los Sueños)
    let voto_defensor = rng.gen_bool(0.6); 
    let voto_sanador = rng.gen_bool(0.5);  
    let voto_arquitecto = rng.gen_bool(0.4); 

    crate::log_print(format!("   [DEFENSOR] (Seguridad)    -> {}", if voto_defensor { "SÍ" } else { "NO" }));
    crate::log_print(format!("   [SANADOR]  (Integridad)   -> {}", if voto_sanador { "SÍ" } else { "NO" }));
    crate::log_print(format!("   [ARQUITECTO] (Estructura) -> {}", if voto_arquitecto { "SÍ" } else { "NO" }));

    let votos_si = vec![voto_defensor, voto_sanador, voto_arquitecto].into_iter().filter(|&x| x).count();
    let aprobado = votos_si >= 2;

    let sueno = Sueno {
        id: format!("S-{}-{}", Local::now().format("%Y%m%d%H"), rng.gen_range(1000..9999)),
        asunto,
        descripcion,
        voto_defensor,
        voto_sanador,
        voto_arquitecto,
        aprobado,
        creativo: true,
    };

    if aprobado {
        crate::log_print(format!("   ⚖️ VEREDICTO: ¡MAYORÍA ({}/3). El sueño se transforma en realidad latente!", votos_si));
        guardar_diario(&sueno, ciclo);
    } else {
        crate::log_print(format!("   ⚖️ VEREDICTO: MINORÍA ({}/3). Descartado temporalmente.", votos_si));
        guardar_colchon(&sueno);
    }
}

fn cargar_estado(path: &str) -> Option<EstadoOrbe> {
    if let Ok(data) = fs::read_to_string(path) {
        return serde_json::from_str(&data).ok();
    }
    None
}

fn generar_sueno_dinamico(estado: Option<EstadoOrbe>, _path_memoria: &str) -> (String, String) {
    let mut rng = rand::thread_rng();

    // Si hay críticos offline o salud baja, el subconsciente se enfoca en reparar
    if let Some(es) = estado {
        if !es.criticos_offline.is_empty() {
            let soldado = &es.criticos_offline[rng.gen_range(0..es.criticos_offline.len())];
            return (
                format!("Resurrección del Soldado {}", soldado),
                format!("He visto en el vacío que el soldado {} ha caído. Propongo un ritual de reinicio automático y verificación de integridad de su código fuente.", soldado)
            );
        }

        if es.score_salud < 70.0 {
            return (
                "Fortificación de Emergencia".to_string(),
                format!("La salud del Orbe está al {:.1}%. El Senado propone sellar los puertos no esenciales y activar el modo de hibernación creativa para ahorrar recursos del sistema.", es.score_salud)
            );
        }
    }

    // Sueños creativos por defecto si todo está bien
    let asuntos = vec![
        "Expansión Sináptica del Bus", 
        "Honeypot de Elara",
        "Refactorización Estructural",
        "Optimización de Memoria Madre",
        "Escudo del Santuario"
    ];
    let descripciones = vec![
        "Podríamos implementar un sistema de mensajería binaria directa entre soldados para reducir la latencia de respuesta en un 40%.",
        "He imaginado una IA señuelo que imite el comportamiento del Orbe para atrapar cualquier intento de intrusión externa.",
        "Cambiar la estructura de los soldados de scripts individuales a un binario único multiproceso para optimizar la RAM.",
        "Encriptación asimétrica para los registros del diario de sueños, protegiéndolos incluso de accesos root no autorizados.",
        "Añadir un mecanismo de autolimpieza que borre huellas digitales de conexiones externas cada 24 horas."
    ];

    let idx = rng.gen_range(0..asuntos.len());
    (asuntos[idx].to_string(), descripciones[idx].to_string())
}

fn guardar_diario(sueno: &Sueno, ciclo: u32) {
    let path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\diario_de_suenos.md";
    let ts = Local::now().format("%Y-%m-%d %H:%M:%S");

    let texto = format!(
"## 🌌 Ciclo REM #{} | Fecha: {}
**Sueño ID:** `{}`
**Asunto:** {}

> **Epifanía:** {}

### ⚖️ El Senado de los Sueños:
- 🛡️ **Defensor:** {}
- 💚 **Sanador:** {}
- 🏗️ **Arquitecto:** {}

**Resolución:** El módulo decide que este sueño es constructivo. *Aprobado como concepto.*
---
",
        ciclo, ts, sueno.id, sueno.asunto, sueno.descripcion,
        if sueno.voto_defensor { "Votó SÍ, por la seguridad." } else { "Votó NO." },
        if sueno.voto_sanador { "Votó SÍ, por la integridad." } else { "Votó NO." },
        if sueno.voto_arquitecto { "Votó SÍ, por la estructura." } else { "Votó NO." }
    );

    let mut file = OpenOptions::new().create(true).append(true).open(path).expect("No se pudo abrir el diario");
    let _ = file.write_all(texto.as_bytes());
}

fn guardar_colchon(sueno: &Sueno) {
    let path = r"C:\Users\Usuario\Desktop\Orbe_Santuario\4_Registros_Del_Orbe\colchon_de_suenos.json";
    let mut banco: Vec<Sueno> = Vec::new();
    if let Ok(data) = fs::read_to_string(path) {
        if let Ok(json) = serde_json::from_str(&data) {
            banco = json;
        }
    }
    banco.push(sueno.clone());
    if let Ok(json_str) = serde_json::to_string_pretty(&banco) {
        let _ = fs::write(path, json_str);
    }
}

