import React, { useState } from 'react';

interface Props {
  onBack: () => void;
  onLog: (msg: string) => void;
}

export function CapsuleCreator({ onBack, onLog }: Props) {
  const [filePath, setFilePath] = useState('');
  const [password, setPassword] = useState('');

  const handleCreate = async () => {
    if (!filePath || !password) {
      onLog("[ERROR] Debes proporcionar una ruta válida y una contraseña.");
      return;
    }
    onLog(`> Iniciando forja nativa de cápsula en Rust para: ${filePath}...`);
    try {
      const res = await fetch(`http://localhost:3000/api/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actionId: 1, payload: filePath, password: password })
      });
      const data = await res.json();
      onLog(data.message);
    } catch (e) {
      onLog(`[ERROR]: Falla en la red al contactar Rust API.`);
    }
  };

  return (
    <div className="view-container animate-fade-in">
      <div className="view-header">
        <button className="cyber-button secondary" onClick={onBack}>← Volver</button>
        <h2>1. Crear Cápsula</h2>
      </div>
      
      <div className="view-content glass" style={{ padding: '24px', marginTop: '20px' }}>
        <p style={{ color: 'var(--text-secondary)', marginBottom: '20px' }}>
          Sella un archivo o carpeta en una cápsula encriptada dentro del Santuario de Verix.
        </p>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
          <label style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>Ruta del Archivo/Carpeta a Encapsular:</label>
          <input 
            type="text" 
            value={filePath}
            onChange={(e) => setFilePath(e.target.value)}
            placeholder="C:\Users\Usuario\Documents\proyecto_secreto"
            style={{
              padding: '12px',
              background: 'rgba(0,0,0,0.5)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              borderRadius: '8px',
              fontFamily: 'var(--font-mono)'
            }}
          />
          <label style={{ color: 'var(--text-primary)', fontSize: '0.9rem' }}>Contraseña de Encriptación (AES-256):</label>
          <input 
            type="password" 
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Introduce una contraseña segura..."
            style={{
              padding: '12px',
              background: 'rgba(0,0,0,0.5)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-primary)',
              borderRadius: '8px',
              fontFamily: 'var(--font-mono)'
            }}
          />
          <button className="cyber-button" onClick={handleCreate} style={{ marginTop: '10px' }}>
            [ Forjar Cápsula (Rust) ]
          </button>
        </div>
      </div>
    </div>
  );
}
