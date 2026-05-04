use serde::{Deserialize, Serialize};
use std::time::Duration;
use tracing::{info, warn, debug};

// ─────────────────────────────────────────────────────────────────
// UUIDs estándar GATT para sensores biométricos
// Fuente: Bluetooth SIG - Assigned Numbers
// ─────────────────────────────────────────────────────────────────
pub mod gatt_uuids {
    // Servicios
    pub const HEART_RATE_SERVICE: &str        = "0000180d-0000-1000-8000-00805f9b34fb";
    pub const BATTERY_SERVICE: &str           = "0000180f-0000-1000-8000-00805f9b34fb";
    pub const HEALTH_THERMOMETER: &str        = "00001809-0000-1000-8000-00805f9b34fb";
    pub const GENERIC_ACCESS: &str            = "00001800-0000-1000-8000-00805f9b34fb";

    // Características (Characteristics)
    pub const HEART_RATE_MEASUREMENT: &str    = "00002a37-0000-1000-8000-00805f9b34fb";
    pub const BODY_SENSOR_LOCATION: &str      = "00002a38-0000-1000-8000-00805f9b34fb";
    pub const BATTERY_LEVEL: &str             = "00002a19-0000-1000-8000-00805f9b34fb";
    pub const TEMPERATURE_MEASUREMENT: &str   = "00002a1c-0000-1000-8000-00805f9b34fb";
    pub const DEVICE_NAME: &str               = "00002a00-0000-1000-8000-00805f9b34fb";
}

/// Datos biométricos leídos del wearable en un instante
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiometricSnapshot {
    pub timestamp: String,
    pub heart_rate_bpm: Option<u8>,
    pub battery_percent: Option<u8>,
    pub body_temperature_celsius: Option<f32>,
    pub device_name: String,
    pub device_address: String,
    pub signal_strength_rssi: Option<i16>,
}

/// Firma biométrica calculada a partir de múltiples muestras
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BiometricSignature {
    pub soul_id: String,
    pub avg_heart_rate: f32,
    pub heart_rate_variance: f32,
    pub avg_temperature: Option<f32>,
    pub sample_count: u32,
    pub confidence_score: f32,
}

// ─────────────────────────────────────────────────────────────────
// MODO SIMULACIÓN (cuando no hay hardware físico)
// ─────────────────────────────────────────────────────────────────

