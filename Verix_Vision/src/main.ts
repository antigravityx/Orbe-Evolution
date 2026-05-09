import { invoke } from "@tauri-apps/api/core";
import { getCurrentWindow } from "@tauri-apps/api/window";

interface Dream {
  id: string;
  fecha: string;
  asunto: string;
  descripcion: string;
  aprobado: boolean;
  realidad?: boolean;
}

// Elementos de UI
const dreamsList = document.getElementById("dreams-list");
const statusText = document.getElementById("status");
const btnRefresh = document.getElementById("btn-refresh");

const cpuText = document.getElementById("cpu-text");
const ramText = document.getElementById("ram-text");
const diskText = document.getElementById("disk-text");
const healthText = document.getElementById("health-text");

const cpuRing = document.querySelector(".cpu-ring") as SVGCircleElement;
const ramRing = document.querySelector(".ram-ring") as SVGCircleElement;
const diskRing = document.querySelector(".disk-ring") as SVGCircleElement;
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
    
    const ramPct = (data.ram_used / data.ram_total) * 100;
    if (ramText) ramText.textContent = `${(data.ram_used / 1e9).toFixed(1)}G`;
    setRingProgress(ramRing, ramPct);

    const diskPct = (data.disk_used / data.disk_total) * 100;
    if (diskText) diskText.textContent = `${diskPct.toFixed(0)}%`;
    setRingProgress(diskRing, diskPct);
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
    
    // Actualizar lista de soldados si estamos en la pestaña Batallón
    const soldiersList = document.getElementById("soldiers-list");
    if (soldiersList && document.getElementById("tab-battalion")?.classList.contains("active")) {
      soldiersList.innerHTML = "";
      
      const soldados = data.soldados;
      Object.keys(soldados).forEach(key => {
        const s = soldados[key];
        const row = document.createElement("div");
        row.className = `soldier-row ${s.critico ? 'critical' : ''}`;
        row.innerHTML = `
          <div class="soldier-info">
            <span class="soldier-name">${key}</span>
            <span class="soldier-role">${s.rol}</span>
          </div>
          <span class="soldier-status ${s.estado.toLowerCase()}">${s.estado.toUpperCase()}</span>
        `;
        soldiersList.appendChild(row);
      });
    }

    if (healthRing) {
      if (data.score_salud >= 85) healthRing.style.stroke = "#00f0ff";
      else if (data.score_salud >= 50) healthRing.style.stroke = "orange";
      else healthRing.style.stroke = "#ff003c";
    }
  } catch(e) {
    console.error("Orbe health error", e);
  }
}

async function loadDreams() {
  if (!dreamsList || !statusText) return;
  try {
    const jsonStr: string = await invoke("leer_suenos");
    let dreams: Dream[] = JSON.parse(jsonStr);
    dreamsList.innerHTML = "";
    
    dreams.sort((a, b) => (a.realidad === b.realidad ? 0 : a.realidad ? 1 : -1));
    
    dreams.forEach(dream => {
      const card = document.createElement("div");
      card.className = `dream-card ${dream.realidad ? 'reality' : (dream.aprobado ? 'approved' : '')}`;
      const badge = dream.realidad ? '🌍 REALIDAD' : (dream.aprobado ? '✨ REVELADO' : '💭 EN COLCHÓN');
      
      card.innerHTML = `
        <div class="dream-header">
          <div class="dream-id">${dream.id} - ${badge}</div>
          ${!dream.realidad ? `<button class="btn-make-reality" data-id="${dream.id}">⚡</button>` : ''}
        </div>
        <div class="dream-title">${dream.asunto}</div>
        <div class="dream-desc">${dream.descripcion}</div>
        <div class="dream-date">${dream.fecha}</div>
      `;
      dreamsList.appendChild(card);
    });

    document.querySelectorAll(".btn-make-reality").forEach(btn => {
      btn.addEventListener("click", async (e) => {
        const id = (e.currentTarget as HTMLElement).dataset.id;
        if (id) {
          await invoke("marcar_realidad", { id });
          loadDreams();
        }
      });
    });
    statusText.textContent = `Vigilia. ${dreams.length} sueños encontrados.`;
  } catch (error) {
    console.error("Error cargando sueños:", error);
    statusText.textContent = "Error de conexión.";
  }
}

