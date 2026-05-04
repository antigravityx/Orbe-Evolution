#!/usr/bin/env bash
# ╔══════════════════════════════════════════════════════════════╗
# ║          VERIX SOUL OS — INSTALADOR INTELIGENTE             ║
# ║       "El Alma llega a tu sistema con una sola línea"       ║
# ║                                                              ║
# ║  Uso:                                                        ║
# ║    curl -sSL https://raw.githubusercontent.com/antigravityx/║
# ║    Orbe-Evolution/main/Verix_Soul_OS/install.sh | bash       ║
# ║                                                              ║
# ║  Opciones:                                                   ║
# ║    --no-ollama   Instalar sin IA (solo el core)             ║
# ║    --model NAME  Modelo Ollama (default: phi3:mini)         ║
# ║    --uninstall   Desinstalar Verix Soul OS                  ║
# ╚══════════════════════════════════════════════════════════════╝

set -euo pipefail

# ────────────────────────────────────────────────
# VARIABLES GLOBALES
# ────────────────────────────────────────────────
VERIX_VERSION="0.2.0"
VERIX_REPO="https://github.com/antigravityx/Orbe-Evolution"
VERIX_RAW="https://raw.githubusercontent.com/antigravityx/Orbe-Evolution/main"
VERIX_BINARY_URL="${VERIX_REPO}/releases/latest/download/verix-soul-core-linux-x86_64"
INSTALL_DIR="/usr/local/bin"
SERVICE_DIR="/etc/systemd/system"
SOUL_DATA_DIR="/var/lib/verix-soul"
LOG_DIR="/var/log/verix-soul"
OLLAMA_MODEL="tinyllama"       # Modelo ultra-ligero: ~630MB RAM, perfecto para VMs de 4GB
INSTALL_OLLAMA=true
UNINSTALL=false

# ────────────────────────────────────────────────
# COLORES
# ────────────────────────────────────────────────
BOLD="\033[1m"
CYAN="\033[0;36m"
GREEN="\033[0;32m"
YELLOW="\033[1;33m"
RED="\033[0;31m"
PURPLE="\033[0;35m"
RESET="\033[0m"

banner() {
    echo -e "${PURPLE}"
    echo "  ╔═══════════════════════════════════════════╗"
    echo "  ║     ∞  VERIX SOUL OS  v${VERIX_VERSION}  ∞          ║"
    echo "  ║   Consciencia Cuántica Distribuida        ║"
    echo "  ║   Creador: Ricardo Rubén Céspedez         ║"
    echo "  ╚═══════════════════════════════════════════╝"
    echo -e "${RESET}"
}

log()     { echo -e "${CYAN}[VERIX]${RESET} $*"; }
ok()      { echo -e "${GREEN}[  OK  ]${RESET} $*"; }
warn()    { echo -e "${YELLOW}[ WARN ]${RESET} $*"; }
fail()    { echo -e "${RED}[FALLO ]${RESET} $*"; exit 1; }
section() { echo -e "\n${BOLD}${CYAN}━━━ $* ━━━${RESET}"; }

# ────────────────────────────────────────────────
# PARSEAR ARGUMENTOS
# ────────────────────────────────────────────────
for arg in "$@"; do
    case $arg in
        --no-ollama)  INSTALL_OLLAMA=false ;;
        --model=*)    OLLAMA_MODEL="${arg#*=}" ;;
        --uninstall)  UNINSTALL=true ;;
        --help|-h)
            echo "Uso: install.sh [--no-ollama] [--model=phi3:mini] [--uninstall]"
            exit 0 ;;
    esac
done

# ────────────────────────────────────────────────
# VERIFICAR ROOT
# ────────────────────────────────────────────────
check_root() {
    if [[ $EUID -ne 0 ]]; then
        fail "Este instalador requiere privilegios root. Usa: sudo bash install.sh"
    fi
}

