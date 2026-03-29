import { invoke } from "@tauri-apps/api/core";

// DOM Elements
const viewIntro = document.getElementById("view-intro");
const dialogText = document.getElementById("dialog-text");
const quickSurvey = document.getElementById("quick-survey");
const userRoleInput = document.getElementById("user-role-input") as HTMLInputElement;
const btnNextRole = document.getElementById("btn-next-role");

const viewEula = document.getElementById("view-eula");
const signatureInput = document.getElementById("signature-input") as HTMLInputElement;
const btnSignPact = document.getElementById("btn-sign-pact");

const viewDashboard = document.getElementById("view-dashboard");
const dashboardTitle = document.getElementById("dashboard-title");
const btnMinimizeTray = document.getElementById("btn-minimize-tray");

// Variables
let userName = "Invitado";

// Secuencia de entrada (Dialogos Livianos)
function startIntro() {
  setTimeout(() => {
    if(dialogText && quickSurvey) {
      dialogText.innerHTML = "He despertado. ¿Qué clase de constructor guiará mis hilos hoy?";
      quickSurvey.classList.remove("hidden");
    }
  }, 2000);
}

btnNextRole?.addEventListener("click", () => {
  const role = userRoleInput?.value.trim();
  if (role) {
    if(dialogText && quickSurvey) {
      quickSurvey.classList.add("hidden");
      dialogText.innerHTML = `Comprendo. Un <span class="highlight">${role}</span> requiere herramientas específicas. Me adaptaré en silencio.`;
      
      setTimeout(() => {
        // Transición a EULA
        viewIntro?.classList.add("hidden");
        viewEula?.classList.remove("hidden");
      }, 2500);
    }
  }
});

btnSignPact?.addEventListener("click", () => {
  userName = signatureInput?.value.trim();
  if (userName) {
    // Aquí es donde en el futuro llamaríamos a un invoke de Tauri para escalar permisos o loggear firma
    // await invoke("sign_pact", { name: userName });
    
    viewEula?.classList.add("hidden");
    viewDashboard?.classList.remove("hidden");
    
    if(dashboardTitle) {
      dashboardTitle.innerHTML = `Orbe de <span class="highlight">${userName}</span>`;
    }
  }
});

btnMinimizeTray?.addEventListener("click", async () => {
    try {
        // Obtenemos si estamos en Tauri o en el Navegador
        if ((window as any).__TAURI__) {
            await invoke("hide_to_tray");
        } else {
            alert("✨ Estás en el modo Web (Vivaldi). El modo 'Guardián Silencioso' (Minimizar) está disponible únicamente en la aplicación instalada nativa de Windows/Linux/Móvil. ¡Tu botón funciona perfecto en la versión instalable!");
        }
    } catch (e) {
        console.error("Error al minimizar: ", e);
    }
});

window.addEventListener("DOMContentLoaded", () => {
  startIntro();
});
