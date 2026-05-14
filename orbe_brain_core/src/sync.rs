use crate::vault::VerixVault;
use reqwest::header::{HeaderMap, HeaderValue, AUTHORIZATION, ACCEPT, USER_AGENT};
use serde::{Serialize, Deserialize};
use std::process::Command;
use std::path::Path;
use colored::*;

#[derive(Serialize, Deserialize, Debug)]
pub struct GitHubRepo {
    pub name: String,
    pub private: bool,
    pub html_url: String,
}

pub struct VerixSync {
    token: String,
    user: String,
    client: reqwest::Client,
}

impl VerixSync {
    pub fn new() -> Self {
        let vault = VerixVault::new();
        let token = vault.get_secret("GITHUB_PAT_RICHON").unwrap_or_default();
        let user = vault.get_secret("GITHUB_USER").unwrap_or_else(|| "drxteren".to_string());

        let mut headers = HeaderMap::new();
        headers.insert(ACCEPT, HeaderValue::from_static("application/vnd.github+json"));
        headers.insert(USER_AGENT, HeaderValue::from_static("Verix-Rust-Sync/1.0"));
        
        if !token.is_empty() {
            let auth_val = format!("Bearer {}", token);
            headers.insert(AUTHORIZATION, HeaderValue::from_str(&auth_val).unwrap());
        }

        let client = reqwest::Client::builder()
            .default_headers(headers)
            .build()
            .unwrap();

        Self { token, user, client }
    }

    pub async fn check_identity(&self) -> Result<String, String> {
        let resp = self.client.get("https://api.github.com/user")
            .send().await
            .map_err(|e| e.to_string())?;

        if resp.status().is_success() {
            let json: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
            Ok(json["login"].as_str().unwrap_or("unknown").to_string())
        } else {
            Err(format!("HTTP {}", resp.status()))
        }
    }

    pub async fn list_repos(&self) -> Result<Vec<GitHubRepo>, String> {
        let resp = self.client.get("https://api.github.com/user/repos?per_page=100")
            .send().await
            .map_err(|e| e.to_string())?;

        if resp.status().is_success() {
            let repos: Vec<GitHubRepo> = resp.json().await.map_err(|e| e.to_string())?;
            Ok(repos)
        } else {
            Err(format!("HTTP {}", resp.status()))
        }
    }

    pub async fn create_repo(&self, name: &str, private: bool) -> Result<String, String> {
        let body = json!({
            "name": name,
            "private": private,
            "auto_init": true
        });

        let resp = self.client.post("https://api.github.com/user/repos")
            .json(&body)
            .send().await
            .map_err(|e| e.to_string())?;

        if resp.status().is_success() {
            let json: serde_json::Value = resp.json().await.map_err(|e| e.to_string())?;
            Ok(json["clone_url"].as_str().unwrap_or("").to_string())
        } else {
            Err(format!("HTTP {}", resp.status()))
        }
    }

    pub fn instant_sync(&self, message: &str, path: &str) -> bool {
        println!("{}", format!("🚀 [SYNC] Iniciando Push Instantáneo en {}", path).cyan());
        
        let git = |args: &[&str]| {
            Command::new("git")
                .args(args)
                .current_dir(path)
                .output()
        };

        // 1. Add all
        if git(&["add", "-A"]).is_err() { return false; }

        // 2. Commit
        let _ = git(&["commit", "-m", message]);

        // 3. Push with token injection
        // Usamos la técnica de inyectar el token en la URL de forma temporal para git push
        let remote_url = format!("https://{}:{}@github.com/{}/{}.git", 
            self.user, self.token, self.user, "Orbe-Evolution"); // Repo hardcoded o dinámico
        
        let push_res = Command::new("git")
            .args(&["push", &remote_url, "HEAD"])
            .current_dir(path)
            .output();

        match push_res {
            Ok(out) => {
                if out.status.success() {
                    println!("{}", "✅ Sync Instantánea Completada".green());
                    true
                } else {
                    let err = String::from_utf8_lossy(&out.stderr);
                    println!("{}", format!("❌ Error en Sync: {}", err).red());
                    false
                }
            },
            Err(_) => false,
        }
    }
}

use serde_json::json;
