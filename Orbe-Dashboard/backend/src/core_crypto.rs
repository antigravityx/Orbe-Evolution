use std::fs::File;
use std::io::{Read, Write};
use std::path::Path;
use zip::write::SimpleFileOptions;
use walkdir::WalkDir;
use aes::Aes256;
use cfb_mode::Encryptor;
use cfb_mode::Decryptor;
use cfb_mode::cipher::{AsyncStreamCipher, KeyIvInit};
use sha2::{Sha256, Digest};
use rand::RngCore;

type Aes256CfbEnc = Encryptor<Aes256>;
type Aes256CfbDec = Decryptor<Aes256>;

fn derive_key(password: &str) -> [u8; 32] {
    let mut hasher = Sha256::new();
    hasher.update(password.as_bytes());
    hasher.finalize().into()
}

pub fn create_capsule(source_path: &str, password: &str) -> Result<String, String> {
    let source = Path::new(source_path);
    if !source.exists() {
        return Err("La ruta de origen no existe.".to_string());
    }

    let file_stem = source.file_name().unwrap().to_str().unwrap();
    let timestamp = chrono::Local::now().format("%Y%m%d_%H%M%S").to_string();
    let capsula_name = format!("{}_{}.capsula", file_stem, timestamp);
    
    let santuario_raiz = r"C:\Users\Usuario\Desktop\Orbe_Santuario";
    let temp_zip_path = format!(r"{}\{}_{}.tmp.zip", santuario_raiz, file_stem, timestamp);
    let dest_capsulas = format!(r"{}\1_Almas_Encapsuladas", santuario_raiz);

    // 1. ZIP
    let zip_file = File::create(&temp_zip_path).map_err(|e| e.to_string())?;
    let mut zip = zip::ZipWriter::new(zip_file);
    let options = SimpleFileOptions::default().compression_method(zip::CompressionMethod::Deflated);

    if source.is_dir() {
        for entry in WalkDir::new(source) {
            let entry = entry.map_err(|e| e.to_string())?;
            let path = entry.path();
            let name = path.strip_prefix(Path::new(source).parent().unwrap()).unwrap();
            let name_str = name.to_str().unwrap().replace("\\", "/");
            if path.is_file() {
                zip.start_file(name_str, options).unwrap();
                let mut f = File::open(path).unwrap();
                let mut buf = Vec::new();
                f.read_to_end(&mut buf).unwrap();
                zip.write_all(&buf).unwrap();
            } else if path.is_dir() && !name_str.is_empty() {
                zip.add_directory(name_str, options).unwrap();
            }
        }
    } else {
        zip.start_file(source.file_name().unwrap().to_str().unwrap(), options).unwrap();
        let mut f = File::open(source).unwrap();
        let mut buf = Vec::new();
        f.read_to_end(&mut buf).unwrap();
        zip.write_all(&buf).unwrap();
    }
    zip.finish().map_err(|e| e.to_string())?;

    // 2. AES-256-CFB encrypt
    let key = derive_key(password);
    let mut iv = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut iv);

    let cipher = Aes256CfbEnc::new(&key.into(), &iv.into());

    std::fs::create_dir_all(&dest_capsulas).map_err(|e| e.to_string())?;
    let capsula_path = format!(r"{}\{}", dest_capsulas, capsula_name);

    let mut zip_bytes = Vec::new();
    File::open(&temp_zip_path).map_err(|e| e.to_string())?.read_to_end(&mut zip_bytes).map_err(|e| e.to_string())?;
    cipher.encrypt(&mut zip_bytes);

    let mut f_out = File::create(&capsula_path).map_err(|e| e.to_string())?;
    f_out.write_all(&iv).map_err(|e| e.to_string())?;
    f_out.write_all(&zip_bytes).map_err(|e| e.to_string())?;
    std::fs::remove_file(&temp_zip_path).ok();

    Ok(capsula_path)
}

pub fn invoke_capsule(capsule_path: &str, password: &str) -> Result<String, String> {
    let source = Path::new(capsule_path);
    if !source.exists() {
        return Err("La cápsula no existe.".to_string());
    }

    let mut data = Vec::new();
    File::open(capsule_path).map_err(|e| e.to_string())?.read_to_end(&mut data).map_err(|e| e.to_string())?;
    
    if data.len() < 16 { return Err("Cápsula corrupta o inválida.".to_string()); }

    let iv: [u8; 16] = data[..16].try_into().unwrap();
    let mut encrypted = data[16..].to_vec();

    let key = derive_key(password);
    let cipher = Aes256CfbDec::new(&key.into(), &iv.into());
    cipher.decrypt(&mut encrypted);

    let timestamp = chrono::Local::now().format("%Y%m%d_%H%M%S").to_string();
    let dest_base = format!(r"C:\Users\Usuario\Desktop\Orbe_Santuario\2_Almas_Liberadas\alma_{}", timestamp);
    std::fs::create_dir_all(&dest_base).map_err(|e| e.to_string())?;

    let temp_zip = format!(r"{}\temp.zip", dest_base);
    std::fs::write(&temp_zip, &encrypted).map_err(|e| e.to_string())?;

    let zip_file = File::open(&temp_zip).map_err(|e| e.to_string())?;
    let mut archive = zip::ZipArchive::new(zip_file).map_err(|e| format!("ZIP inválido (¿contraseña incorrecta?): {}", e))?;
    archive.extract(&dest_base).map_err(|e| e.to_string())?;
    std::fs::remove_file(&temp_zip).ok();

    Ok(dest_base)
}
