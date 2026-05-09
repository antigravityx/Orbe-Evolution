use sha2::{Sha256, Digest};
use chrono::Utc;
use serde::{Serialize, Deserialize};

#[derive(Serialize, Deserialize, Debug)]
pub struct MemoryAnchor {
    pub timestamp: String,
    pub event: String,
    pub level: String, // "INFO", "SUCCESS", "ERROR"
    pub hash: String,
}

impl MemoryAnchor {
    pub fn new(event: &str, level: &str) -> Self {
        let timestamp = Utc::now().to_rfc3339();
        let payload = format!("{}{}{}", timestamp, event, level);
        
        let mut hasher = Sha256::new();
        hasher.update(payload);
        let hash = format!("{:x}", hasher.finalize());

        Self {
            timestamp,
            event: event.to_string(),
            level: level.to_string(),
            hash,
        }
    }

    pub fn seal(&self) {
        println!("🔒 Anclaje Sellado: [{}] {} -> Hash: {}", 
            self.level, self.event, &self.hash[0..8]
        );
    }
}
