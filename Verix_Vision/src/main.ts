import { invoke } from "@tauri-apps/api/core";

interface Dream {
  id: string;
  fecha: string;
  asunto: string;
  descripcion: string;
  aprobado: boolean;
}

const dreamsList = document.getElementById("dreams-list");
const statusText = document.getElementById("status");
const btnRefresh = document.getElementById("btn-refresh");

async function loadDreams() {
  if (!dreamsList || !statusText) return;
  
  try {
    statusText.textContent = "Sincronizando con el Orbe...";
    
    // Llamar al comando de Rust
    const jsonStr: string = await invoke("leer_suenos");
    const dreams: Dream[] = JSON.parse(jsonStr);
    
    dreamsList.innerHTML = "";
    
    if (dreams.length === 0) {
      dreamsList.innerHTML = `<div class="dream-card loading"><p>El Orbe no tiene sueños registrados aún.</p></div>`;
      statusText.textContent = "Orbe en reposo.";
      return;
    }
    
    dreams.forEach(dream => {
      const card = document.createElement("div");
      card.className = `dream-card ${dream.aprobado ? 'approved' : ''}`;
      
      const badge = dream.aprobado ? '✨ Revelado' : '💭 En Colchón';
      
      card.innerHTML = `
        <div class="dream-id">${dream.id} - ${badge}</div>
        <div class="dream-title">${dream.asunto}</div>
        <div class="dream-desc">${dream.descripcion}</div>
        <div class="dream-date">${dream.fecha}</div>
      `;
      dreamsList.appendChild(card);
    });
    
    statusText.textContent = `Vigilia. ${dreams.length} sueños encontrados.`;
  } catch (error) {
    console.error("Error cargando sueños:", error);
    dreamsList.innerHTML = `
      <div class="dream-card" style="border-left-color: red;">
        <p style="color: red;">Error crítico al leer los sueños del Orbe.</p>
        <p style="font-size: 0.8rem; margin-top: 10px;">${error}</p>
      </div>
    `;
    statusText.textContent = "Error de conexión.";
  }
}

if (btnRefresh) {
  btnRefresh.addEventListener("click", () => {
    dreamsList!.innerHTML = `<div class="dream-card loading"><p>Sincronizando...</p></div>`;
    setTimeout(loadDreams, 500); // Pequeño delay visual
  });
}

// Cargar al inicio
window.addEventListener("DOMContentLoaded", () => {
  loadDreams();
  
  // Auto-refresh cada 30 segundos
  setInterval(loadDreams, 30000);
});
