import { useState } from 'react';

interface Props { onBack: () => void; onLog: (msg: string) => void; }

const API = 'http://localhost:3000/api';

// =================== HELPER ===================
async function apiCall(endpoint: string, body?: object, method = 'POST') {
  const res = await fetch(`${API}${endpoint}`, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  return res.json();
}

// =================== STYLE HELPERS ===================
const inputStyle: React.CSSProperties = {
  padding: '12px 16px',
  background: 'rgba(0,0,0,0.5)',
  border: '1px solid var(--border-color)',
  color: 'var(--text-primary)',
  borderRadius: '8px',
  fontFamily: 'var(--font-mono)',
  fontSize: '0.9rem',
  outline: 'none',
  width: '100%',
};

const labelStyle: React.CSSProperties = {
  color: 'var(--text-secondary)',
  fontSize: '0.8rem',
  textTransform: 'uppercase',
  letterSpacing: '1px',
  marginBottom: '6px',
};

// =================== VIEW: CREAR CÁPSULA (1) ===================
export function CapsuleCreator({ onBack, onLog }: Props) {
  const [path, setPath] = useState('');
  const [pass, setPass] = useState('');
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!path || !pass) { onLog('[ERROR] Ruta y contraseña requeridas.'); return; }
    setLoading(true);
    onLog(`> Forjando cápsula para: ${path}...`);
    const d = await apiCall('/capsule/create', { source_path: path, password: pass });
    onLog(d.message);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' }}>
      <ViewHeader title="⬡ Crear Cápsula" subtitle="Comprime y encripta un archivo o carpeta con AES-256-CFB nativo en Rust." onBack={onBack} />
      <label style={labelStyle}>Ruta del archivo o carpeta a sellar:</label>
      <input style={inputStyle} value={path} onChange={e => setPath(e.target.value)} placeholder="C:\Users\Usuario\Documents\proyecto" />
      <label style={labelStyle}>Contraseña de encriptación:</label>
      <input style={inputStyle} type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="Contraseña AES-256..." />
      <CyberButton onClick={run} loading={loading}>[ Forjar Cápsula ]</CyberButton>
    </div>
  );
}

// =================== VIEW: INVOCAR ALMA (2) ===================
export function CapsuleInvoker({ onBack, onLog }: Props) {
  const [path, setPath] = useState('');
  const [pass, setPass] = useState('');
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!path || !pass) { onLog('[ERROR] Ruta de cápsula y contraseña requeridas.'); return; }
    setLoading(true);
    onLog(`> Invocando alma de cápsula: ${path}...`);
    const d = await apiCall('/capsule/invoke', { capsule_path: path, password: pass });
    onLog(d.message);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' }}>
      <ViewHeader title="⬡ Invocar Alma" subtitle="Desencripta y libera el contenido de una cápsula en el Santuario." onBack={onBack} />
      <label style={labelStyle}>Ruta del archivo .capsula:</label>
      <input style={inputStyle} value={path} onChange={e => setPath(e.target.value)} placeholder="C:\...\1_Almas_Encapsuladas\archivo.capsula" />
      <label style={labelStyle}>Contraseña original:</label>
      <input style={inputStyle} type="password" value={pass} onChange={e => setPass(e.target.value)} placeholder="La misma contraseña usada al sellar..." />
      <CyberButton onClick={run} loading={loading}>[ Invocar Alma ]</CyberButton>
    </div>
  );
}

