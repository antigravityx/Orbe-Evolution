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
    try {
      const payload = {
        id: `shield_scan_${Date.now()}`,
        content: `SHIELD Scan: ${data.split('\n').filter(l => l.trim()).slice(1).join(' | ')}`,
        type: "system_scan",
        connect_to: "shield-01",
        weight: 0.8
      };
      
      console.log(`🧠 Reportando hallazgos al Hipocampo...`);
      const res = await fetch("http://127.0.0.1:3030/api/hipocampo/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      
      if (res.ok) {
        console.log("✅ Memoria sincronizada.");
      }
    } catch (err) {
      console.error("❌ Fallo en el reporte neuronal:", err);
    }
  }
}

new ShieldLegionnaire();
