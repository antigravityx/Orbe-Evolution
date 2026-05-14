// ══════════════════════════════════════════════════
// 🔐 VERIX VAULT — Bóveda de Secretos
// ══════════════════════════════════════════════════
//
// Migrado desde: vault_soldier.py + soldado_encapsulador.py
// Misión: Cifrado y custodia de secretos del Orbe.
//
// NOTA: Usa XOR como placeholder. La evolución a AES-256
// se hará con la crate `aes-gcm` en la siguiente iteración.

use serde::{Deserialize, Serialize};
use std::fs;
use std::path::Path;

const VAULT_DIR: &str = r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\santuario_local\vault";

/// Representa un secreto almacenado
#[derive(Debug, Serialize, Deserialize)]
pub struct VaultEntry {
    pub name: String,
    pub encrypted_value: String,
    pub created_at: String,
    pub guardian: String,
}

/// Índice de la bóveda
#[derive(Debug, Serialize, Deserialize)]
pub struct VaultIndex {
    pub entries: Vec<VaultEntry>,
    pub total_secrets: usize,
    pub last_access: String,
}

/// Cifra datos usando XOR con la clave proporcionada.
/// Retorna los bytes cifrados como string hexadecimal.
pub fn encrypt(data: &str, key: &str) -> String {
    let key_bytes = key.as_bytes();
    let encrypted: Vec<u8> = data
        .as_bytes()
        .iter()
        .enumerate()
        .map(|(i, b)| b ^ key_bytes[i % key_bytes.len()])
        .collect();
    
    encrypted.iter().map(|b| format!("{:02x}", b)).collect()
}

/// Descifra datos previamente cifrados con XOR.
pub fn decrypt(hex_data: &str, key: &str) -> String {
    let key_bytes = key.as_bytes();
    let bytes: Vec<u8> = (0..hex_data.len())
        .step_by(2)
        .filter_map(|i| u8::from_str_radix(&hex_data[i..i + 2], 16).ok())
        .collect();
    
    let decrypted: Vec<u8> = bytes
        .iter()
        .enumerate()
        .map(|(i, b)| b ^ key_bytes[i % key_bytes.len()])
        .collect();
    
    String::from_utf8(decrypted).unwrap_or_default()
}

/// Almacena un secreto cifrado en la bóveda local.
pub fn store_secret(name: &str, value: &str, key: &str) -> Result<(), String> {
    // Ensure vault directory exists
    let vault_path = Path::new(VAULT_DIR);
    if !vault_path.exists() {
        fs::create_dir_all(vault_path).map_err(|e| format!("Error creando bóveda: {}", e))?;
    }

    let encrypted = encrypt(value, key);
    let entry = VaultEntry {
        name: name.to_string(),
        encrypted_value: encrypted,
        created_at: chrono::Local::now().to_rfc3339(),
        guardian: "r1ch0n".to_string(),
    };

    let file_path = vault_path.join(format!("{}.vault", name));
    let json = serde_json::to_string_pretty(&entry)
        .map_err(|e| format!("Error serializando: {}", e))?;
    
    fs::write(&file_path, json)
        .map_err(|e| format!("Error escribiendo: {}", e))?;
    
    Ok(())
}

/// Recupera un secreto de la bóveda local.
pub fn retrieve_secret(name: &str, key: &str) -> Result<String, String> {
    let file_path = Path::new(VAULT_DIR).join(format!("{}.vault", name));
    
    if !file_path.exists() {
        return Err(format!("Secreto '{}' no encontrado en la bóveda", name));
    }

    let data = fs::read_to_string(&file_path)
        .map_err(|e| format!("Error leyendo: {}", e))?;
    
    let entry: VaultEntry = serde_json::from_str(&data)
        .map_err(|e| format!("Error deserializando: {}", e))?;
    
    Ok(decrypt(&entry.encrypted_value, key))
}

/// Lista todos los secretos almacenados (sin revelar valores).
pub fn list_secrets() -> VaultIndex {
    let vault_path = Path::new(VAULT_DIR);
    let mut entries = Vec::new();

    if vault_path.exists() {
        if let Ok(dir) = fs::read_dir(vault_path) {
            for entry in dir.flatten() {
                if entry.path().extension().is_some_and(|ext| ext == "vault") {
                    if let Ok(data) = fs::read_to_string(entry.path()) {
                        if let Ok(vault_entry) = serde_json::from_str::<VaultEntry>(&data) {
                            entries.push(VaultEntry {
                                name: vault_entry.name,
                                encrypted_value: "[SELLADO]".to_string(),
                                created_at: vault_entry.created_at,
                                guardian: vault_entry.guardian,
                            });
                        }
                    }
                }
            }
        }
    }

    let total = entries.len();
    VaultIndex {
        entries,
        total_secrets: total,
        last_access: chrono::Local::now().to_rfc3339(),
    }
}