// =================== VIEW: GESTOR GIT (3) ===================
export function GitManager({ onBack, onLog }: Props) {
  const [msg, setMsg] = useState('');
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const sync = async () => {
    setLoading(true);
    onLog('> Iniciando Latido Eterno (git add + commit + push)...');
    const d = await apiCall('/git/sync', { message: msg || 'Latido Eterno de Verix' });
    onLog(d.message);
    setLoading(false);
  };

  const clone = async () => {
    if (!url) { onLog('[ERROR] URL de repositorio requerida.'); return; }
    setLoading(true);
    onLog(`> Clonando alma desde el Éter: ${url}...`);
    const d = await apiCall('/git/clone', { repo_url: url });
    onLog(d.message);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', maxWidth: '600px' }}>
      <ViewHeader title="⬡ Gestor de Almas (Git)" subtitle="Sincroniza el Orbe con el Éter o invoca repos remotos." onBack={onBack} />
      <label style={labelStyle}>Mensaje de commit (opcional):</label>
      <input style={inputStyle} value={msg} onChange={e => setMsg(e.target.value)} placeholder="Latido Eterno de Verix" />
      <CyberButton onClick={sync} loading={loading}>[ Latido Eterno — Sincronizar con GitHub ]</CyberButton>
      <hr style={{ border: '1px solid var(--border-color)', margin: '8px 0' }} />
      <label style={labelStyle}>Clonar repositorio remoto (URL .git):</label>
      <input style={inputStyle} value={url} onChange={e => setUrl(e.target.value)} placeholder="https://github.com/usuario/repo.git" />
      <CyberButton onClick={clone} loading={loading}>[ Invocar Alma Remota — Git Clone ]</CyberButton>
    </div>
  );
}

// =================== VIEW: GESTOR DE CÁPSULAS (4) ===================
export function CapsuleManager({ onBack, onLog }: Props) {
  const [capsulas, setCapsulas] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const d = await apiCall('/capsule/list', undefined, 'GET');
    onLog(d.message);
    setCapsulas(d.data || []);
    setLoading(false);
  };

  const del = async (path: string, name: string) => {
    if (!confirm(`¿Deseas eliminar "${name}"?`)) return;
    const d = await apiCall('/capsule/delete', { capsule_path: path });
    onLog(d.message);
    load();
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <ViewHeader title="⬡ Gestor de Cápsulas" subtitle="Administra las almas selladas en el Santuario." onBack={onBack} />
      <CyberButton onClick={load} loading={loading}>[ Escanear Santuario ]</CyberButton>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {capsulas.map(c => (
          <div key={c.path} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '12px 16px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div>
              <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: '0.9rem' }}>{c.name}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>{c.size_kb} KB</div>
            </div>
            <button onClick={() => del(c.path, c.name)} style={{ background: 'rgba(255,50,50,0.15)', border: '1px solid rgba(255,50,50,0.4)', color: '#ff5555', borderRadius: '6px', padding: '6px 14px', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.8rem' }}>Eliminar</button>
          </div>
        ))}
        {capsulas.length === 0 && <div style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '0.9rem' }}>Ninguna cápsula escaneada aún.</div>}
      </div>
    </div>
  );
}

// =================== VIEW: INTEGRIDAD Y CRIPTOGRAFÍA (5) ===================
export function CryptoPanel({ onBack, onLog }: Props) {
  const [filePath, setFilePath] = useState('');
  const [loading, setLoading] = useState(false);
  const [hash, setHash] = useState('');
  const [logs, setLogs] = useState<string[]>([]);

  const calcHash = async () => {
    if (!filePath) { onLog('[ERROR] Ruta requerida.'); return; }
    setLoading(true);
    const d = await apiCall('/crypto/checksum', { file_path: filePath });
    onLog(d.message);
    if (d.data?.sha256) setHash(d.data.sha256);
    setLoading(false);
  };

  const getLog = async () => {
    setLoading(true);
    const d = await apiCall('/logs', undefined, 'GET');
    onLog(d.message);
    setLogs(d.data || []);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <ViewHeader title="⬡ Integridad y Criptografía" subtitle="Calcula checksums SHA-256 y consulta el log de eventos del Orbe." onBack={onBack} />
      <label style={labelStyle}>Archivo para calcular SHA-256:</label>
      <input style={inputStyle} value={filePath} onChange={e => setFilePath(e.target.value)} placeholder="C:\...\archivo.capsula" />
      <CyberButton onClick={calcHash} loading={loading}>[ Calcular Checksum SHA-256 ]</CyberButton>
      {hash && <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: '0.8rem', wordBreak: 'break-all', background: 'rgba(0,0,0,0.4)', padding: '12px', borderRadius: '8px' }}>SHA-256: {hash}</div>}
      <hr style={{ border: '1px solid var(--border-color)', margin: '8px 0' }} />
      <CyberButton onClick={getLog} loading={loading}>[ Ver Registro de Eventos del Orbe ]</CyberButton>
      {logs.length > 0 && (
        <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '8px', padding: '12px', maxHeight: '250px', overflowY: 'auto' }}>
          {logs.map((l, i) => <div key={i} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)', padding: '2px 0' }}>{l}</div>)}
        </div>
      )}
    </div>
  );
}

