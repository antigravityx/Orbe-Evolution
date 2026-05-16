import { spawn } from "bun";
import { appendFileSync, readFileSync, writeFileSync } from "fs";

const logFile = "ovric_colmena.log";
const configFile = "ovric_config.json";

let currentConfig = { browser: "edge", editor: "vscode", gemini_key: "" };
try {
    const data = readFileSync(configFile, "utf8");
    currentConfig = JSON.parse(data);
} catch (e) {
    writeFileSync(configFile, JSON.stringify(currentConfig, null, 2));
}

function log(message: string) {
    const timestamp = new Date().toISOString();
    const formatted = `[${timestamp}] ${message}\n`;
    try {
        appendFileSync(logFile, formatted);
    } catch (e) {
        console.log("Error writing to log:", e);
    }
    console.log(formatted.trim());
}

log("==================================================");
log("[OVRIC] - INICIANDO SISTEMAS GLOBALES (COLMENA)");
log("==================================================");

const p1 = spawn({
    cmd: ["cargo", "run"],
    cwd: "Verix_NextGen_API",
    stdout: "pipe",
    stderr: "pipe",
});

const p2 = spawn({
    cmd: ["cargo", "run"],
    cwd: "Orbe-Dashboard/backend",
    stdout: "pipe",
    stderr: "pipe",
});

const p3 = spawn({
    cmd: ["cmd.exe", "/c", "npm run dev"],
    cwd: "Verix_NextGen",
    stdout: "pipe",
    stderr: "pipe",
});

const p4 = spawn({
    cmd: ["bun", "run", "dev"],
    cwd: "OVRIC-Nexus",
    stdout: "pipe",
    stderr: "pipe",
});

async function streamToLog(prefix: string, stream: any) {
    if (!stream) return;
    const reader = stream.getReader();
    const decoder = new TextDecoder();
    try {
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            for (const line of lines) {
                if (line.trim()) {
                    try {
                        appendFileSync(logFile, `[${prefix}] ${line}\n`);
                    } catch (e) {}
                }
            }
        }
    } catch (e) {
        log(`Error reading stream for ${prefix}: ${e}`);
    }
}

streamToLog("API-RUST", p1.stdout);
streamToLog("API-RUST-ERR", p1.stderr);
streamToLog("DASH-RUST", p2.stdout);
streamToLog("DASH-RUST-ERR", p2.stderr);
streamToLog("VITE-FRONT", p3.stdout);
streamToLog("VITE-FRONT-ERR", p3.stderr);
streamToLog("OVRIC-BUN", p4.stdout);
streamToLog("OVRIC-BUN-ERR", p4.stderr);

// Micro-servidor de configuración OVRIC
Bun.serve({
    port: 3050,
    async fetch(req) {
        if (req.method === "OPTIONS") {
            return new Response(null, {
                headers: {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
                    "Access-Control-Allow-Headers": "Content-Type",
                }
            });
        }
        
        const url = new URL(req.url);
        if (url.pathname === "/api/config") {
            if (req.method === "GET") {
                return new Response(JSON.stringify(currentConfig), {
                    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
                });
            }
            if (req.method === "POST") {
                try {
                    const body = await req.json();
                    currentConfig = { ...currentConfig, ...body };
                    writeFileSync(configFile, JSON.stringify(currentConfig, null, 2));
                    log(`Configuracion actualizada: Navegador -> ${currentConfig.browser}, Editor -> ${currentConfig.editor}, GeminiKey -> ${currentConfig.gemini_key ? 'SETEADA' : 'VACIA'}`);
                    return new Response(JSON.stringify({ status: "success", config: currentConfig }), {
                        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
                    });
                } catch (e) {
                    return new Response(JSON.stringify({ status: "error", message: String(e) }), {
                        status: 400,
                        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
                    });
                }
            }
        }

        if (url.pathname === "/api/chat" && req.method === "POST") {
            try {
                const { messages } = await req.json();
                const apiKey = currentConfig.gemini_key || process.env.GEMINI_API_KEY || "";
                
                if (!apiKey) {
                    return new Response(JSON.stringify({ 
                        role: "assistant", 
                        content: "⚠️ No se ha configurado la GEMINI_API_KEY. Por favor, sella tu llave en las variables de entorno para activar el Cerebro." 
                    }), { headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
                }

                // Micro-inteligencia: Llamada a Gemini Flash (rápido y eficiente)
                const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        contents: messages.filter((m: any) => m.role !== 'system').map((m: any) => ({
                            role: m.role === 'assistant' ? 'model' : 'user',
                            parts: [{ text: m.content }]
                        }))
                    })
                });

                const data: any = await response.json();
                const aiResponse = data.candidates?.[0]?.content?.parts?.[0]?.text || "Lo siento, la micro-inteligencia tuvo un problema de conexión.";

                return new Response(JSON.stringify({ role: "assistant", content: aiResponse }), {
                    headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
                });
            } catch (e) {
                 return new Response(JSON.stringify({ status: "error", message: String(e) }), {
                        status: 500,
                        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
                    });
            }
        }
        return new Response("Not Found", { status: 404 });
    }
});
log("Micro-servidor de configuracion iniciado en puerto 3050.");

log("Motores iniciados en segundo plano. Esperando 10 segundos para estabilizacion de puertos...");

setTimeout(() => {
    log("Lanzando OVRIC-Nexus PWA...");
    
    let pwaCmd = ["cmd.exe", "/c", "start msedge --app=http://localhost:5173"];
    
    if (currentConfig.browser === "chrome") {
        pwaCmd = ["cmd.exe", "/c", "start chrome --app=http://localhost:5173"];
    } else if (currentConfig.browser === "brave") {
        pwaCmd = ["cmd.exe", "/c", "start brave --app=http://localhost:5173"];
    } else if (currentConfig.browser === "default") {
        pwaCmd = ["cmd.exe", "/c", "start http://localhost:5173"];
    }
    
    const pwaProcess = spawn({
        cmd: pwaCmd,
        stdout: "ignore",
        stderr: "ignore",
    });

    log(`¡OVRIC-Nexus (Super Admin) esta completamente en linea! [Motor: ${currentConfig.browser}]`);
}, 10000);
