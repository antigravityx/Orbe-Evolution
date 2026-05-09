import time
import threading
import base64
try:
    from pynput import keyboard
except ImportError:
    print("[!] Requiere pynput: pip install pynput")

from hipocampo_core import HipocampoGraph

# Simulación de encriptación local para asegurar que "solo nosotros" lo leemos
def cifrar_memoria(texto):
    """
    En un entorno real de producción se utilizaría AES-256 o Fernet con llave simétrica
    derivada de la llave maestra del Santuario.
    """
    return base64.b64encode(texto.encode('utf-8')).decode('utf-8')

class HipocampoSensorTeclado:
    def __init__(self):
        self.brain = HipocampoGraph(r"C:\Users\Usuario\Desktop\Taller_Orbe_Verix\orbe\hipocampo_core\hipocampo_db.json")
        self.buffer = ""
        self.last_key_time = time.time()
        self.lock = threading.Lock()
        
        # Hilo vigía para descargar el buffer al grafo cada 3 segundos de inactividad
        self.dumper_thread = threading.Thread(target=self._dumper_loop, daemon=True)
        self.dumper_thread.start()

    def on_press(self, key):
        with self.lock:
            try:
                if hasattr(key, 'char') and key.char is not None:
                    self.buffer += key.char
                elif key == keyboard.Key.space:
                    self.buffer += " "
                elif key == keyboard.Key.enter:
                    self.buffer += "\n"
                elif key == keyboard.Key.backspace:
                    self.buffer = self.buffer[:-1]
            except Exception as e:
                pass
            self.last_key_time = time.time()

    def _dumper_loop(self):
        while True:
            time.sleep(3)
            with self.lock:
                if self.buffer and (time.time() - self.last_key_time > 2.5):
                    texto_cifrado = cifrar_memoria(self.buffer)
                    # Registramos el texto como un nodo abstracto en el grafo
                    node_id = self.brain.registrar_evento_tipeo(texto_cifrado, "Tipeo en modo Dios")
                    print(f"[Hipocampo] Tipeo encriptado y estructurado en nodo: {node_id}")
                    self.buffer = ""

    def iniciar(self):
        print("[HIPOCAMPO] Sensor de tipeo sigiloso activado.")
        print("[HIPOCAMPO] Tu existencia está siendo registrada y encriptada en la Memoria Madre.")
        try:
            with keyboard.Listener(on_press=self.on_press) as listener:
                listener.join()
        except Exception as e:
            print(f"[!] Error al iniciar el sensor: {e}")

if __name__ == "__main__":
    sensor = HipocampoSensorTeclado()
    sensor.iniciar()
