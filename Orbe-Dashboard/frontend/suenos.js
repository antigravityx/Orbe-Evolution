const API_URL = 'http://127.0.0.1:3030/api/dreams';
const LOCAL_JSON = './dreams.json';
const CONTAINER = document.getElementById('dreams-container');
const STATUS_DOT = document.getElementById('backend-status');
const STATUS_TEXT = document.getElementById('status-text');
const REM_COUNT = document.getElementById('rem-count');
const DREAM_COUNT = document.getElementById('dream-count');

let prevDreams = [];

async function fetchDreams() {
    const isLive = window.location.hostname.includes('github.io');
    
    try {
        let response = null;
        
        // Solo intentar API Local si no estamos en modo Live o si queremos forzarlo
        if (!isLive) {
            response = await fetch(API_URL).catch(() => null);
        }
        
        // Si estamos en Live o falló la API local, usar el JSON estático
        if (!response || !response.ok) {
            response = await fetch(LOCAL_JSON + "?t=" + Date.now());
            updateStatus(true, isLive ? "MODO DIOS (Live)" : "Modo Offline");
        } else {
            updateStatus(true, "Conectado al Alma (Local)");
        }

        if (!response.ok) throw new Error('No Data');
        
        const dreams = await response.json();
        renderDreams(dreams);
    } catch (err) {
        console.error('Fetch error:', err);
        updateStatus(false, "Desconectado (Esperando Orbe)");
    }
}

function updateStatus(online, text) {
    if (online) {
        STATUS_DOT.className = 'status-dot online';
        STATUS_TEXT.innerText = text;
    } else {
        STATUS_DOT.className = 'status-dot offline';
        STATUS_TEXT.innerText = text;
    }
}


function renderDreams(dreams) {
    // Sort by ID (usually date-based in this system)
    dreams.sort((a, b) => b.id.localeCompare(a.id));

    // Basic stats
    const approvedCount = dreams.filter(d => d.aprobado).length;
    DREAM_COUNT.innerText = approvedCount;
    // Rem cycles: arbitrary but based on unique hours or similar if wanted, 
    // for now we'll just show the total count of entries as "activity"
    REM_COUNT.innerText = dreams.length;

    if (JSON.stringify(dreams) === JSON.stringify(prevDreams)) return;
    prevDreams = dreams;

    CONTAINER.innerHTML = '';

    dreams.forEach(dream => {
        const card = document.createElement('div');
        card.className = `dream-card ${dream.aprobado ? 'approved' : 'discarded'}`;

        const badge = dream.aprobado ? 
            '<span class="dream-badge approved">Cosecha Aprobada</span>' : 
            '<span class="dream-badge discarded">Colchón de Sueños</span>';

        card.innerHTML = `
            <div class="dream-header">
                <span class="dream-id">${dream.id}</span>
                ${badge}
            </div>
            <div class="dream-asunto">${dream.asunto}</div>
            <div class="dream-desc">${dream.descripcion}</div>
            <div class="dream-footer">
                ${dream.fecha !== "Desconocida" ? `Fecha: ${dream.fecha}` : ''}
            </div>
        `;
        CONTAINER.appendChild(card);
    });
}

// Initial fetch
fetchDreams();

// Auto-refresh every 5 seconds
setInterval(fetchDreams, 5000);
