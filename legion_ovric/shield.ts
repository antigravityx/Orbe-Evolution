/**
 * 🛡️ LEGIONARIO SHIELD (v1.0)
 * Soldado de la Legion OVRIC.
 * Especialidad: Reconocimiento de Procesos y Escaneo de Esencias.
 */

import { spawn } from "child_process";

class ShieldLegionnaire {
  private id: string = "SHIELD-01";
  private scanInterval: number = 10000; // 10 segundos

  constructor() {
    console.log(`\n⌬ [OVRIC] Legionario ${this.id} despertando...`);
    this.startMission();
  }

  private async startMission() {
    console.log(`🛡️  Mision: Escaneo de esencias del sistema activa.`);
    
    setInterval(async () => {
      console.log(`\n🔍 [${new Date().toLocaleTimeString()}] Escaneando procesos activos...`);
      const processes = await this.getSystemProcesses();
      this.analyzeEsences(processes);
    }, this.scanInterval);
  }

  private getSystemProcesses(): Promise<string> {
    return new Promise((resolve) => {
      // Usamos PowerShell para listar procesos en Windows
      const ps = spawn("powershell", ["Get-Process | Select-Object Name, CPU, WorkingSet | Sort-Object CPU -Descending | Select-Object -First 5"]);
      let output = "";
      ps.stdout.on("data", (data) => (output += data));
      ps.on("close", () => resolve(output));
    });
  }

  private analyzeEsences(data: string) {
    console.log("📊 Esencias detectadas (Top 5 CPU):");
    console.log(data);

    // Aquí conectaríamos con el Hipocampo via API
    this.reportToHipocampo(data);
  }

  private async reportToHipocampo(data: string) {
    // Simulacion de reporte al Hipocampo
    try {
      const event = {
        id: `scan_${Date.now()}`,
        content: `Escaneo de SHIELD: ${data.split('\n')[1] || "Sin datos"}`,
        type: "system_scan"
      };
      
      console.log(`🧠 Enviando reporte al Hipocampo...`);
      // fetch("http://127.0.0.1:3030/api/hipocampo/register", ...)
    } catch (err) {
      console.error("❌ Error en la conexion neuronal.");
    }
  }
}

new ShieldLegionnaire();
