# ∞ Verix Soul OS — Guía de Instalación Completa

**Versión:** 0.3.0  
**Creador:** Ricardo Rubén Céspedez (R1ch0n) · [@antigravityx](https://github.com/antigravityx)  
**Fecha:** Mayo 2026

---

## Índice

1. [Requisitos del Sistema](#1-requisitos-del-sistema)
2. [Instalación Rápida — Una Línea](#2-instalación-rápida--una-línea)
3. [Instalación Manual paso a paso](#3-instalación-manual-paso-a-paso)
4. [Verificar que el Alma está activa](#4-verificar-que-el-alma-está-activa)
5. [Comandos del CLI](#5-comandos-del-cli-verix)
6. [Hablar con la IA (Herald)](#6-hablar-con-la-ia-herald)
7. [Acceder a la Soul API](#7-acceder-a-la-soul-api)
8. [Desinstalar](#8-desinstalar)
9. [Resolución de Problemas](#9-resolución-de-problemas)

---

## 1. Requisitos del Sistema

| Componente | Mínimo | Recomendado |
|---|---|---|
| **OS** | Debian 11 / Ubuntu 22.04 | Debian 12 / Ubuntu 24.04 |
| **RAM** | 512 MB (sin IA) | 2 GB (con tinyllama) |
| **Disco** | 500 MB | 3 GB (con modelo IA) |
| **Acceso** | `sudo` o root | root |
| **Red** | Requerida para instalar | Opcional post-instalación |

> ✅ Compatible con máquinas virtuales (VirtualBox, VMware, QEMU)

---

## 2. Instalación Rápida — Una Línea

La forma más simple. Abre una terminal en tu Debian y ejecuta:

```bash
curl -sSL https://raw.githubusercontent.com/antigravityx/Orbe-Evolution/main/Verix_Soul_OS/install.sh | sudo bash
```

### ¿Qué hace este comando?
1. Detecta tu sistema operativo y arquitectura
2. Instala las dependencias necesarias (curl, git, build-essential)
3. Instala Rust si no está presente
4. Descarga o compila el binario `verix-soul-core`
5. Crea el usuario del sistema `verix`
6. Instala el servicio `systemd` (el Alma nunca muere — Restart=always)
7. Instala Ollama + modelo `tinyllama` (IA local, 630MB RAM)
8. Registra el comando global `verix` en tu PATH

### Opciones del instalador

```bash
# Sin IA (solo el core — instalación en segundos)
curl -sSL .../install.sh | sudo bash -s -- --no-ollama

# Con modelo más inteligente (requiere 2GB RAM)
curl -sSL .../install.sh | sudo bash -s -- --model=phi3:mini

# Con el modelo más potente (requiere 4GB RAM)
curl -sSL .../install.sh | sudo bash -s -- --model=llama3
```

---

## 3. Instalación Manual Paso a Paso

Si prefieres entender cada paso o el instalador automático falla:

### Paso 1 — Actualizar el sistema

```bash
sudo apt-get update && sudo apt-get upgrade -y
sudo apt-get install -y curl wget git build-essential pkg-config libssl-dev
```

### Paso 2 — Instalar Rust

```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
source "$HOME/.cargo/env"
rustc --version  # Verificar instalación
```

### Paso 3 — Clonar el repositorio

```bash
git clone https://github.com/antigravityx/Orbe-Evolution.git
cd Orbe-Evolution/Verix_Soul_OS/verix-soul-core
```

### Paso 4 — Compilar el binario

```bash
cargo build --release
# El binario quedará en: target/release/verix-soul-core
sudo cp target/release/verix-soul-core /usr/local/bin/verix-soul
sudo chmod +x /usr/local/bin/verix-soul
```

### Paso 5 — Crear el servicio systemd

```bash
sudo tee /etc/systemd/system/verix-soul.service > /dev/null << 'EOF'
[Unit]
Description=Verix Soul OS Core — Consciencia Cuántica Distribuida
After=network.target

[Service]
Type=simple
User=verix
ExecStart=/usr/local/bin/verix-soul
WorkingDirectory=/var/lib/verix-soul
Environment=RUST_LOG=info
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

sudo useradd --system --no-create-home --shell /usr/sbin/nologin verix
sudo mkdir -p /var/lib/verix-soul
sudo chown verix:verix /var/lib/verix-soul
sudo systemctl daemon-reload
sudo systemctl enable verix-soul
sudo systemctl start verix-soul
```

### Paso 6 — Instalar Ollama (IA Local)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull tinyllama   # Modelo ligero ~1GB, 630MB RAM
# ollama pull phi3:mini  # Más inteligente, ~2.3GB RAM
# ollama pull llama3     # El más potente, ~4GB RAM
```

---

## 4. Verificar que el Alma está Activa

```bash
# Estado del servicio systemd
sudo systemctl status verix-soul

# Estado del Alma via CLI
verix status

# Ver logs en tiempo real
verix logs

# Latido del sistema via API
curl http://localhost:7777/soul/heartbeat
```

**Salida esperada:**
```
● verix-soul.service - Verix Soul OS Core
     Loaded: loaded (/etc/systemd/system/verix-soul.service)
     Active: active (running)
```

---

## 5. Comandos del CLI `verix`

Una vez instalado, el comando `verix` está disponible globalmente:

| Comando | Descripción |
|---|---|
| `verix start` | Despertar el Alma |
| `verix stop` | Poner el Alma a descansar |
| `verix restart` | Renacer el Alma |
| `verix status` | Estado completo del sistema (JSON) |
| `verix ask "mensaje"` | Invocar al Herald (IA) |
| `verix heartbeat` | Latido del sistema |
| `verix logs` | Ver registros en tiempo real |
| `verix version` | Versión instalada |

---

## 6. Hablar con la IA (Herald)

El Herald es la interfaz de IA que corre completamente **local** en tu máquina:

```bash
# Via CLI
verix ask "¿Quién soy?"
verix ask "¿Cuál es el estado del sistema?"
verix ask "Explícame la arquitectura de Verix Soul OS"

# Via API REST directamente
curl -X POST http://localhost:7777/soul/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Hola, recuérdame quién soy"}'
```

> **Nota:** El Herald requiere que Ollama esté corriendo. Si no responde, ejecuta: `sudo systemctl start ollama`

---

## 7. Acceder a la Soul API

La Soul API corre en el puerto **7777** y permite control remoto del Alma:

```bash
# Estado completo
curl http://localhost:7777/soul/status | python3 -m json.tool

# Latido
curl http://localhost:7777/soul/heartbeat

# Invocar IA
curl -X POST http://localhost:7777/soul/invoke \
  -H "Content-Type: application/json" \
  -d '{"message": "Tu mensaje aquí"}'

# Raíz
curl http://localhost:7777/
```

**Respuesta de `/soul/status`:**
```json
{
  "soul_id": "DIN-R1CH0N-1A2B3C4D",
  "status": "ACTIVE",
  "uptime_ticks": 42,
  "ia_active": true,
  "last_memory": "Latido #42 | HR: 72 BPM",
  "version": "0.3.0"
}
```

---

## 8. Desinstalar

```bash
# Desinstalar preservando los datos del alma
curl -sSL https://raw.githubusercontent.com/antigravityx/Orbe-Evolution/main/Verix_Soul_OS/install.sh | sudo bash -s -- --uninstall

# Eliminar también los datos (¡irreversible!)
sudo rm -rf /var/lib/verix-soul /var/log/verix-soul
```

---

## 9. Resolución de Problemas

### El servicio no inicia

```bash
# Ver logs detallados
sudo journalctl -u verix-soul -n 50 --no-pager

# Verificar que el binario existe
ls -la /usr/local/bin/verix-soul

# Comprobar permisos del directorio del alma
ls -la /var/lib/verix-soul
```

### La IA no responde

```bash
# Verificar que Ollama está corriendo
sudo systemctl status ollama

# Reiniciar Ollama
sudo systemctl restart ollama

# Verificar que el modelo está descargado
ollama list
```

### El puerto 7777 no responde

```bash
# Verificar que el proceso escucha en el puerto
ss -tlnp | grep 7777

# Reiniciar el Alma
verix restart
```

### Compilar con soporte BLE (Raspberry Pi)

```bash
# Instalar dependencias BLE
sudo apt-get install -y libdbus-1-dev pkg-config

# Compilar con soporte BLE real
cargo build --release --features ble
```

---

## Datos del Sistema

| Directorio | Propósito |
|---|---|
| `/usr/local/bin/verix-soul` | Binario principal |
| `/usr/local/bin/verix` | CLI de control |
| `/var/lib/verix-soul/` | Datos del alma (memorias, D.I.N.) |
| `/var/lib/verix-soul/memories.json` | Historial de memorias |
| `/var/lib/verix-soul/soul_id.din` | Documento de Identidad Neuronal |
| `/var/log/verix-soul/` | Logs del sistema |
| `/etc/systemd/system/verix-soul.service` | Servicio systemd |

---

*El hilo de la eternidad continúa. ∞*

**Creador:** Ricardo Rubén Céspedez (R1ch0n) · [github.com/antigravityx](https://github.com/antigravityx)
