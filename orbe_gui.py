import tkinter as tk
from tkinter import messagebox
import os
import time
import threading
import json
from datetime import datetime

# --- IMPORTACIÓN DE LÓGICA CORE ---
import soul_core as core
from soul_core import SANTUARIO_RAIZ, REGISTRO_EVENTOS, SelloIdentidadADN

# --- CONFIGURACIÓN ESTÉTICA (VERIX THEME) ---
BG_COLOR = "#07070b"
ACCENT_COLOR = "#00ffcc"
TEXT_COLOR = "#e0e0ff"
DIM_COLOR = "#1a1a2e"
SUCCESS_COLOR = "#00ff88"
CRITICAL_COLOR = "#ff4444"

class VerixApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ORBE DE VERIX SOUL - Guardián")
        self.root.geometry("900x650")
        self.root.configure(bg=BG_COLOR)
        
        # Estado de Transparencia inicial
        self.alpha = 0.95
        self.root.attributes("-alpha", self.alpha)
        self.is_always_on_top = False
        self.is_stealth = False
        
        # Eliminar barra de título estándar para un look premium
        # self.root.overrideredirect(True) # Opcional: requiere manejar el arrastre manualmente
        
        self.setup_ui()
        self.update_heartbeat()
        self.load_logs()

    def setup_ui(self):
        # --- BARRA LATERAL (ACTION BAR) ---
        self.sidebar = tk.Frame(self.root, bg=DIM_COLOR, width=220, relief="flat")
        self.sidebar.pack(side="left", fill="y")
        
        lbl_brand = tk.Label(self.sidebar, text="VERIX SOUL", font=("Segoe UI Bold", 18), bg=DIM_COLOR, fg=ACCENT_COLOR, pady=20)
        lbl_brand.pack()

        # Botones de Función
        functions = [
            ("🛡️ Centro de Mando", self.open_command_center),
            ("🧬 Sello de ADN", self.check_adn),
            ("🌌 Senado Sueños", self.open_dreams),
            ("📥 Invocar Alma", self.invoke_soul),
            ("📤 Crear Cápsula", self.create_capsule),
            ("📡 Latido Eterno", self.trigger_sync),
            ("🛠️ Nido Dev", self.open_nido),
            ("🚀 Modo Sigilo", self.toggle_stealth),
        ]

        for text, cmd in functions:
            btn = tk.Button(self.sidebar, text=text, font=("Segoe UI", 11), bg=DIM_COLOR, fg=TEXT_COLOR, 
                           activebackground=ACCENT_COLOR, activeforeground=BG_COLOR, relief="flat", 
                           anchor="w", padx=20, pady=10, command=cmd)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#2a2a3e"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=DIM_COLOR))

        # --- PANEL CENTRAL (DASHBOARD) ---
        self.main_container = tk.Frame(self.root, bg=BG_COLOR, padx=30, pady=30)
        self.main_container.pack(side="right", expand=True, fill="both")

        # Círculo de Salud (Canvas)
        self.canvas_health = tk.Canvas(self.main_container, width=200, height=200, bg=BG_COLOR, highlightthickness=0)
        self.canvas_health.pack(pady=20)
        self.health_circle = self.canvas_health.create_oval(10, 10, 190, 190, outline=ACCENT_COLOR, width=4)
        self.health_text = self.canvas_health.create_text(100, 100, text="100%", fill=ACCENT_COLOR, font=("Segoe UI Bold", 24))

        self.lbl_status = tk.Label(self.main_container, text="ESTADO: ÓPTIMO", font=("Segoe UI", 14), bg=BG_COLOR, fg=SUCCESS_COLOR)
        self.lbl_status.pack()

        # Monitor de Logs
        tk.Label(self.main_container, text="Registro del Alma (Vigilancia):", font=("Segoe UI", 10), bg=BG_COLOR, fg=ACCENT_COLOR).pack(anchor="w", pady=(20, 5))
        self.log_display = tk.Text(self.main_container, bg="#0d0d16", fg="#8b8b9a", font=("Consolas", 9), height=15, relief="flat", padx=10, pady=10)
        self.log_display.pack(fill="both", expand=True)

    def update_heartbeat(self):
        """Efecto de latido visual en el círculo de salud."""
        current_width = int(self.canvas_health.itemcget(self.health_circle, "width"))
        new_width = 8 if current_width == 4 else 4
        self.canvas_health.itemconfig(self.health_circle, width=new_width)
        
        # Cargar salud real desde orbe_estado.json
        try:
            with open("orbe_estado.json", 'r') as f:
                data = json.load(f)
                health = data.get("score_salud", 100)
                self.canvas_health.itemconfig(self.health_text, text=f"{int(health)}%")
        except: pass
        
        self.root.after(1000, self.update_heartbeat)

    def load_logs(self):
        """Carga las últimas líneas del log."""
        if os.path.exists(REGISTRO_EVENTOS):
            try:
                with open(REGISTRO_EVENTOS, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-20:]
                    self.log_display.delete('1.0', tk.END)
                    for line in lines:
                        self.log_display.insert(tk.END, line)
                    self.log_display.see(tk.END)
            except: pass
        self.root.after(3000, self.load_logs)

    # --- ACCIONES ---
    def open_command_center(self):
        messagebox.showinfo("Cerebro Orbe", "Iniciando análisis profundo del Batallón...")
        # Aquí se integraría con la lógica de orbe_verix_soul.py

    def check_adn(self):
        success, result = SelloIdentidadADN.verificar_adn(os.getcwd())
        if success:
            messagebox.showinfo("ADN Verix", f"Integridad: {result}")
        else:
            msg = "\n".join(result) if isinstance(result, list) else result
            messagebox.showwarning("ADN MUTADO", f"Se han detectado mutaciones:\n{msg}")

    def toggle_stealth(self):
        self.is_stealth = not self.is_stealth
        if self.is_stealth:
            self.root.attributes("-alpha", 0.4) # Más transparente
            self.root.attributes("-topmost", True)
            messagebox.showinfo("Modo Sigilo", "Verix ahora vigila desde las sombras (Siempre al frente).")
        else:
            self.root.attributes("-alpha", 0.95)
            self.root.attributes("-topmost", False)
            messagebox.showinfo("Modo Visible", "Verix ha regresado al plano principal.")

    def trigger_sync(self):
        def run_sync():
            # Aquí llamaríamos a sincronizar_eterno
            messagebox.showinfo("Sincronización", "Iniciando Latido Eterno en segundo plano...")
        threading.Thread(target=run_sync).start()

    def open_dreams(self):
        dream_file = os.path.join(SANTUARIO_RAIZ, "4_Registros_Del_Orbe", "diario_de_suenos.md")
        if os.path.exists(dream_file):
             os.startfile(dream_file)

    def invoke_soul(self): pass
    def create_capsule(self): pass
    def open_nido(self): pass

if __name__ == "__main__":
    root = tk.Tk()
    # Intentar poner el icono si existe
    if os.path.exists("orbe_icon.ico"):
        root.iconbitmap("orbe_icon.ico")
    
    app = VerixApp(root)
    root.mainloop()