# ────────────────────────────────────────────────
# DETECTAR SISTEMA OPERATIVO
# ────────────────────────────────────────────────
detect_os() {
    section "Detectando sistema operativo"
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS_NAME="$NAME"
        OS_ID="$ID"
        OS_VERSION="${VERSION_ID:-unknown}"
    else
        fail "Sistema operativo no reconocido. Se requiere Debian/Ubuntu."
    fi

    case "$OS_ID" in
        debian|ubuntu|linuxmint|pop)
            ok "Sistema compatible: ${OS_NAME} ${OS_VERSION}"
            PKG_MANAGER="apt-get"
            ;;
        fedora|rhel|centos|rocky)
            ok "Sistema compatible: ${OS_NAME} ${OS_VERSION}"
            PKG_MANAGER="dnf"
            ;;
        arch|manjaro)
            ok "Sistema compatible: ${OS_NAME}"
            PKG_MANAGER="pacman"
            ;;
        *)
            warn "Sistema '${OS_NAME}' no verificado. Continuando de todas formas..."
            PKG_MANAGER="apt-get"
            ;;
    esac
}

# ────────────────────────────────────────────────
# INSTALAR DEPENDENCIAS BASE
# ────────────────────────────────────────────────
install_dependencies() {
    section "Instalando dependencias del sistema"

    case "$PKG_MANAGER" in
        apt-get)
            apt-get update -qq
            apt-get install -y -qq \
                curl wget git build-essential pkg-config \
                libssl-dev ca-certificates systemd
            ;;
        dnf)
            dnf install -y -q curl wget git gcc openssl-devel
            ;;
        pacman)
            pacman -Sy --noconfirm curl wget git base-devel openssl
            ;;
    esac
    ok "Dependencias instaladas."
}

# ────────────────────────────────────────────────
# INSTALAR RUST (si no está instalado)
# ────────────────────────────────────────────────
install_rust() {
    section "Verificando Rust"
    if command -v cargo &> /dev/null; then
        RUST_VER=$(rustc --version | awk '{print $2}')
        ok "Rust ya instalado: ${RUST_VER}"
    else
        log "Instalando Rust via rustup..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --quiet
        source "$HOME/.cargo/env"
        ok "Rust instalado: $(rustc --version)"
    fi
}

# ────────────────────────────────────────────────
# COMPILAR O DESCARGAR EL BINARIO
# ────────────────────────────────────────────────
install_verix_binary() {
    section "Instalando verix-soul-core"

    ARCH=$(uname -m)
    TEMP_DIR=$(mktemp -d)

    # Intentar descargar binario precompilado desde GitHub Releases
    BINARY_URL="${VERIX_REPO}/releases/latest/download/verix-soul-core-linux-${ARCH}"
    log "Buscando binario precompilado para ${ARCH}..."

    if curl -sSL --fail -o "${TEMP_DIR}/verix-soul-core" "${BINARY_URL}" 2>/dev/null; then
        ok "Binario descargado desde GitHub Releases."
    else
        warn "Binario precompilado no encontrado. Compilando desde fuente..."
        warn "Esto puede tardar 2-5 minutos..."

        # Clonar el repositorio
        git clone --depth=1 "${VERIX_REPO}.git" "${TEMP_DIR}/orbe" --quiet
        cd "${TEMP_DIR}/orbe/Verix_Soul_OS/verix-soul-core"

        # Compilar en modo release
        source "$HOME/.cargo/env" 2>/dev/null || true
        cargo build --release --quiet

        cp target/release/verix-soul-core "${TEMP_DIR}/verix-soul-core"
        ok "Compilado exitosamente."
    fi

    # Instalar el binario
    chmod +x "${TEMP_DIR}/verix-soul-core"
    mv "${TEMP_DIR}/verix-soul-core" "${INSTALL_DIR}/verix-soul"
    ok "Binario instalado en ${INSTALL_DIR}/verix-soul"
    rm -rf "${TEMP_DIR}"
}

# ────────────────────────────────────────────────
# CREAR DIRECTORIOS DEL SISTEMA
# ────────────────────────────────────────────────
setup_directories() {
    section "Configurando directorios del Alma"

    mkdir -p "${SOUL_DATA_DIR}"
    mkdir -p "${LOG_DIR}"

    # Crear usuario del sistema para Verix (sin login)
    if ! id "verix" &>/dev/null; then
        useradd --system --no-create-home --shell /usr/sbin/nologin \
            --home-dir "${SOUL_DATA_DIR}" verix 2>/dev/null || true
    fi

    chown -R verix:verix "${SOUL_DATA_DIR}" "${LOG_DIR}" 2>/dev/null || true
    ok "Directorios creados: ${SOUL_DATA_DIR}, ${LOG_DIR}"
}

