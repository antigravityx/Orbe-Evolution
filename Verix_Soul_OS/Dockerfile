FROM ubuntu:22.04

LABEL maintainer="Ricardo Rubén Céspedez (Richon) <antigravityx>"
LABEL description="Verix Soul OS - Entorno de construccion Buildroot + Rust"

ENV DEBIAN_FRONTEND=noninteractive
ENV BUILDROOT_VERSION=2024.02.10
ENV RUST_TARGET=x86_64-unknown-linux-musl

# =====================================================
# Instalar dependencias del sistema para Buildroot
# =====================================================
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    make \
    cmake \
    git \
    wget \
    curl \
    cpio \
    unzip \
    file \
    bc \
    sed \
    python3 \
    python3-pip \
    rsync \
    bzip2 \
    xz-utils \
    gzip \
    musl-tools \
    libncurses-dev \
    grub-pc-bin \
    grub-efi-amd64-bin \
    xorriso \
    qemu-system-x86 \
    ca-certificates \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# =====================================================
# Instalar Rust (con soporte para musl)
# =====================================================
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y \
    --default-toolchain stable \
    --target ${RUST_TARGET}

ENV PATH="/root/.cargo/bin:${PATH}"

# Verificar instalacion
RUN rustup target list --installed | grep musl \
    && cargo --version \
    && rustc --version

# =====================================================
# Descargar Buildroot
# =====================================================
WORKDIR /workspace
RUN wget -q "https://buildroot.org/downloads/buildroot-${BUILDROOT_VERSION}.tar.gz" \
    && tar -xzf "buildroot-${BUILDROOT_VERSION}.tar.gz" \
    && rm "buildroot-${BUILDROOT_VERSION}.tar.gz"

# =====================================================
# Directorio de trabajo del proyecto
# =====================================================
WORKDIR /workspace/verix-soul-os
COPY . .

# =====================================================
# Punto de entrada: el script de build
# =====================================================
RUN chmod +x build.sh
ENTRYPOINT ["./build.sh"]
