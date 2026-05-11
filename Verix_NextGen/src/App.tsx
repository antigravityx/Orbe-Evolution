import { useState, useEffect, useRef } from 'react';
import './App.css';
import {
  CapsuleCreator, CapsuleInvoker, GitManager, CapsuleManager,
  CryptoPanel, NidoDev, SanctuaryNavigator, SleepMode, CerebroOrbe
} from './views/AllViews';
import { BackupSoulView } from './views/BackupSoulView';
import { AdminDashboard } from './views/AdminDashboard';

const MENU_OPTIONS = [
  { id: 1, icon: '⬡', title: 'Crear Cápsula', description: 'Sella archivos con AES-256-CFB nativo' },
  { id: 2, icon: '⬡', title: 'Invocar Alma', description: 'Descifra y libera una cápsula' },
  { id: 3, icon: '⬡', title: 'Gestor de Almas', description: 'Git — sincroniza con el Éter' },
  { id: 4, icon: '⬡', title: 'Gestor de Cápsulas', description: 'Administra las cápsulas del Santuario' },
  { id: 5, icon: '⬡', title: 'Integridad & Cripto', description: 'SHA-256, firmas y registros' },
  { id: 6, icon: '⬡', title: 'Nido del HumanoDev', description: 'Tu espacio sagrado de creación' },
  { id: 7, icon: '⬡', title: 'Navegador Santuario', description: 'Explora la estructura del Orbe' },
  { id: 8, icon: '⬡', title: 'Modo Sueño', description: 'Estado y ciclo de energía del Orbe' },
  { id: 9, icon: '⬡', title: 'Cerebro Orbe', description: 'Misiones, vigilancia y agenda' },
  { id: 10, icon: '⬡', title: 'Backup & Almas', description: 'Backup total y estado de Verix & r1ch0n' },
  { id: 12, icon: '☢', title: 'SUPER ADMIN', description: 'Control total de flujos y sistemas' },
  { id: 11, icon: '⬡', title: 'Salir del Orbe', description: 'Cierra la conexión' },
];

const ASCII_LOGO = `   *           .
.      .-.
    *  |o_o|         *
.       |:_/|
      * //   \\\\ \\\\   *
       (|     | )
.     /'\\_   _/'\\ .
      \\___)=(___/`;

