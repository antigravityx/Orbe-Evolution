import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './App.css';

interface MenuOption {
  id: number;
  title: string;
  description: string;
  type?: 'primary' | 'secondary' | 'danger';
}

const MENU_OPTIONS: MenuOption[] = [
  { id: 1, title: 'Crear Cápsula', description: 'Sella un archivo o carpeta en una cápsula encriptada.', type: 'primary' },
  { id: 2, title: 'Invocar Alma', description: 'Libera el contenido de una cápsula en el Santuario.', type: 'primary' },
  { id: 3, title: 'Gestor de Almas (Git)', description: 'Administra y encapsula proyectos desde repositorios Git.', type: 'secondary' },
  { id: 4, title: 'Gestor de Cápsulas', description: 'Administra las cápsulas que has creado.', type: 'secondary' },
  { id: 5, title: 'Integridad y Criptografía', description: 'Accede a los poderes de firma, verificación y logs.', type: 'secondary' },
  { id: 6, title: 'Nido del HumanoDev', description: 'Entra a tu espacio sagrado para que el orbe aprenda de ti.', type: 'primary' },
  { id: 7, title: 'Navegador del Santuario', description: 'Explora la estructura completa del Orbe.', type: 'secondary' },
  { id: 8, title: 'Modo Sueño', description: 'Controla el ciclo REM y el senado de los Sueños.', type: 'primary' },
  { id: 9, title: 'Cerebro Orbe', description: 'Gestiona la vigilancia y la agenda automática.', type: 'secondary' },
  { id: 10, title: 'Salir del Orbe', description: 'Cierra la conexión con el orbe de forma segura.', type: 'danger' },
];

function App() {
  const [activeLog, setActiveLog] = useState<string>('INICIANDO LATIDO ETERNO (SINCRONIZACIÓN)...\\n[OK] FORJA asegurado en el Éter.\\n--- LATIDO COMPLETADO ---');

  const handleAction = async (option: MenuOption) => {
    setActiveLog(prev => `${prev}\n> Ejecutando: ${option.title}...\n[!] Conectando con núcleo Rust/Python...`);
    try {
      const response = await invoke('execute_action', { actionId: option.id });
      setActiveLog(prev => `${prev}\n${response}`);
    } catch (e) {
      setActiveLog(prev => `${prev}\n[ERROR]: ${e}`);
    }
  };

  return (
    <div className="app-container">
      <header className="app-header glass-panel">
        <div className="logo-container">
          <pre className="ascii-art text-glow">
{`   .       .
  *   |o_o|
    |:_/|
  *  //   \\\\  *
   (|     |)
  / \\_   _/ \\
  \\___)=(___/  .`}
          </pre>
          <div>
            <h1 className="title glitch-effect">ORBE DE VERIX SOUL</h1>
            <p className="subtitle">Creado por Richon, Arquitecto Cronos</p>
          </div>
        </div>
      </header>

      <main className="main-content">
        <section className="terminal-log glass-panel">
          <div className="terminal-header">
            <span className="dot dot-red"></span>
            <span className="dot dot-yellow"></span>
            <span className="dot dot-green"></span>
            <span className="terminal-title">Terminal de Sistema</span>
          </div>
          <div className="terminal-body">
            <pre>{activeLog}</pre>
            <div className="cursor-blink">_</div>
          </div>
        </section>

        <section className="control-panel">
          <h2 className="panel-title">¿Qué deseas hacer ahora, Richon?</h2>
          <div className="grid-container">
            {MENU_OPTIONS.map((option) => (
              <div key={option.id} className="card glass-panel" onClick={() => handleAction(option)}>
                <div className={`card-number text-${option.type || 'primary'}`}>
                  {option.id < 10 ? `0${option.id}` : option.id}
                </div>
                <div className="card-content">
                  <h3>{option.title}</h3>
                  <p>{option.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
