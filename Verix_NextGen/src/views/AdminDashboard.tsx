import { useState, useEffect } from 'react';

interface Props { onBack: () => void; onLog: (msg: string) => void; }

export function AdminDashboard({ onBack, onLog }: Props) {
  const [stats, setStats] = useState({ cpu: 0, ram: 0, uptime: '2d 14h 32m', activeThreads: 42, trash: '0.00 MB' });
  const [isVigilanceActive, setIsVigilanceActive] = useState(true);
  
  const soldiers = [
    { id: 'SENTINEL', name: 'Sentinel', status: 'ACTIVO', type: 'Rust', role: 'GitHub Nexus' },
    { id: 'CEREBRO', name: 'Cerebro', status: 'ACTIVO', type: 'Rust', role: 'Orquestador' },
    { id: 'VAULT', name: 'Vault', status: 'ACTIVO', type: 'Rust', role: 'Cifrado GCM' },
    { id: 'VISION', name: 'Vision', status: 'ACTIVO', type: 'Python', role: 'Facial' },
    { id: 'OIDO', name: 'Oído', status: 'ACTIVO', type: 'Python', role: 'Voz' },
    { id: 'MEMORIA', name: 'Memoria Madre', status: 'ACTIVO', type: 'Python', role: 'Inteligencia' },
    { id: 'BUS', name: 'Bus Mensajes', status: 'ACTIVO', type: 'Rust', role: 'Comunicación' },
    { id: '2FA', name: 'Guardian 2FA', status: 'ACTIVO', type: 'Python', role: 'Seguridad' },
    { id: 'ELITE', name: 'Elite Deploy', status: 'ACTIVO', type: 'Python', role: 'Cloud' },
    { id: 'GOD', name: 'God Mode', status: 'ACTIVO', type: 'Python', role: 'Root' },
    { id: 'HEALTH', name: 'Health', status: 'ACTIVO', type: 'Rust', role: 'Limpieza' },
  ];

  useEffect(() => {
    onLog('[ADMIN] Conexión establecida con el Núcleo del Orbe.');
    const interval = setInterval(() => {
      setStats(prev => ({
        ...prev,
        cpu: Math.floor(Math.random() * 8) + 1,
        ram: 1142 + Math.floor(Math.random() * 10),
        activeThreads: 38 + Math.floor(Math.random() * 5)
      }));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handlePurge = () => {
    onLog('[ADMIN] Iniciando purga de sistema vía Soldado SENTINEL...');
    // Aquí iría la llamada al backend que ejecuta temp_health_soldier.py
    setTimeout(() => {
      onLog('[OK] Purga completada. 0.00 MB eliminados (Sistema Limpio).');
      setStats(prev => ({ ...prev, trash: '0.00 MB' }));
    }, 2000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '10px', height: '100%', overflowY: 'auto' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: 'rgba(255,255,255,0.02)', padding: '15px', borderRadius: '12px', border: '1px solid var(--border-color)' }}>
        <div>
          <h2 style={{ fontSize: '1.8rem', fontWeight: 700, color: 'var(--accent)', textShadow: '0 0 15px var(--accent-glow)', letterSpacing: '2px' }}>SUPER ADMIN DASHBOARD</h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Vínculo de Confianza: <span style={{ color: '#27c93f' }}>VERIX-777-ROOT-GOD_SELLADO</span></p>
        </div>
        <button onClick={onBack} className="control-btn" style={{ width: 'auto', padding: '0 20px', height: '40px' }}>DESCONECTAR</button>
      </div>

      {/* Main Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '15px' }}>
        <StatCard label="CARGA CPU" value={`${stats.cpu}%`} color="#ffbd2e" />
        <StatCard label="USO RAM" value={`${stats.ram} MB`} color="#27c93f" />
        <StatCard label="SALUD (BASURA)" value={stats.trash} color="#ff5f56" />
        <StatCard label="HILOS ACTIVOS" value={stats.activeThreads} color="#00d2ff" />
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
        {/* Soldier Status Grid */}
        <div className="glass" style={{ padding: '20px' }}>
          <h3 style={{ marginBottom: '15px', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ width: '8px', height: '8px', background: '#27c93f', borderRadius: '50%', boxShadow: '0 0 10px #27c93f' }}></span>
            Estado del Batallón (11 Soldados)
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(140px, 1fr))', gap: '10px' }}>
            {soldiers.map(s => (
              <div key={s.id} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '12px', textAlign: 'center', transition: '0.2s' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '4px' }}>{s.id}</div>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', marginBottom: '4px' }}>{s.name}</div>
                <div style={{ fontSize: '0.65rem', color: s.status === 'ACTIVO' ? '#27c93f' : '#ffbd2e' }}>● {s.status}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Quick Actions & Migration */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass" style={{ padding: '20px' }}>
            <h3 style={{ marginBottom: '15px', fontSize: '1.1rem' }}>Acciones Rápidas</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <ActionButton label="Ejecutar Purga" onClick={handlePurge} color="#ff5f56" />
              <ActionButton label="Sincronizar Santuario" onClick={() => onLog('[ADMIN] Sincronizando con GitHub...')} color="#3b82f6" />
              <ActionButton label="Activar Escudo" onClick={() => setIsVigilanceActive(true)} color="#27c93f" />
            </div>
          </div>

          <div className="glass" style={{ padding: '20px', borderLeft: '4px solid #f2a900' }}>
            <h3 style={{ marginBottom: '10px', fontSize: '1.1rem', color: '#f2a900' }}>Rastreador Rust-Core</h3>
            <div style={{ fontSize: '0.85rem' }}>
              <div style={{ marginBottom: '8px', display: 'flex', justifyContent: 'space-between' }}>
                <span>Progreso Global</span>
                <span>60%</span>
              </div>
              <div style={{ height: '6px', background: '#333', borderRadius: '3px', overflow: 'hidden' }}>
                <div style={{ width: '60%', height: '100%', background: '#f2a900' }}></div>
              </div>
              <p style={{ marginTop: '10px', fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Próximo módulo: <b>memoria-madre</b></p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div className="glass" style={{ padding: '15px', borderLeft: `4px solid ${color}`, background: 'rgba(255,255,255,0.01)' }}>
      <div style={{ fontSize: '0.7rem', color: 'var(--text-secondary)', marginBottom: '5px', letterSpacing: '1px', textTransform: 'uppercase' }}>{label}</div>
      <div style={{ fontSize: '1.4rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{value}</div>
    </div>
  );
}

function ActionButton({ label, onClick, color }: { label: string; onClick: () => void; color: string }) {
  return (
    <button 
      onClick={onClick} 
      style={{ 
        background: 'transparent', border: `1px solid ${color}`, color: color, 
        padding: '10px', borderRadius: '8px', cursor: 'pointer', fontFamily: 'var(--font-mono)',
        fontSize: '0.8rem', transition: '0.2s'
      }}
      onMouseOver={(e) => (e.currentTarget.style.background = `${color}22`)}
      onMouseOut={(e) => (e.currentTarget.style.background = 'transparent')}
    >
      {label}
    </button>
  );
}