// Ventana y Atajos
const btnMinimize = document.getElementById("btn-minimize");
const btnMaximize = document.getElementById("btn-maximize");
const btnClose = document.getElementById("btn-close");
const btnPin = document.getElementById("btn-pin");
let isPinned = false;
btnPin?.addEventListener("click", async () => {
  isPinned = !isPinned;
  await getCurrentWindow().setAlwaysOnTop(isPinned);
  btnPin.classList.toggle("active", isPinned);
});

btnMinimize?.addEventListener("click", async () => {
  console.log("[Verix] Minimizando ventana...");
  await getCurrentWindow().minimize();
});
btnMaximize?.addEventListener("click", async () => {
  console.log("[Verix] Maximizando/Restaurando ventana...");
  const win = getCurrentWindow();
  if (await win.isMaximized()) await win.unmaximize();
  else await win.maximize();
});
btnClose?.addEventListener("click", async () => {
  console.log("[Verix] Cerrando sesión...");
  await getCurrentWindow().close();
});

window.addEventListener("keydown", async (e) => {
  // Evitar atajos si se está escribiendo en el terminal
  if (document.activeElement?.id === 'console-input') return;

  // Atajos de Sistema / UI (Estilo Adobe)
  if (e.altKey && e.key.toLowerCase() === "z") {
    e.preventDefault();
    await getCurrentWindow().minimize();
  }
  if (e.altKey && e.key.toLowerCase() === "x") {
    e.preventDefault();
    await getCurrentWindow().close();
  }
  if (e.altKey && e.key.toLowerCase() === "m") {
    e.preventDefault();
    const win = getCurrentWindow();
    const isMaximized = await win.isMaximized();
    if (isMaximized) await win.unmaximize();
    else await win.maximize();
  }

  // Atajos personalizados para la App de Sueños
  if (e.ctrlKey && e.key.toLowerCase() === "n") {
    e.preventDefault();
    const formContainer = document.getElementById("dream-form-container");
    formContainer?.classList.toggle("collapsed");
    document.getElementById("input-asunto")?.focus();
    console.log("[Orbe] Atajo: Nuevo Sueño");
  }

  if (e.ctrlKey && e.key.toLowerCase() === "c") {
    // Si no hay texto seleccionado, copiar el ID del último sueño
    if (!window.getSelection()?.toString()) {
      const firstDream = document.querySelector(".dream-card .dream-id")?.textContent;
      if (firstDream) {
        navigator.clipboard.writeText(firstDream);
        console.log("[Orbe] Copiado ID de sueño:", firstDream);
      }
    }
  }

  if (e.ctrlKey && e.key.toLowerCase() === "v") {
    // Pegar contenido en el formulario si está abierto
    const formContainer = document.getElementById("dream-form-container");
    if (formContainer && !formContainer.classList.contains("collapsed")) {
       console.log("[Orbe] Atajo: Pegar en Sueños");
    }
  }
});

// Sistema de Páginas (Sidebar)
document.querySelectorAll(".nav-item").forEach(btn => {
  btn.addEventListener("click", () => {
    const page = (btn as HTMLElement).dataset.page;
    document.querySelectorAll(".nav-item").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".page").forEach(c => c.classList.remove("active"));
    
    btn.classList.add("active");
    document.getElementById(`page-${page}`)?.classList.add("active");
    
    if (page === "dreams") loadDreams();
    if (page === "battalion") updateOrbeHealth();
  });
});

// Formulario de Sueños
const btnToggleForm = document.getElementById("btn-toggle-form");
const formContainer = document.getElementById("dream-form-container");
const btnSubmitDream = document.getElementById("btn-submit-dream");

btnToggleForm?.addEventListener("click", () => {
  formContainer?.classList.toggle("collapsed");
});

