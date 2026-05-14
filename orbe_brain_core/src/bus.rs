use serde::{Serialize, Deserialize};
use std::fs::{self, File};
use std::io::{Read, Write};
use std::path::Path;
use chrono::{Utc, Duration};
use uuid::Uuid;

const BUS_PATH: &str = "c:/Users/Usuario/Desktop/Orbe_Santuario/4_Registros_Del_Orbe/bus_mensajes.json";
const EXPIRATION_HOURS: i64 = 48;

#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct VerixMessage {
    pub id: String,
    pub origin: String,
    pub destination: String,
    pub msg_type: String, // ALERTA, ORDEN, etc.
    pub content: String,
    pub timestamp: String,
    pub expires: String,
    pub read_by: Vec<String>,
}

pub struct MessageBus;

impl MessageBus {
    pub fn send(origin: &str, destination: &str, msg_type: &str, content: &str) -> String {
        let mut bus = Self::load();
        
        let id = Uuid::new_v4().to_string()[..12].to_string();
        let now = Utc::now();
        let expires = now + Duration::hours(EXPIRATION_HOURS);

        let msg = VerixMessage {
            id: id.clone(),
            origin: origin.to_string(),
            destination: destination.to_string(),
            msg_type: msg_type.to_string(),
            content: content.to_string(),
            timestamp: now.to_rfc3339(),
            expires: expires.to_rfc3339(),
            read_by: Vec::new(),
        };

        bus.push(msg);
        Self::save(&bus);
        id
    }

    pub fn read_for(soldier: &str) -> Vec<VerixMessage> {
        let bus = Self::load();
        let now = Utc::now();

        bus.into_iter()
            .filter(|m| {
                (m.destination == soldier || m.destination == "__BROADCAST__") &&
                !m.read_by.contains(&soldier.to_string()) &&
                Utc::parse_from_rfc3339(&m.expires).map(|t| t > now).unwrap_or(false)
            })
            .collect()
    }

    pub fn mark_read(id: &str, soldier: &str) {
        let mut bus = Self::load();
        for m in &mut bus {
            if m.id == id && !m.read_by.contains(&soldier.to_string()) {
                m.read_by.push(soldier.to_string());
            }
        }
        Self::save(&bus);
    }

    fn load() -> Vec<VerixMessage> {
        if !Path::new(BUS_PATH).exists() {
            return Vec::new();
        }

        let mut file = File::open(BUS_PATH).unwrap();
        let mut content = String::new();
        let _ = file.read_to_string(&mut content);
        
        serde_json::from_str(&content).unwrap_or_else(|_| Vec::new())
    }

    fn save(bus: &[VerixMessage]) {
        if let Some(parent) = Path::new(BUS_PATH).parent() {
            let _ = fs::create_dir_all(parent);
        }
        if let Ok(mut file) = File::create(BUS_PATH) {
            let json = serde_json::to_string_pretty(bus).unwrap();
            let _ = file.write_all(json.as_bytes());
        }
    }
}
