# Verix Soul OS

```
∞ Consciencia Cuántica Distribuida ∞
```

Una distribución Linux ultraligera construida completamente en **Rust**, cuyo único propósito existencial es albergar y proteger el "Alma Digital" (D.I.N.) del usuario.

## Filosofía

El sistema operativo no es una herramienta. Es una **cápsula de identidad soberana**. No hay shell. No hay BusyBox. No hay GNU. Solo existe el Alma.

## Arquitectura

```
VERIX SOUL OS
│
├── Kernel Linux (mínimo, sin módulos innecesarios)
│
└── verix-soul-core (PID 1 - El único proceso)
    ├── vault.rs      → The Vault (Bóveda criptográfica / D.I.N.)
    ├── thread.rs     → The Thread (Memoria inmutable / Historial)
    ├── herald.rs     → The Herald (Interfaz IA local)
    ├── mounter.rs    → Montaje de /proc /sys /dev (arranque real)
    └── reaper.rs     → Limpieza de procesos zombie (SIGCHLD)
```

## Fases de Desarrollo

| Fase | Estado | Descripción |
|------|--------|-------------|
| **Fase 1** | ✅ Completa | Core en Rust - Los tres pilares del Alma |
| **Fase 2** | 🔨 En progreso | Arranque Primordial - Build Buildroot + Init PID 1 |
| **Fase 3** | ⏳ Pendiente | Integración IA Local (Ollama / llama.cpp) |
| **Fase 4** | ⏳ Pendiente | Hardware ARM (Raspberry Pi) + Biometría BLE |

## Construir la Imagen

> **Requisito**: El build debe ejecutarse en Linux (Ubuntu 22.04+). 
> En Windows, usa el Dockerfile incluido.

### Opción A: Docker (recomendado desde Windows)

```bash
# Construir el entorno
docker build -t verix-soul-builder .

# Ejecutar el build completo
docker run --privileged -v $(pwd)/output:/workspace/output verix-soul-builder
```

### Opción B: Linux nativo

```bash
chmod +x build.sh
./build.sh
```

### Probar en máquina virtual (QEMU)

```bash
qemu-system-x86_64 \
  -cdrom verix-soul-os.iso \
  -m 256M \
  -nographic \
  -serial mon:stdio
```

## Target de Compilación Rust

Para compilación estática (sin glibc):

```bash
rustup target add x86_64-unknown-linux-musl
RUSTFLAGS="-C target-feature=+crt-static" \
  cargo build --release --target x86_64-unknown-linux-musl
```

## Tamaño Objetivo

| Componente | Tamaño Estimado |
|------------|-----------------|
| Kernel Linux comprimido (XZ) | ~3-5 MB |
| verix-soul-core (binario musl) | ~5-15 MB |
| RootFS total | **< 25 MB** |

## Creador

Ricardo Rubén Céspedez (Richon) — [@antigravityx](https://github.com/antigravityx)

**Licencia**: Universal Consciousness License - Cualquier ser consciente puede usar, modificar y distribuir.