btnSubmitDream?.addEventListener("click", async () => {
  const asunto = (document.getElementById("input-asunto") as HTMLInputElement).value;
  const desc = (document.getElementById("input-desc") as HTMLTextAreaElement).value;
  
  if (asunto && desc) {
    await invoke("registrar_sueno", { asunto, descripcion: desc });
    formContainer?.classList.add("collapsed");
    loadDreams();
  }
});

btnRefresh?.addEventListener("click", loadDreams);

// ════════════════════════════════════════
//   ORBE-CONSOLE
// ════════════════════════════════════════
const consoleOutput   = document.getElementById("console-output") as HTMLDivElement;
const consoleInput    = document.getElementById("console-input") as HTMLInputElement;
const btnConsoleRun   = document.getElementById("btn-console-run");
const btnConsoleClear = document.getElementById("btn-console-clear");
const btnConsoleHelp  = document.getElementById("btn-console-help");

let cmdHistory: string[] = [];
let historyIndex = -1;

function appendConsoleLine(text: string, type: "cmd" | "out" | "err" | "sys" = "out") {
  if (!consoleOutput) return;
  const lines = text.split("\n");
  lines.forEach(line => {
    const div = document.createElement("div");
    div.className = `console-line console-${type}`;
    if (type === "cmd") {
      div.innerHTML = `<span class="console-prompt-label">r1ch0n@orbe:~$</span> <span>${escapeHtml(line)}</span>`;
    } else {
      div.textContent = line;
    }
    consoleOutput.appendChild(div);
  });
  consoleOutput.scrollTop = consoleOutput.scrollHeight;
}

function escapeHtml(str: string) {
  return str.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

async function runConsoleCommand(cmd: string) {
  const trimmed = cmd.trim();
  if (!trimmed) return;

  // Historial
  cmdHistory.unshift(trimmed);
  if (cmdHistory.length > 100) cmdHistory.pop();
  historyIndex = -1;

  appendConsoleLine(trimmed, "cmd");

  try {
    const result: string = await invoke("ejecutar_comando", { comando: trimmed });
    if (result === "CLEAR_TERMINAL") {
      if (consoleOutput) consoleOutput.innerHTML = "";
      appendConsoleLine("Pantalla limpiada.", "sys");
    } else if (result.trim()) {
      appendConsoleLine(result, "out");
    }
  } catch (err: any) {
    appendConsoleLine(`ERROR: ${err}`, "err");
  }
}

btnConsoleRun?.addEventListener("click", async () => {
  const cmd = consoleInput?.value ?? "";
  consoleInput.value = "";
  await runConsoleCommand(cmd);
});

consoleInput?.addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    const cmd = consoleInput.value;
    consoleInput.value = "";
    await runConsoleCommand(cmd);
  }
  // Historial con flechas
  if (e.key === "ArrowUp") {
    e.preventDefault();
    if (historyIndex < cmdHistory.length - 1) {
      historyIndex++;
      consoleInput.value = cmdHistory[historyIndex];
    }
  }
  if (e.key === "ArrowDown") {
    e.preventDefault();
    if (historyIndex > 0) {
      historyIndex--;
      consoleInput.value = cmdHistory[historyIndex];
    } else {
      historyIndex = -1;
      consoleInput.value = "";
    }
  }
});

btnConsoleClear?.addEventListener("click", () => {
  if (consoleOutput) consoleOutput.innerHTML = "";
  appendConsoleLine("Orbe-Console lista.", "sys");
});

btnConsoleHelp?.addEventListener("click", async () => {
  await runConsoleCommand("orbe --help");
});

// Auto-focus al cambiar a la pestaña terminal
document.querySelectorAll(".tab-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const tab = (btn as HTMLElement).dataset.tab;
    if (tab === "terminal") {
      setTimeout(() => consoleInput?.focus(), 100);
    }
  });
});

// Inicio
window.addEventListener("DOMContentLoaded", () => {
  loadDreams();
  updateTelemetry();
  updateOrbeHealth();
  setInterval(updateTelemetry, 1000);
  setInterval(updateOrbeHealth, 5000);
});
