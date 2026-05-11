use std::fs::File;
use std::io::{Write, Read};
use std::path::Path;
use walkdir::WalkDir;
use zip::write::FileOptions;
use chrono::Local;

pub fn create_backup() -> Result<String, String> {
    let timestamp = Local::now().format("%Y%m%d_%H%M%S").to_string();
    let backup_dir = r"C:\Users\Usuario\Desktop\Orbe_Santuario\Backups";
    
    if !Path::new(backup_dir).exists() {
        std::fs::create_dir_all(backup_dir).map_err(|e| e.to_string())?;
    }

    let backup_path = format!(r"{}\Verix_Soul_Backup_{}.zip", backup_dir, timestamp);
    let file = File::create(&backup_path).map_err(|e| e.to_string())?;
    let mut zip = zip::ZipWriter::new(file);

    let options = zip::write::SimpleFileOptions::default()
        .compression_method(zip::CompressionMethod::Deflated)
        .unix_permissions(0o755);

    let paths_to_backup = [
        r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe",
        r"C:\Users\Usuario\Desktop\Orbe_Santuario",
    ];

    for root_path in paths_to_backup {
        let root = Path::new(root_path);
        if !root.exists() { continue; }

        let _folder_name = root.file_name().unwrap().to_string_lossy();

        for entry in WalkDir::new(root)
            .into_iter()
            .filter_map(|e| e.ok())
        {
            let path = entry.path();
            let name = path.strip_prefix(root.parent().unwrap()).unwrap();

            // Ignore bulky and temporary folders
            if path.to_string_lossy().contains("target") || 
               path.to_string_lossy().contains("node_modules") ||
               path.to_string_lossy().contains(".git") ||
               path.to_string_lossy().contains("Backups") ||
               path.to_string_lossy().contains(".tmp") 
            {
                continue;
            }

            if path.is_file() {
                zip.start_file(name.to_string_lossy().to_string(), options).map_err(|e| e.to_string())?;
                let mut f = File::open(path).map_err(|e| e.to_string())?;
                let mut buffer = Vec::new();
                f.read_to_end(&mut buffer).map_err(|e| e.to_string())?;
                zip.write_all(&buffer).map_err(|e| e.to_string())?;
            } else if !name.as_os_str().is_empty() {
                zip.add_directory(name.to_string_lossy().to_string(), options).map_err(|e| e.to_string())?;
            }
        }
    }

    zip.finish().map_err(|e| e.to_string())?;
    Ok(backup_path)
}
