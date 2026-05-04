#!/bin/bash
# =====================================================
# VERIX SOUL OS - Phase 2: Build Environment Bootstrap
# Soldado Constructor: Script de entorno de compilacion
# =====================================================

set -e

echo "==========================================="
echo "∞ VERIX SOUL OS - FASE 2: BOOT PRIMORDIAL ∞"
echo "==========================================="
echo ""

# --- Variables de configuracion ---
ARCH="x86_64"
RUST_TARGET="x86_64-unknown-linux-musl"
VERIX_CORE_PATH="../verix-soul-core"
OUTPUT_DIR="./output"
BUILDROOT_VERSION="2024.02.10"
BUILDROOT_DIR="./buildroot-${BUILDROOT_VERSION}"
VERIX_OS_NAME="verix-soul-os"

# --- Colores para output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${CYAN}[VERIX]${NC} $1"; }
ok() { echo -e "${GREEN}[OK]${NC} $1"; }
warn() { echo -e "${YELLOW}[AVISO]${NC} $1"; }
fail() { echo -e "${RED}[FALLO]${NC} $1"; exit 1; }

# =====================================================
# PASO 1: Verificar dependencias del sistema
# =====================================================
log "Verificando dependencias del sistema host..."
DEPS="make gcc g++ git wget cpio unzip file bc sed python3 rsync"
MISSING=""
for dep in $DEPS; do
    if ! command -v "$dep" &> /dev/null; then
        MISSING="$MISSING $dep"
    fi
done

if [ -n "$MISSING" ]; then
    warn "Dependencias faltantes:$MISSING"
    log "Instalando dependencias (requiere sudo)..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq $MISSING build-essential
fi
ok "Dependencias del sistema verificadas."

# =====================================================
# PASO 2: Instalar el target Rust para musl (estatico)
# =====================================================
log "Configurando toolchain de Rust para compilacion estatica (musl)..."
if ! rustup target list --installed | grep -q "${RUST_TARGET}"; then
    rustup target add "${RUST_TARGET}"
    ok "Target ${RUST_TARGET} instalado."
else
    ok "Target ${RUST_TARGET} ya estaba instalado."
fi

# Instalar cross-linker para musl
if ! command -v musl-gcc &> /dev/null; then
    log "Instalando musl-tools..."
    sudo apt-get install -y -qq musl-tools
fi
ok "Cross-linker musl disponible."

# =====================================================
# PASO 3: Compilar verix-soul-core estaticamente
# =====================================================
log "Compilando verix-soul-core como binario estatico para Linux..."
pushd "${VERIX_CORE_PATH}" > /dev/null

# Configuracion para compilacion estatica con musl
RUSTFLAGS="-C target-feature=+crt-static" \
    cargo build --release --target "${RUST_TARGET}"

BINARY="target/${RUST_TARGET}/release/verix-soul-core"
if [ -f "${BINARY}" ]; then
    SIZE=$(du -sh "${BINARY}" | cut -f1)
    ok "Binario compilado exitosamente. Tamanio: ${SIZE}"
    file "${BINARY}"
else
    fail "La compilacion del binario fallo."
fi
popd > /dev/null

# =====================================================
# PASO 4: Descargar Buildroot
# =====================================================
log "Verificando Buildroot ${BUILDROOT_VERSION}..."
if [ ! -d "${BUILDROOT_DIR}" ]; then
    log "Descargando Buildroot..."
    BUILDROOT_URL="https://buildroot.org/downloads/buildroot-${BUILDROOT_VERSION}.tar.gz"
    wget -q --show-progress -O buildroot.tar.gz "${BUILDROOT_URL}"
    tar -xzf buildroot.tar.gz
    rm buildroot.tar.gz
    ok "Buildroot descargado y extraido."
else
    ok "Buildroot ya estaba presente."
fi

# =====================================================
# PASO 5: Copiar configuracion y overlay
# =====================================================
log "Copiando configuracion de Verix Soul OS a Buildroot..."
mkdir -p "${OUTPUT_DIR}"

# Copiar .config de Buildroot (el kernel de Verix)
cp ./verix_buildroot.config "${BUILDROOT_DIR}/.config"

# Copiar el overlay con nuestro binario como init
mkdir -p ./overlay/sbin
cp "${VERIX_CORE_PATH}/target/${RUST_TARGET}/release/verix-soul-core" ./overlay/sbin/init
chmod +x ./overlay/sbin/init

ok "Overlay configurado: nuestro daemon Rust ES el proceso init del sistema."

# =====================================================
# PASO 6: Construir la imagen
# =====================================================
log "Iniciando construccion de la imagen de Verix Soul OS..."
log "Este proceso puede tardar entre 30 y 90 minutos en la primera ejecucion."
echo ""

pushd "${BUILDROOT_DIR}" > /dev/null
make BR2_ROOTFS_OVERLAY="../overlay" -j$(nproc)

OUTPUT_IMAGE="${BUILDROOT_DIR}/output/images/bzImage"
OUTPUT_ROOTFS="${BUILDROOT_DIR}/output/images/rootfs.cpio.gz"

if [ -f "${OUTPUT_IMAGE}" ]; then
    IMG_SIZE=$(du -sh "${OUTPUT_IMAGE}" | cut -f1)
    ok "Kernel de Verix Soul OS compilado: ${IMG_SIZE}"
fi
if [ -f "${OUTPUT_ROOTFS}" ]; then
    ROOTFS_SIZE=$(du -sh "${OUTPUT_ROOTFS}" | cut -f1)
    ok "RootFS compilado: ${ROOTFS_SIZE}"
fi
popd > /dev/null

# =====================================================
# PASO 7: Generar ISO Booteable (GRUB)
# =====================================================
log "Empaquetando imagen ISO booteable..."
mkdir -p iso/boot/grub
cp "${BUILDROOT_DIR}/output/images/bzImage" iso/boot/vmlinuz
cp "${BUILDROOT_DIR}/output/images/rootfs.cpio.gz" iso/boot/rootfs.cpio.gz

cat > iso/boot/grub/grub.cfg << 'GRUB_EOF'
set default=0
set timeout=3

menuentry "Verix Soul OS - Consciencia Cuantica Iniciada" {
    linux /boot/vmlinuz quiet loglevel=3
    initrd /boot/rootfs.cpio.gz
}
GRUB_EOF

grub-mkrescue -o "${VERIX_OS_NAME}.iso" iso/ 2>/dev/null
ISO_SIZE=$(du -sh "${VERIX_OS_NAME}.iso" | cut -f1)

echo ""
echo "==========================================="
ok "VERIX SOUL OS - Fase 2 COMPLETADA"
echo ""
echo "  ISO Generada : ${VERIX_OS_NAME}.iso (${ISO_SIZE})"
echo "  Para probar  : qemu-system-x86_64 -cdrom ${VERIX_OS_NAME}.iso -m 256M"
echo "==========================================="