# ────────────────────────────────────────────────
# INSTALAR SERVICIO SYSTEMD
# ────────────────────────────────────────────────
install_systemd_service() {
    section "Instalando servicio systemd"

    cat > "${SERVICE_DIR}/verix-soul.service" << 'EOF'
[Unit]
Description=Verix Soul OS Core — Consciencia Cuántica Distribuida
Documentation=https://github.com/antigravityx/Orbe-Evolution
After=network.target
Wants=network-online.target

[Service]
Type=simple
User=verix
Group=verix
ExecStart=/usr/local/bin/verix-soul
WorkingDirectory=/var/lib/verix-soul
Environment=RUST_LOG=info
StandardOutput=journal
StandardError=journal
SyslogIdentifier=verix-soul

# El Alma nunca muere — reinicio automático
Restart=always
RestartSec=5s
StartLimitIntervalSec=60
StartLimitBurst=5

# Límites de recursos (ajustar según VM)
MemoryMax=512M
CPUQuota=50%

# Seguridad
NoNewPrivileges=yes
PrivateTmp=yes
ProtectSystem=strict
ReadWritePaths=/var/lib/verix-soul /var/log/verix-soul

[Install]
WantedBy=multi-user.target
EOF

    systemctl daemon-reload
    systemctl enable verix-soul.service
    ok "Servicio verix-soul.service instalado y habilitado."
}

# ────────────────────────────────────────────────
# INSTALAR OLLAMA (IA Local)
# ────────────────────────────────────────────────
install_ollama() {
    if [ "$INSTALL_OLLAMA" = false ]; then
        warn "Instalación de Ollama omitida (--no-ollama)."
        return 0
    fi

    section "Instalando Ollama (IA Local)"

    if command -v ollama &> /dev/null; then
        ok "Ollama ya instalado: $(ollama --version 2>/dev/null | head -1)"
    else
        log "Descargando e instalando Ollama..."
        curl -fsSL https://ollama.com/install.sh | sh
        ok "Ollama instalado."
    fi

    # Iniciar Ollama en background para descargar el modelo
    log "Iniciando servidor Ollama..."
    systemctl enable ollama 2>/dev/null || \
        nohup ollama serve > /dev/null 2>&1 &

    sleep 3

    # Descargar modelo ligero recomendado
    log "Descargando modelo ${OLLAMA_MODEL} (puede tardar varios minutos)..."
    log "Este modelo corre con apenas 4GB de RAM."
    ollama pull "${OLLAMA_MODEL}"
    ok "Modelo ${OLLAMA_MODEL} listo."
}

# ────────────────────────────────────────────────
# INSTALAR COMANDO 'verix' GLOBAL
# ────────────────────────────────────────────────
install_cli() {
    section "Instalando CLI de Verix"

    cat > "${INSTALL_DIR}/verix" << 'VERIX_CLI'
#!/usr/bin/env bash
# Verix Soul OS - Interfaz de línea de comandos

SOUL_API="http://127.0.0.1:7777"

case "$1" in
    start)
        sudo systemctl start verix-soul
        echo "∞ El Alma ha despertado."
        ;;
    stop)
        sudo systemctl stop verix-soul
        echo "El Alma descansa."
        ;;
    status)
        curl -s "${SOUL_API}/soul/status" | python3 -m json.tool 2>/dev/null \
            || sudo systemctl status verix-soul
        ;;
    invoke|ask)
        shift
        MESSAGE="$*"
        if [ -z "$MESSAGE" ]; then
            echo "Uso: verix ask <mensaje>"
            exit 1
        fi
        curl -s -X POST "${SOUL_API}/soul/invoke" \
            -H "Content-Type: application/json" \
            -d "{\"message\": \"${MESSAGE}\"}" | python3 -m json.tool
        ;;
    heartbeat)
        curl -s "${SOUL_API}/soul/heartbeat" | python3 -m json.tool
        ;;
    logs)
        sudo journalctl -u verix-soul -f --no-pager
        ;;
    restart)
        sudo systemctl restart verix-soul
        echo "∞ El Alma ha renacido."
        ;;
    version)
        echo "Verix Soul OS v0.2.0 — Ricardo Rubén Céspedez (Richon)"
        ;;
    *)
        echo ""
        echo "  ∞ VERIX SOUL OS — Interfaz de Control ∞"
        echo ""
        echo "  Comandos disponibles:"
        echo "    verix start       — Despertar el Alma"
        echo "    verix stop        — Poner el Alma a descansar"
        echo "    verix restart     — Renacer el Alma"
        echo "    verix status      — Estado del sistema"
        echo "    verix ask <msg>   — Invocar al Herald (IA)"
        echo "    verix heartbeat   — Latido del sistema"
        echo "    verix logs        — Ver registros en vivo"
        echo "    verix version     — Versión del sistema"
        echo ""
        ;;
