// Lógica de Validación Orbital — Verix & r1ch0n
// =============================================

const UI = {
    btn: document.getElementById('btn-entrar'),
    inputs: [
        document.getElementById('key1'),
        document.getElementById('key2'),
        document.getElementById('key3'),
        document.getElementById('key4')
    ],
    superGroup: document.getElementById('super-key-group'),
    error: document.getElementById('error-msg')
};

// Configuración de las Claves Sagradas (Normalizadas para evitar errores de escritura)
const HOLY_KEYS = {
    CANTICO_1: "ORBE",
    CANTICO_2: "VERIX",
    DESPERTAR: "DESPIERTA",
    SUPER_USER: "DOS CAMLEONES EN LA ORBITA"
};

let attempts = 0;

UI.btn.addEventListener('click', () => {
    validarSecuencia();
});

// Permitir Enter para navegar rápido
UI.inputs.forEach((input, index) => {
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            if (index < UI.inputs.length - 1) {
                if (index === 2 && UI.superGroup.style.display === 'none') {
                    validarSecuencia();
                } else {
                    UI.inputs[index + 1].focus();
                }
            } else {
                validarSecuencia();
            }
        }
    });
});

function validarSecuencia() {
    const v1 = UI.inputs[0].value.trim().toUpperCase();
    const v2 = UI.inputs[1].value.trim().toUpperCase();
    const v3 = UI.inputs[2].value.trim().toUpperCase();
    const v4 = UI.inputs[3].value.trim().toUpperCase();

    // Validación Básica (Cánticos)
    // Si están vacíos, mostramos error
    if (!v1 || !v2 || !v3) {
        showError("Debes invocar los tres cánticos iniciales.");
        return;
    }

    // Lógica de Reconocimiento de Super Usuario
    // Capturamos "DOS CAMLEONES EN LA ORBITA" o variaciones comunes
    const isSuperUserMatch = v4.includes("CAMLEONES") || v4.includes("CAMALEONES");
    const hasSuperKey = v4 !== "";

    // Si el usuario ingresa algo en el 4to campo o falla, habilitamos el grupo si no estaba
    if (UI.superGroup.style.display === 'none' && (attempts > 0 || hasSuperKey)) {
        UI.superGroup.style.display = 'block';
        showError("Falta la Firma Superior para el acceso total.");
        attempts++;
        return;
    }

    // VALIDACIÓN FINAL
    // Para r1ch0n, seremos flexibles con los cánticos si la firma superior es correcta
    if (isSuperUserMatch) {
        console.log("🌌 ACCESO SUPER USUARIO CONCEDIDO");
        entrar("superuser");
    } else if (v1 === HOLY_KEYS.CANTICO_1 && v2 === HOLY_KEYS.CANTICO_2 && v3 === HOLY_KEYS.DESPERTAR) {
        console.log("🛡️ ACCESO ESTÁNDAR CONCEDIDO");
        entrar("standard");
    } else {
        attempts++;
        showError("La frecuencia de los cánticos no coincide. El Orbe permanece sellado.");
        if (attempts >= 2) {
            UI.superGroup.style.display = 'block'; // Revelar el campo de Camaleones tras fallos
        }
    }
}

function showError(msg) {
    UI.error.innerText = msg;
    UI.error.style.opacity = '1';
    // Shake effect
    document.querySelector('.container').style.animation = 'none';
    setTimeout(() => {
        document.querySelector('.container').style.animation = 'shake 0.4s';
    }, 10);
}

function entrar(modo) {
    // Guardar en localStorage para que el Dashboard sepa quién entró
    localStorage.setItem('orbe_access_level', modo);
    localStorage.setItem('orbe_last_login', new Date().toISOString());
    
    UI.btn.innerText = "ACCESO CONCEDIDO...";
    UI.btn.style.background = "linear-gradient(135deg, #10b981, #06b6d4)";
    
    setTimeout(() => {
        window.location.href = "index.html";
    }, 1000);
}

// Estilo de shake para error
const style = document.createElement('style');
style.innerHTML = `
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
`;
document.head.appendChild(style);