/// Genera datos biométricos simulados para desarrollo y testing en VM
pub fn simulate_biometric_snapshot(soul_id: &str) -> BiometricSnapshot {
    use std::time::SystemTime;

    // Simular variación natural del ritmo cardíaco (60-90 BPM)
    let base_hr: u8 = 72;
    let variation = (SystemTime::now()
        .duration_since(SystemTime::UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs() % 20) as i8 - 10;
    let heart_rate = (base_hr as i8 + variation).clamp(50, 120) as u8;

    BiometricSnapshot {
        timestamp: chrono::Utc::now().to_rfc3339(),
        heart_rate_bpm: Some(heart_rate),
        battery_percent: Some(87),
        body_temperature_celsius: Some(36.6),
        device_name: format!("VerixSim-{}", &soul_id[..8.min(soul_id.len())]),
        device_address: "00:00:00:00:00:SIM".to_string(),
        signal_strength_rssi: Some(-65),
    }
}

/// Calcula la firma biométrica a partir de múltiples snapshots
pub fn calculate_biometric_signature(
    soul_id: &str,
    snapshots: &[BiometricSnapshot],
) -> BiometricSignature {
    if snapshots.is_empty() {
        return BiometricSignature {
            soul_id: soul_id.to_string(),
            avg_heart_rate: 0.0,
            heart_rate_variance: 0.0,
            avg_temperature: None,
            sample_count: 0,
            confidence_score: 0.0,
        };
    }

    let heart_rates: Vec<f32> = snapshots
        .iter()
        .filter_map(|s| s.heart_rate_bpm.map(|hr| hr as f32))
        .collect();

    let avg_hr = if !heart_rates.is_empty() {
        heart_rates.iter().sum::<f32>() / heart_rates.len() as f32
    } else {
        0.0
    };

    // Calcular varianza (HRV - Heart Rate Variability)
    let variance = if heart_rates.len() > 1 {
        let mean = avg_hr;
        heart_rates.iter()
            .map(|hr| (hr - mean).powi(2))
            .sum::<f32>() / (heart_rates.len() - 1) as f32
    } else {
        0.0
    };

    let temps: Vec<f32> = snapshots
        .iter()
        .filter_map(|s| s.body_temperature_celsius)
        .collect();
    let avg_temp = if !temps.is_empty() {
        Some(temps.iter().sum::<f32>() / temps.len() as f32)
    } else {
        None
    };

    // Score de confianza basado en número de muestras
    let confidence = (snapshots.len() as f32 / 30.0).min(1.0) * 100.0;

    BiometricSignature {
        soul_id: soul_id.to_string(),
        avg_heart_rate: avg_hr,
        heart_rate_variance: variance,
        avg_temperature: avg_temp,
        sample_count: snapshots.len() as u32,
        confidence_score: confidence,
    }
}

// ─────────────────────────────────────────────────────────────────
// ALGORITMO DE RECONOCIMIENTO BIOMÉTRICO
// Implementación del algoritmo del Verix Soul whitepaper
// ─────────────────────────────────────────────────────────────────

/// Compara dos firmas biométricas y decide si pertenecen al mismo portador
pub fn recognize_soul(
    current: &BiometricSignature,
    historical: &BiometricSignature,
    threshold: f32,
) -> SoulRecognitionResult {
    if current.sample_count < 5 {
        return SoulRecognitionResult {
            recognized: false,
            confidence: 0.0,
            reason: "Insuficientes muestras para reconocimiento confiable".to_string(),
        };
    }

    // Score 1: Similitud de ritmo cardíaco promedio
    let hr_diff = (current.avg_heart_rate - historical.avg_heart_rate).abs();
    let hr_score = 1.0 - (hr_diff / 30.0).min(1.0); // 30 BPM de margen

    // Score 2: Similitud de HRV (variabilidad)
    let hrv_diff = (current.heart_rate_variance - historical.heart_rate_variance).abs();
    let hrv_score = 1.0 - (hrv_diff / 50.0).min(1.0);

    // Score 3: Temperatura (si disponible)
    let temp_score = match (current.avg_temperature, historical.avg_temperature) {
        (Some(ct), Some(ht)) => {
            let diff = (ct - ht).abs();
            1.0 - (diff / 2.0).min(1.0) // 2°C de margen
        }
        _ => 0.5, // Sin datos de temperatura: neutral
    };

    // Ponderación: HR 50%, HRV 30%, Temperatura 20%
    let combined_score = (hr_score * 0.50) + (hrv_score * 0.30) + (temp_score * 0.20);
    let final_confidence = combined_score * 100.0;

    SoulRecognitionResult {
        recognized: final_confidence >= threshold,
        confidence: final_confidence,
        reason: format!(
            "HR:{:.0}% HRV:{:.0}% Temp:{:.0}% → {:.1}%",
            hr_score * 100.0,
            hrv_score * 100.0,
            temp_score * 100.0,
            final_confidence
        ),
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct SoulRecognitionResult {
    pub recognized: bool,
    pub confidence: f32,
    pub reason: String,
}

// ─────────────────────────────────────────────────────────────────
// GESTOR DE HARDWARE BIOMÉTRICO
// Hardware Abstraction Layer (HAL)
// ─────────────────────────────────────────────────────────────────

pub enum BiometricMode {
    Simulation,
    #[cfg(target_os = "linux")]
    BluetoothLE { device_address: String },
}

pub struct BiometricSensor {
    pub mode: BiometricMode,
    pub snapshots: Vec<BiometricSnapshot>,
    pub baseline_signature: Option<BiometricSignature>,
}

impl BiometricSensor {
    pub fn new_simulated() -> Self {
        info!("🧬 Sensor biométrico iniciado en modo SIMULACIÓN.");
        info!("  → Para hardware real: conecta tu wearable BLE y reinicia.");
        Self {
            mode: BiometricMode::Simulation,
            snapshots: Vec::new(),
            baseline_signature: None,
        }
    }

    /// Lee una muestra biométrica (simulada o real)
    pub async fn read_sample(&mut self, soul_id: &str) -> BiometricSnapshot {
        let snapshot = match &self.mode {
            BiometricMode::Simulation => {
                let snap = simulate_biometric_snapshot(soul_id);
                debug!("  💓 HR simulado: {} BPM", snap.heart_rate_bpm.unwrap_or(0));
                snap
            }
            #[cfg(target_os = "linux")]
            BiometricMode::BluetoothLE { device_address } => {
                // TODO Fase 4b: Implementar lectura BLE real con btleplug
                warn!("  BLE hardware: dirección {} - en construcción", device_address);
                simulate_biometric_snapshot(soul_id)
            }
        };

        self.snapshots.push(snapshot.clone());

        // Mantener solo las últimas 60 muestras (rolling window)
        if self.snapshots.len() > 60 {
            self.snapshots.remove(0);
        }

        snapshot
    }

    /// Construye o actualiza la firma de referencia del alma
    pub fn update_baseline(&mut self, soul_id: &str) {
        if self.snapshots.len() >= 10 {
            let sig = calculate_biometric_signature(soul_id, &self.snapshots);
            info!(
                "🧬 Firma biométrica actualizada: HR={:.0} BPM (±{:.1}), confianza={:.0}%",
                sig.avg_heart_rate, sig.heart_rate_variance, sig.confidence_score
            );
            self.baseline_signature = Some(sig);
        }
    }

    /// Verifica si el portador actual coincide con el alma registrada
    pub fn verify_bearer(&self, soul_id: &str, threshold: f32) -> Option<SoulRecognitionResult> {
        let baseline = self.baseline_signature.as_ref()?;
        let current = calculate_biometric_signature(soul_id, &self.snapshots);
        let result = recognize_soul(&current, baseline, threshold);
        info!(
            "🔍 Verificación biométrica: {} ({:.1}%) — {}",
            if result.recognized { "RECONOCIDO ✓" } else { "NO RECONOCIDO ✗" },
            result.confidence,
            result.reason
        );
        Some(result)
    }
}
