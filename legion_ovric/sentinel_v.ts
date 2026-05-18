import { spawn } from "bun";

/**
 * 🛡️ SOLDADO SENTINEL-V
 * Misión: Vigilancia y Mantenimiento del Virtualizador V-ORBE
 */

class SentinelV {
    private boxPath: string = "C:\\Users\\Usuario\\Desktop\\Taller_Orbe_Verix\\orbe\\virtual_boxes";

    async start() {
        console.log("🛡️ [SENTINEL-V] Desplegado. Vigilando cajas virtuales...");
        
        // Ciclo de mantenimiento cada 30 segundos
        setInterval(() => this.purgeOrphanBoxes(), 30000);
    }

    private async purgeOrphanBoxes() {
        console.log("🔍 [SENTINEL-V] Escaneando cajas inactivas...");
        // Lógica para detectar si una caja ya no tiene procesos asociados
        // Por ahora, simplemente nos aseguramos de que el directorio base exista
        const cmd = spawn(["cmd", "/c", "dir", this.boxPath]);
        const output = await new Response(cmd.stdout).text();
        
        if (output.includes("no se encuentra")) {
            console.log("⚠️ [SENTINEL-V] Directorio de cajas no encontrado. Creando...");
            spawn(["cmd", "/c", "mkdir", this.boxPath]);
        }
    }
}

const sentinel = new SentinelV();
sentinel.start();