// =================== VIEW: NIDO DEL HUMANODEV (6) ===================
export function NidoDev({ onBack, onLog }: Props) {
  const [currentPath, setCurrentPath] = useState('C:\\Users\\Usuario\\Desktop\\Orbe_Santuario\\5_Nido_HumanoDev');
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const browse = async (path?: string) => {
    const p = path || currentPath;
    setLoading(true);
    const d = await apiCall('/sanctuary/browse', { path: p });
    if (d.ok) {
      setCurrentPath(d.data.current_path);
      setItems(d.data.items || []);
    }
    onLog(d.message);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <ViewHeader title="⬡ Nido del HumanoDev" subtitle="Tu espacio sagrado de creación y trabajo." onBack={onBack} />
      <div style={{ display: 'flex', gap: '8px' }}>
        <input style={{ ...inputStyle, flex: 1 }} value={currentPath} onChange={e => setCurrentPath(e.target.value)} />
        <CyberButton onClick={() => browse()} loading={loading}>Ir</CyberButton>
      </div>
      <FileList items={items} onNavigate={p => browse(p)} />
    </div>
  );
}

// =================== VIEW: NAVEGADOR DEL SANTUARIO (7) ===================
export function SanctuaryNavigator({ onBack, onLog }: Props) {
  const [currentPath, setCurrentPath] = useState('C:\\Users\\Usuario\\Desktop\\Orbe_Santuario');
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);

  const browse = async (path?: string) => {
    const p = path || currentPath;
    setLoading(true);
    const d = await apiCall('/sanctuary/browse', { path: p });
    if (d.ok) {
      setCurrentPath(d.data.current_path);
      setItems(d.data.items || []);
    }
    onLog(d.message);
    setLoading(false);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <ViewHeader title="⬡ Navegador del Santuario" subtitle="Explora la estructura completa del Orbe." onBack={onBack} />
      <div style={{ display: 'flex', gap: '8px' }}>
        <input style={{ ...inputStyle, flex: 1 }} value={currentPath} onChange={e => setCurrentPath(e.target.value)} />
        <CyberButton onClick={() => browse()} loading={loading}>Explorar</CyberButton>
      </div>
      <FileList items={items} onNavigate={p => browse(p)} />
    </div>
  );
}

// =================== VIEW: MODO SUEÑO (8) ===================
export function SleepMode({ onBack, onLog }: Props) {
  const [estado, setEstado] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const d = await apiCall('/sleep/status', undefined, 'GET');
    onLog(d.message);
    setEstado(d.data);
    setLoading(false);
  };

  const set = async (newState: string) => {
    setLoading(true);
    const d = await apiCall('/sleep/set', { estado: newState, timestamp: new Date().toISOString() });
    onLog(d.message);
    load();
  };

  const estadoColor = estado?.estado === 'activo' ? '#27c93f' : estado?.estado === 'dormido' ? '#7b8cff' : '#aaa';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', maxWidth: '500px' }}>
      <ViewHeader title="⬡ Modo Sueño" subtitle="Controla el ciclo de energía y el estado del Orbe." onBack={onBack} />
      <CyberButton onClick={load} loading={loading}>[ Leer Estado Actual ]</CyberButton>
      {estado && (
        <div style={{ background: 'rgba(0,0,0,0.4)', borderRadius: '12px', padding: '20px', textAlign: 'center' }}>
          <div style={{ width: 20, height: 20, borderRadius: '50%', background: estadoColor, margin: '0 auto 12px', boxShadow: `0 0 20px ${estadoColor}` }}></div>
          <div style={{ fontFamily: 'var(--font-mono)', color: estadoColor, fontSize: '1.2rem', textTransform: 'uppercase' }}>{estado.estado || 'desconocido'}</div>
          {estado.timestamp && <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem', marginTop: '8px' }}>{estado.timestamp}</div>}
        </div>
      )}
      <div style={{ display: 'flex', gap: '12px' }}>
        <CyberButton onClick={() => set('activo')} loading={loading}>[ Despertar ]</CyberButton>
        <CyberButton onClick={() => set('dormido')} loading={loading}>[ Dormir ]</CyberButton>
        <CyberButton onClick={() => set('vigilancia')} loading={loading}>[ Vigilancia ]</CyberButton>
      </div>
    </div>
  );
}

