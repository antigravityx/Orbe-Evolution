import { invoke } from "@tauri-apps/api/core";

const btnNext = document.getElementById("btn-next") as HTMLButtonElement;
const depOllama = document.getElementById("dep-ollama");
const depRust = document.getElementById("dep-rust");

async function checkDependencies() {
  if (depOllama) {
    const hasOllama = await invoke<boolean>("check_ollama");
    const status = depOllama.querySelector(".dep-status");
    if (status) {
      status.textContent = hasOllama ? "✓ Instalado" : "✗ No encontrado";
      status.style.color = hasOllama ? "#00f0ff" : "#ff4b4b";
    }
  }

  if (depRust) {
    const hasRust = await invoke<boolean>("check_rust");
    const status = depRust.querySelector(".dep-status");
    if (status) {
      status.textContent = hasRust ? "✓ Instalado" : "✗ No encontrado";
      status.style.color = hasRust ? "#00f0ff" : "#ff4b4b";
    }
  }

  if (btnNext) {
    btnNext.disabled = false;
    btnNext.textContent = "Despertar Alma";
  }
}

window.addEventListener("DOMContentLoaded", () => {
  setTimeout(checkDependencies, 1500); // Pequeño delay para el efecto visual
});

btnNext?.addEventListener("click", () => {
  alert("Iniciando secuencia de despertar... ∞");
});