function App() {
  const [logs, setLogs] = useState<string[]>([
    '[SYSTEM] Verix NextGen API — Rust Puro + Vite',
    '[OK] Motor AES-256-CFB activo.',
    '[OK] Todas las funciones operativas.',
    'Esperando instrucciones del Arquitecto Richon...'
  ]);
  const [theme, setTheme] = useState('dark');
  const [activeView, setActiveView] = useState<number | null>(null);
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const [isMinimized, setIsMinimized] = useState(false);
  const logEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => { document.body.setAttribute('data-theme', theme); }, [theme]);
  useEffect(() => { logEndRef.current?.scrollIntoView({ behavior: 'smooth' }); }, [logs]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Alt + Z: Minimizar
      if (e.altKey && e.key.toLowerCase() === 'z') {
        setIsMinimized(prev => !prev);
        addLog(`[UI] Aplicación ${!isMinimized ? 'Minimizada' : 'Restaurada'} (Alt + Z)`);
      }
      // Alt + X: Home / Escape rápido
      if (e.altKey && e.key.toLowerCase() === 'x') {
        setActiveView(null);
        addLog('[UI] Regresando al Home (Alt + X)');
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isMinimized]);

  useEffect(() => {
    fetch('http://localhost:3000/api/health')
      .then(r => r.json())
      .then(d => { setApiStatus('online'); addLog(`[API] ${d.message}`); })
      .catch(() => { setApiStatus('offline'); addLog('[ERROR] API Rust no responde. ¿Está corriendo?'); });
  }, []);

  const addLog = (msg: string) => setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);

  const handleMenuClick = (id: number) => {
    if (id === 11) { addLog('[ORBE] Sesión cerrada. Hasta la próxima, Arquitecto.'); return; }
    setActiveView(id);
    addLog(`> Accediendo a: ${MENU_OPTIONS[id - 1].title}`);
  };

  const renderView = () => {
    const props = { onBack: () => setActiveView(null), onLog: addLog };
    switch (activeView) {
      case 1: return <CapsuleCreator {...props} />;
      case 2: return <CapsuleInvoker {...props} />;
      case 3: return <GitManager {...props} />;
      case 4: return <CapsuleManager {...props} />;
      case 5: return <CryptoPanel {...props} />;
      case 6: return <NidoDev {...props} />;
      case 7: return <SanctuaryNavigator {...props} />;
      case 8: return <SleepMode {...props} />;
      case 9: return <CerebroOrbe {...props} />;
      case 10: return <BackupSoulView onLog={addLog} />;
      case 12: return <AdminDashboard {...props} />;
      default: return <HomeView />;
    }
  };

  const statusColor = apiStatus === 'online' ? '#27c93f' : apiStatus === 'offline' ? '#ff5f56' : '#ffbd2e';

  return (
    <div className={`layout-container animate-fade-in ${isMinimized ? 'minimized' : ''}`}>
      {/* SIDEBAR */}
      <aside className="sidebar glass">
        <div className="brand">
          <div className="brand-title">
            <div className="brand-indicator" style={{ background: statusColor, boxShadow: `0 0 8px ${statusColor}` }}></div>
            Verix Soul
            <span style={{ fontSize: '0.65rem', color: statusColor, fontFamily: 'var(--font-mono)', marginLeft: '4px' }}>
              {apiStatus === 'online' ? 'ONLINE' : apiStatus === 'offline' ? 'OFFLINE' : '...'}
            </span>
          </div>
          <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
            <button className="control-btn" onClick={() => setIsMinimized(!isMinimized)} title="Minimizar (Alt+Z)">_</button>
            <select className="theme-select" value={theme} onChange={e => setTheme(e.target.value)}>
              <option value="dark">Dark</option>
              <option value="stealth">Stealth</option>
              <option value="light">Light</option>
            </select>
          </div>
        </div>

        <nav className="menu-list">
          {MENU_OPTIONS.map(opt => (
            <button
              key={opt.id}
              className={`menu-item ${activeView === opt.id ? 'active' : ''}`}
              onClick={() => handleMenuClick(opt.id)}
            >
              <span className="menu-item-num">{String(opt.id).padStart(2, '0')}</span>
              <span>
                <span className="menu-item-title">{opt.title}</span>
                <span className="menu-item-desc">{opt.description}</span>
              </span>
            </button>
          ))}
        </nav>
      </aside>

      {/* MAIN */}
      <main className="main-area">
        <section className="hero-section" style={{ flex: 1, overflowY: 'auto', height: 'auto' }}>
          <div className="animate-fade-in" key={activeView}>
            {renderView()}
          </div>
        </section>

        {/* TERMINAL LOG */}
        <section className="terminal-wrapper glass" style={{ flex: 'none', height: '28%', minHeight: '160px' }}>
          <div className="terminal-header">
            <div className="terminal-dots">
              <div className="tdot" style={{ background: '#ff5f56' }}></div>
              <div className="tdot" style={{ background: '#ffbd2e' }}></div>
              <div className="tdot" style={{ background: '#27c93f' }}></div>
            </div>
            <span className="terminal-title">~/verix-core/output</span>
          </div>
          <div className="terminal-body">
            {logs.map((log, i) => (
              <div key={i} className="terminal-line">
                <span className="terminal-prefix">➜</span>
                <span>{log}</span>
              </div>
            ))}
            <div ref={logEndRef} />
            <div className="terminal-line">
              <span className="terminal-prefix">➜</span>
              <span className="cursor-blink"></span>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

function HomeView() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100%', textAlign: 'center', padding: '40px' }}>
      <pre style={{ color: 'var(--accent)', fontFamily: 'var(--font-mono)', lineHeight: 1.4, marginBottom: '24px', fontSize: '0.95rem', textShadow: '0 0 10px var(--accent-glow)' }}>
{`   *           .
.      .-.
    *  |o_o|         *
.       |:_/|
      * //   \\ \\   *
       (|     | )
.     /'\\_   _/'\\ .
      \\___)=(___/`}
      </pre>
      <h1 className="hero-title" style={{ fontSize: '2.2rem', marginBottom: '10px' }}>ORBE DE VERIX SOUL</h1>
      <h3 style={{ color: 'var(--text-secondary)', fontWeight: 300, marginBottom: '20px', fontSize: '1rem' }}>Creado por Richon · Arquitecto Cronos · v2.0 Rust Puro</h3>
      <p className="hero-subtitle" style={{ maxWidth: '500px', lineHeight: 1.8 }}>
        Motor criptográfico <strong>AES-256-CFB</strong> escrito en Rust nativo.<br />
        Todas las 9 funciones activas. Selecciona una opción del panel izquierdo.
      </p>
      <div style={{ display: 'flex', gap: '12px', marginTop: '24px', flexWrap: 'wrap', justifyContent: 'center' }}>
        {['Rust', 'AES-256', 'Vite', 'Axum', 'ZIP'].map(tag => (
          <span key={tag} style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--accent)', border: '1px solid var(--accent)', borderRadius: '20px', padding: '4px 14px', opacity: 0.7 }}>{tag}</span>
        ))}
      </div>
    </div>
  );
}

export default App;
