import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";

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

// Elementos del Dashboard
const cpuText = document.getElementById("cpu-text");
const ramText = document.getElementById("ram-text");
const healthText = document.getElementById("health-text");
const soldiersText = document.getElementById("soldiers-text");
const cpuRing = document.querySelector(".cpu-ring") as SVGCircleElement;
const ramRing = document.querySelector(".ram-ring") as SVGCircleElement;
const healthRing = document.querySelector(".health-ring") as SVGCircleElement;

function setRingProgress(ring: SVGCircleElement, percent: number) {
  if (!ring) return;
  const radius = ring.r.baseVal.value;
  const circumference = radius * 2 * Math.PI;
  ring.style.strokeDasharray = `${circumference} ${circumference}`;
  const offset = circumference - (percent / 100) * circumference;
  ring.style.strokeDashoffset = offset.toString();
}

async function updateTelemetry() {
  try {
    const jsonStr: string = await invoke("obtener_telemetria");
    const data = JSON.parse(jsonStr);
    
    if (cpuText) cpuText.textContent = `${data.cpu.toFixed(0)}%`;
    setRingProgress(cpuRing, data.cpu);
    
    const ramUsedGB = (data.ram_used / 1e9).toFixed(1);
    const ramTotalGB = (data.ram_total / 1e9).toFixed(1);
    if (ramText) ramText.textContent = `${ramUsedGB} / ${ramTotalGB}G`;
    setRingProgress(ramRing, (data.ram_used / data.ram_total) * 100);
  } catch(e) {
    console.error("Telemetry error", e);
  }
}

async function updateOrbeHealth() {
  try {
    const jsonStr: string = await invoke("leer_estado_orbe");
    const data = JSON.parse(jsonStr);
    
    if (healthText) healthText.textContent = `${data.score_salud}%`;
    setRingProgress(healthRing, data.score_salud);
    
    if (soldiersText) soldiersText.textContent = `Soldados: ${data.soldados_activos}/${data.soldados_activos + data.soldados_falla}`;
    
    // Cambiar color basado en la salud
    if (healthRing) {
      if (data.score_salud >= 85) healthRing.style.stroke = "var(--accent-cyan)";
      else if (data.score_salud >= 50) healthRing.style.stroke = "orange";
      else healthRing.style.stroke = "var(--accent-magenta)";
    }
  } catch(e) {
    console.error("Orbe health error", e);
  }
}

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

// Botones de Ventana
const btnMinimize = document.getElementById("btn-minimize");
const btnClose = document.getElementById("btn-close");
const btnPin = document.getElementById("btn-pin");

if (btnMinimize) {
  btnMinimize.addEventListener("click", () => getCurrentWindow().minimize());
}

if (btnClose) {
  btnClose.addEventListener("click", () => getCurrentWindow().close());
}

let isPinned = false;
if (btnPin) {
  btnPin.addEventListener("click", async () => {
    isPinned = !isPinned;
    await getCurrentWindow().setAlwaysOnTop(isPinned);
    if (isPinned) {
      btnPin.classList.add("active");
    } else {
      btnPin.classList.remove("active");
    }
  });
}

// Redacción de Sueños
const btnToggleForm = document.getElementById("btn-toggle-form");
const formContainer = document.getElementById("dream-form-container");
const inputAsunto = document.getElementById("input-asunto") as HTMLInputElement;
const inputDesc = document.getElementById("input-desc") as HTMLTextAreaElement;
const btnSubmitDream = document.getElementById("btn-submit-dream");

if (btnToggleForm && formContainer) {
  btnToggleForm.addEventListener("click", () => {
    formContainer.classList.toggle("collapsed");
    if (!formContainer.classList.contains("collapsed")) {
      inputAsunto?.focus();
    }
  });
}

if (btnSubmitDream && inputAsunto && inputDesc) {
  btnSubmitDream.addEventListener("click", async () => {
    const asunto = inputAsunto.value.trim();
    const desc = inputDesc.value.trim();
    
    if (!asunto || !desc) {
      alert("Debes escribir un asunto y una historia.");
      return;
    }
    
    try {
      btnSubmitDream.textContent = "Sincronizando...";
      await invoke("registrar_sueno", { asunto: asunto, descripcion: desc });
      
      // Limpiar formulario y recargar
      inputAsunto.value = "";
      inputDesc.value = "";
      formContainer?.classList.add("collapsed");
      btnSubmitDream.textContent = "Registrar en el Orbe";
      
      loadDreams();
    } catch (e) {
      alert("Error guardando el sueño: " + e);
      btnSubmitDream.textContent = "Registrar en el Orbe";
    }
  });
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
  updateTelemetry();
  updateOrbeHealth();
  
  // Auto-refresh de sueños
  setInterval(loadDreams, 30000);
  
  // Telemetría rápida (1s)
  setInterval(updateTelemetry, 1000);
  
  // Salud del orbe (5s)
  setInterval(updateOrbeHealth, 5000);
});
