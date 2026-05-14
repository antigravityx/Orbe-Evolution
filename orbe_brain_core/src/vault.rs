use aes_gcm::{Aes256Gcm, Key, Nonce, KeyInit};
use aes_gcm::aead::{Aead, OsRng};
use hmac::{Hmac, Mac};
use sha2::Sha256;
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::Path;
use serde::{Serialize, Deserialize};
use std::collections::HashMap;
use chrono::Utc;

type HmacSha256 = Hmac<Sha256>;

const SALT_FIJO: &[u8] = b"ORB3_V3RIX_R1CH0N_ALMA_2026";
const VAULT_PATH: &str = "c:/Users/Usuario/Desktop/Orbe_Santuario/3_Llaves_Maestras/vault_orbital_rs.db";

#[derive(Serialize, Deserialize, Debug)]
pub struct VaultEntry {
    pub value: String,
    pub category: String,
    pub sealed_at: String,
    pub checksum: String,
}

pub struct VerixVault {
    key: [u8; 32],
}

impl VerixVault {
    pub fn new() -> Self {
        let hostname = whoami::hostname();
        let username = whoami::username();
        let identity = format!("{}::{}", hostname, username);

        let mut mac = HmacSha256::new_from_slice(SALT_FIJO).expect("HMAC can take key of any size");
        mac.update(identity.as_bytes());
        let result = mac.finalize();
        let key_bytes = result.into_bytes();

        let mut key = [0u8; 32];
        key.copy_from_slice(&key_bytes);

        Self { key }
    }

    fn encrypt(&self, data: &str) -> Vec<u8> {
        let key = Key::<Aes256Gcm>::from_slice(&self.key);
        let cipher = Aes256Gcm::new(key);
        let nonce = Aes256Gcm::generate_nonce(&mut OsRng); // 96-bits; unique per message
        
        let ciphertext = cipher.encrypt(&nonce, data.as_bytes().as_ref())
            .expect("encryption failure!");
        
        let mut combined = nonce.to_vec();
        combined.extend_from_slice(&ciphertext);
        combined
    }

    fn decrypt(&self, blob: &[u8]) -> Option<String> {
        if blob.len() < 12 { return None; }
        
        let key = Key::<Aes256Gcm>::from_slice(&self.key);
        let cipher = Aes256Gcm::new(key);
        let (nonce_bytes, ciphertext) = blob.split_at(12);
        let nonce = Nonce::from_slice(nonce_bytes);

        match cipher.decrypt(nonce, ciphertext.as_ref()) {
            Ok(plaintext) => String::from_utf8(plaintext).ok(),
            Err(_) => None,
        }
    }

    pub fn save_secret(&self, name: &str, value: &str, category: &str) -> bool {
        let mut vault = self.load_vault();
        
        let entry = VaultEntry {
            value: value.to_string(),
            category: category.to_string(),
            sealed_at: Utc::now().to_rfc3339(),
            checksum: format!("{:x}", Sha256::digest(value.as_bytes()))[..12].to_string(),
        };

        vault.insert(name.to_string(), entry);
        self.save_vault(vault)
    }

    pub fn get_secret(&self, name: &str) -> Option<String> {
        let vault = self.load_vault();
        vault.get(name).map(|e| e.value.clone())
    }

    fn load_vault(&self) -> HashMap<String, VaultEntry> {
        if !Path::new(VAULT_PATH).exists() {
            return HashMap::new();
        }

        let mut file = File::open(VAULT_PATH).expect("Unable to open vault");
        let mut buffer = Vec::new();
        file.read_to_end(&mut buffer).expect("Unable to read vault");

        if let Some(decrypted_json) = self.decrypt(&buffer) {
            serde_json::from_str(&decrypted_json).unwrap_or_else(|_| HashMap::new())
        } else {
            HashMap::new()
        }
    }

    fn save_vault(&self, vault: HashMap<String, VaultEntry>) -> bool {
        if let Ok(json) = serde_json::to_string(&vault) {
            let encrypted_blob = self.encrypt(&json);
            if let Some(parent) = Path::new(VAULT_PATH).parent() {
                let _ = fs::create_dir_all(parent);
            }
            if let Ok(mut file) = File::create(VAULT_PATH) {
                return file.write_all(&encrypted_blob).is_ok();
            }
        }
        false
    }
}