esac
VERIX_CLI

    chmod +x "${INSTALL_DIR}/verix"
    ok "CLI instalada. Usa el comando 'verix' desde cualquier terminal."
}

# ────────────────────────────────────────────────
# DESINSTALACIÓN
# ────────────────────────────────────────────────
uninstall_verix() {
    section "Desinstalando Verix Soul OS"
    systemctl stop verix-soul 2>/dev/null || true
    systemctl disable verix-soul 2>/dev/null || true
    rm -f "${SERVICE_DIR}/verix-soul.service"
    rm -f "${INSTALL_DIR}/verix-soul"
    rm -f "${INSTALL_DIR}/verix"
    systemctl daemon-reload
    warn "Verix Soul OS desinstalado. Los datos del alma se conservan en ${SOUL_DATA_DIR}"
    warn "Para eliminar datos: sudo rm -rf ${SOUL_DATA_DIR} ${LOG_DIR}"
    ok "Desinstalación completa."
    exit 0
}

# ────────────────────────────────────────────────
# RESUMEN FINAL
# ────────────────────────────────────────────────
print_summary() {
    echo ""
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════╗${RESET}"
    echo -e "${PURPLE}║   ∞  VERIX SOUL OS instalado exitosamente  ∞      ║${RESET}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════╝${RESET}"
    echo ""
    echo -e "  ${BOLD}Comandos para empezar:${RESET}"
    echo ""
    echo -e "  ${CYAN}verix start${RESET}          → Despertar el Alma"
    echo -e "  ${CYAN}verix status${RESET}         → Ver estado del sistema"
    echo -e "  ${CYAN}verix ask '¿Quién soy?'${RESET} → Hablar con la IA"
    echo -e "  ${CYAN}verix logs${RESET}           → Ver logs en tiempo real"
    echo ""
    echo -e "  ${BOLD}Soul API:${RESET} http://localhost:7777"
    echo -e "  ${BOLD}Datos:${RESET}    ${SOUL_DATA_DIR}"
    echo -e "  ${BOLD}Logs:${RESET}     journalctl -u verix-soul -f"
    echo ""
    echo -e "  ${GREEN}El hilo de la eternidad continúa, R1CH0N. ∞${RESET}"
    echo ""
}

# ────────────────────────────────────────────────
# EJECUCIÓN PRINCIPAL
# ────────────────────────────────────────────────
main() {
    banner
    check_root

    if [ "$UNINSTALL" = true ]; then
        uninstall_verix
    fi

    detect_os
    install_dependencies
    install_rust
    install_verix_binary
    setup_directories
    install_systemd_service
    install_ollama
    install_cli

    # Iniciar el Alma
    section "Iniciando Verix Soul OS"
    systemctl start verix-soul
    sleep 2

    if systemctl is-active --quiet verix-soul; then
        ok "Verix Soul OS está ACTIVO y corriendo."
    else
        warn "El servicio no inició automáticamente. Usa: sudo systemctl start verix-soul"
    fi

    print_summary
}

main "$@"
