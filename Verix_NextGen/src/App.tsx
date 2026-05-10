import { useState, useEffect } from 'react';
import './App.css';

interface MenuOption {
  id: number;
  title: string;
  description: string;
}

const MENU_OPTIONS: MenuOption[] = [
  { id: 1, title: 'Crear Cápsula', description: 'Sella un archivo o carpeta en una cápsula encriptada.' },
  { id: 2, title: 'Invocar Alma', description: 'Libera el contenido de una cápsula en el Santuario.' },
  { id: 3, title: 'Gestor de Almas (Git)', description: 'Administra y encapsula proyectos desde repositorios Git.' },
  { id: 4, title: 'Gestor de Cápsulas', description: 'Administra las cápsulas que has creado.' },
  { id: 5, title: 'Integridad y Criptografía', description: 'Accede a los poderes de firma, verificación y logs.' },
  { id: 6, title: 'Nido del HumanoDev', description: 'Entra a tu espacio sagrado para que el orbe aprenda de ti.' },
  { id: 7, title: 'Navegador del Santuario', description: 'Explora la estructura completa del Orbe.' },
  { id: 8, title: 'Modo Sueño', description: 'Controla el ciclo REM y el senado de los Sueños.' },
  { id: 9, title: 'Cerebro Orbe', description: 'Gestiona la vigilancia y la agenda automática.' },
  { id: 10, title: 'Salir del Orbe', description: 'Cierra la conexión con el orbe de forma segura.' },
];

function App() {
  const [activeLog, setActiveLog] = useState<string[]>([
    '[SYSTEM] Inicializando núcleo Verix NextGen...',
    '[OK] Conexión establecida con el Éter.',
    'Esperando instrucciones del Arquitecto...'
  ]);
  const [theme, setTheme] = useState<string>('dark');
  const [activeItem, setActiveItem] = useState<number | null>(null);

  useEffect(() => {
    document.body.setAttribute('data-theme', theme);
  }, [theme]);

  const handleAction = async (option: MenuOption) => {
    setActiveItem(option.id);
    setActiveLog(prev => [...prev, `> Ejecutando: ${option.title}...`, '[!] Contactando a la API de Rust...']);
    try {
      const res = await fetch(`http://localhost:3000/api/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ actionId: option.id })
      });
      const data = await res.json();
      setActiveLog(prev => [...prev, data.message]);
    } catch (e) {
      setActiveLog(prev => [...prev, `[ERROR]: No se pudo conectar a la API de Rust (¿Está corriendo en el puerto 3000?)`]);
    }
  };

  return (
    <div className="layout-container animate-fade-in">
      
      {/* Sidebar Navigation */}
      <aside className="sidebar glass">
        <div className="brand">
          <div className="brand-title">
            <div className="brand-indicator"></div>
            Verix Soul
          </div>
          <select 
            className="theme-select"
            value={theme} 
            onChange={(e) => setTheme(e.target.value)}
          >
            <option value="dark">Dark (Modern)</option>
            <option value="stealth">Stealth (Green)</option>
            <option value="light">Light (Clean)</option>
          </select>
        </div>

        <nav className="menu-list">
          {MENU_OPTIONS.map((option) => (
            <button 
              key={option.id} 
              className={`menu-item ${activeItem === option.id ? 'active' : ''}`}
              onClick={() => handleAction(option)}
            >
              <span className="menu-item-title">{option.title}</span>
              <span className="menu-item-desc">{option.description}</span>
            </button>
          ))}
        </nav>
      </aside>

      {/* Main Content Area */}
      <main className="main-area">
        <section className="hero-section">
          <h1 className="hero-title">Orbe Architecture</h1>
          <p className="hero-subtitle">
            Gestión avanzada de cápsulas, criptografía y sincronización del ecosistema Verix. 
            Ahora potenciado por Rust y Vite para un rendimiento nativo.
          </p>
        </section>

        <section className="terminal-wrapper glass">
          <div className="terminal-header">
            <div className="terminal-dots">
              <div className="tdot"></div>
              <div className="tdot"></div>
              <div className="tdot"></div>
            </div>
            <span className="terminal-title">~/verix-core/output</span>
          </div>
          <div className="terminal-body">
            {activeLog.map((log, index) => (
              <div key={index} className="terminal-line">
                <span className="terminal-prefix">➜</span>
                <span>{log}</span>
              </div>
            ))}
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

export default App;
