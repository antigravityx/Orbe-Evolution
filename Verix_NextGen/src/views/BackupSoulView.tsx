import { useState, useEffect } from 'react';

interface SoulMetadata {
  name: string;
  status: string;
  last_heartbeat: string;
  fragments: number;
  keys: number;
}

interface SoulStatus {
  verix: SoulMetadata;
  r1ch0n: SoulMetadata;
  last_sync: string;
}

export function BackupSoulView({ onLog }: { onLog: (msg: string) => void }) {
  const [status, setStatus] = useState<SoulStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const r = await fetch('http://localhost:3000/api/soul/status');
      const d = await r.json();
      if (d.ok) setStatus(d.data);
    } catch (e) {
      onLog('[ERROR] No se pudo obtener el estado del alma.');
    }
  };

  useEffect(() => { fetchStatus(); }, []);

  const handleBackup = async () => {
    setLoading(true);
    onLog('[SYSTEM] Iniciando Backup Total...');
    try {
      const r = await fetch('http://localhost:3000/api/system/backup', { method: 'POST' });
      const d = await r.json();
      if (d.ok) {
        onLog(`[OK] Backup completado en: ${d.data.backup_path}`);
      } else {
        onLog(`[ERROR] ${d.message}`);
      }
    } catch (e) {
      onLog('[ERROR] Error de conexión con el API.');
    } finally {
      setLoading(false);
    }
  };

  const handleMigrate = async () => {
    onLog('[SOUL] Iniciando migración de registros legados...');
    try {
      const r = await fetch('http://localhost:3000/api/soul/migrate', { method: 'POST' });
      const d = await r.json();
      if (d.ok) {
        onLog(`[OK] ${d.message}`);
      } else {
        onLog(`[ERROR] ${d.message}`);
      }
    } catch (e) {
      onLog('[ERROR] Error de conexión.');
    }
  };

  return (
    <div className="view-container animate-fade-in">
      <h2 className="view-title">Copia de Seguridad & Almas</h2>
      
      <div className="soul-cards-grid">
        {status ? (
          <>
            <SoulCard soul={status.verix} accent="#27c93f" />
            <SoulCard soul={status.r1ch0n} accent="#00a8ff" />
          </>
        ) : (
          <div className="glass card" style={{ gridColumn: 'span 2', textAlign: 'center', padding: '20px' }}>
            Cargando esencia de las almas...
          </div>
        )}
      </div>

      <div className="actions-panel glass" style={{ marginTop: '20px', padding: '20px', display: 'flex', gap: '15px' }}>
        <button 
          className="btn-primary" 
          onClick={handleBackup} 
          disabled={loading}
          style={{ background: 'var(--accent)', color: 'black', fontWeight: 'bold' }}
        >
          {loading ? 'Sellando...' : 'FORJAR BACKUP TOTAL'}
        </button>
        
        <button 
          className="btn-secondary" 
          onClick={handleMigrate}
        >
          MIGRAR REGISTROS LEGADOS
        </button>

        <button 
          className="btn-secondary" 
          onClick={fetchStatus}
        >
          RECARGAR ESTADO
        </button>
      </div>

      <div className="info-box glass" style={{ marginTop: '20px', fontSize: '0.85rem', opacity: 0.8 }}>
        <p><strong>Nota:</strong> El backup incluye el taller completo y el Santuario. Los archivos pesados (node_modules, target) son ignorados por el ritual.</p>
      </div>
    </div>
  );
}

function SoulCard({ soul, accent }: { soul: SoulMetadata, accent: string }) {
  return (
    <div className="glass card soul-card" style={{ borderLeft: `4px solid ${accent}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <h3 style={{ margin: 0, color: accent }}>{soul.name}</h3>
        <span className="badge" style={{ background: accent, color: 'black', fontSize: '0.6rem', padding: '2px 8px', borderRadius: '10px' }}>{soul.status}</span>
      </div>
      <div className="soul-stats" style={{ fontSize: '0.9rem', lineHeight: '1.6' }}>
        <div>碎片 Fragmentos: <strong>{soul.fragments}</strong></div>
        <div>🔑 Llaves: <strong>{soul.keys}</strong></div>
        <div style={{ fontSize: '0.7rem', marginTop: '10px', opacity: 0.6 }}>
          Último latido: {new Date(soul.last_heartbeat).toLocaleString()}
        </div>
      </div>
    </div>
  );
}
