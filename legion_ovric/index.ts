/**
 * ⌬ OVRIC LEGION MASTER
 * Coordinador de la Colmena de Legionarios.
 * Escrito en Bun (TypeScript) para maxima eficiencia.
 */

console.log(`
  ██████╗ ██╗   ██╗██████╗ ██╗ ██████╗ 
 ██╔═══██╗██║   ██║██╔══██╗██║██╔════╝ 
 ██║   ██║██║   ██║██████╔╝██║██║      
 ██║   ██║╚██╗ ██╔╝██╔══██╗██║██║      
 ╚██████╔╝ ╚████╔╝ ██║  ██║██║╚██████╗ 
  ╚═════╝   ╚═══╝  ╚═╝  ╚═╝╚═╝ ╚═════╝ 
  COLMENA DE INTELIGENCIA ACTIVA
`);

import { spawn } from "bun";

async function wakeUpLegion() {
  console.log("🚀 Despertando a la Legion Recordadora...");

  // Iniciar Legionario SHIELD
  const shield = spawn(["bun", "shield.ts"], {
    stdout: "inherit",
    stderr: "inherit"
  });

  console.log("🛡️  Legionario SHIELD en posicion.");

  // Iniciar Legionario PSYCHE (Python)
  const psyche = spawn(["python", "psyche.py"], {
    stdout: "inherit",
    stderr: "inherit"
  });

  console.log("🧠 Legionario PSYCHE en posicion.");
  
  // Aqui podriamos añadir mas legionarios (CHRONOS, etc.)
  console.log("👁️  Legion en linea. Vigilando la existencia de r1ch0n.");
}

wakeUpLegion();