// =================== VIEW: CEREBRO ORBE (9) ===================
export function CerebroOrbe({ onBack, onLog }: Props) {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    const d = await apiCall('/brain/status', undefined, 'GET');
    onLog(d.message);
    setData(d.data);
    setLoading(false);
  };

  const misiones = data?.misiones_activas || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      <ViewHeader title="⬡ Cerebro Orbe" subtitle="Gestiona la vigilancia, misiones y la agenda del Orbe." onBack={onBack} />
      <CyberButton onClick={load} loading={loading}>[ Leer Estado del Cerebro ]</CyberButton>
      {misiones.length > 0 ? (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label style={labelStyle}>Misiones Activas ({misiones.length}):</label>
          {misiones.map((m: any, i: number) => (
            <div key={i} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', borderRadius: '8px', padding: '12px' }}>
              <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: '0.85rem' }}>{m.id}</div>
              <div style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>Tarea: {m.tarea} | Estado: {m.status}</div>
            </div>
          ))}
        </div>
      ) : data && (
        <div style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '0.9rem' }}>No hay misiones activas registradas.</div>
      )}
    </div>
  );
}

// =================== SHARED COMPONENTS ===================
function ViewHeader({ title, subtitle, onBack }: { title: string; subtitle: string; onBack: () => void }) {
  return (
    <div style={{ marginBottom: '8px' }}>
      <button onClick={onBack} style={{ background: 'transparent', border: '1px solid var(--border-color)', color: 'var(--text-secondary)', padding: '6px 14px', borderRadius: '6px', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.75rem', marginBottom: '16px' }}>← Volver</button>
      <h2 style={{ fontSize: '1.8rem', fontWeight: 500, marginBottom: '6px' }}>{title}</h2>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>{subtitle}</p>
    </div>
  );
}

function CyberButton({ onClick, loading, children }: { onClick: () => void; loading: boolean; children: React.ReactNode }) {
  return (
    <button onClick={onClick} disabled={loading} style={{ background: loading ? 'rgba(0,0,0,0.2)' : 'var(--bg-panel)', border: '1px solid var(--accent)', color: loading ? 'var(--text-secondary)' : 'var(--accent)', padding: '12px 20px', borderRadius: '8px', fontFamily: 'var(--font-mono)', cursor: loading ? 'wait' : 'pointer', transition: 'all 0.2s', textTransform: 'uppercase', fontWeight: 600, letterSpacing: '1px', fontSize: '0.85rem' }}>
      {loading ? '[ Procesando... ]' : children}
    </button>
  );
}

function FileList({ items, onNavigate }: { items: any[]; onNavigate: (path: string) => void }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', maxHeight: '350px', overflowY: 'auto' }}>
      {items.map((item, i) => (
        <div key={i} onClick={() => item.is_dir && onNavigate(item.path)} style={{ background: 'rgba(0,0,0,0.3)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '10px 14px', display: 'flex', justifyContent: 'space-between', cursor: item.is_dir ? 'pointer' : 'default', transition: 'border-color 0.2s' }}
          onMouseEnter={e => item.is_dir && ((e.currentTarget as HTMLElement).style.borderColor = 'var(--accent)')}
          onMouseLeave={e => ((e.currentTarget as HTMLElement).style.borderColor = 'var(--border-color)')}>
          <span style={{ fontFamily: 'var(--font-mono)', color: item.is_dir ? 'var(--accent)' : 'var(--text-primary)', fontSize: '0.85rem' }}>
            {item.is_dir ? '📁 ' : '📄 '}{item.name}
          </span>
          {!item.is_dir && <span style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>{item.size_kb} KB</span>}
        </div>
      ))}
      {items.length === 0 && <div style={{ color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)', fontSize: '0.85rem', padding: '12px' }}>Directorio vacío.</div>}
    </div>
  );
}
