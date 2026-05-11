import { useState, useEffect } from 'react';

interface Props { onBack: () => void; onLog: (msg: string) => void; }

export function AdminDashboard({ onBack, onLog }: Props) {
  const [stats, setStats] = useState({ cpu: 0, ram: 0, uptime: '0h 0m', activeThreads: 0 });
  const [isVigilanceActive, setIsVigilanceActive] = useState(true);

  useEffect(() => {
    onLog('[ADMIN] Cargando panel de control superior...');
    const interval = setInterval(() => {
      setStats({
        cpu: Math.floor(Math.random() * 15) + 5,
        ram: Math.floor(Math.random() * 200) + 1100,
        uptime: '2d 14h 32m',
        activeThreads: 42
      });
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px', padding: '10px' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h2 style={{ fontSize: '2.2rem', fontWeight: 600, color: 'var(--accent)', textShadow: '0 0 15px var(--accent-glow)' }}>SUPER ADMIN DASHBOARD</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Control Central del Ecosistema Orbe Verix</p>
        </div>
        <button onClick={onBack} style={{ background: 'transparent', border: '1px solid var(--accent)', color: 'var(--accent)', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontFamily: 'var(--font-mono)' }}>SALIR</button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
        <StatCard label="CPU LOAD" value={`${stats.cpu}%`} color="#ffbd2e" />
        <StatCard label="RAM USAGE" value={`${stats.ram} MB`} color="#27c93f" />
        <StatCard label="UPTIME" value={stats.uptime} color="#27c93f" />
        <StatCard label="ACTIVE THREADS" value={stats.activeThreads} color="#ff5f56" />
      </div>

      <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', borderRadius: '16px', padding: '24px' }}>
        <h3 style={{ marginBottom: '16px', fontSize: '1.2rem' }}>Interruptores de Sistema</h3>
        <div style={{ display: 'flex', gap: '24px' }}>
          <ToggleSwitch label="MODO VIGILANCIA" active={isVigilanceActive} onClick={() => {
            setIsVigilanceActive(!isVigilanceActive);
            onLog(`[ADMIN] Vigilancia ${!isVigilanceActive ? 'ACTIVADA' : 'DESACTIVADA'}`);
          }} />
          <ToggleSwitch label="SELLADO TOTAL" active={false} onClick={() => onLog('[ADMIN] ADVERTENCIA: Sellado total requiere confirmación física.')} />
          <ToggleSwitch label="CONEXIÓN ÉTER" active={true} onClick={() => onLog('[ADMIN] El vínculo con el Éter es permanente.')} />
        </div>
      </div>

      <div style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid var(--border-color)', borderRadius: '16px', padding: '24px' }}>
        <h3 style={{ marginBottom: '16px', fontSize: '1.2rem' }}>Flujos de Datos Recientes</h3>
        <div style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--text-secondary)', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div>[INFO] Checksum validado para Nido_HumanoDev/core_v2.rs</div>
          <div>[OK] Sincronización con GitHub completada (SHA: 7a8f1c)</div>
          <div>[WARN] Intento de acceso no autorizado desde IP local (BLOQUEADO)</div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, color }: { label: string; value: string | number; color: string }) {
  return (
    <div style={{ background: 'rgba(0,0,0,0.4)', border: '1px solid var(--border-color)', borderRadius: '12px', padding: '20px', borderLeft: `4px solid ${color}` }}>
      <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginBottom: '8px', letterSpacing: '1px' }}>{label}</div>
      <div style={{ fontSize: '1.6rem', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>{value}</div>
    </div>
  );
}

function ToggleSwitch({ label, active, onClick }: { label: string; active: boolean; onClick: () => void }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={onClick}>
      <div style={{ 
        width: '44px', height: '22px', background: active ? 'var(--accent)' : '#444', 
        borderRadius: '20px', position: 'relative', transition: '0.3s' 
      }}>
        <div style={{ 
          width: '18px', height: '18px', background: '#fff', borderRadius: '50%', 
          position: 'absolute', top: '2px', left: active ? '24px' : '2px', transition: '0.3s' 
        }}></div>
      </div>
      <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>{label}</span>
    </div>
  );
}
