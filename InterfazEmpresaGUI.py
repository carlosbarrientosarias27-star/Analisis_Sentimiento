# InicioSentimiento.py — Versión refactorizada con GUI
import tkinter as tk
from tkinter import messagebox
from sentimiento.cliente import crear_cliente 
from sentimiento.niveles import basico, intermedio, avanzado
from almacenamiento.guardar import guardar_resultado
 
class AppSentimiento:
    def __init__(self, root):
        self.root = root
        self.root.title('Análisis de Sentimiento - Local')
        self.client = crear_cliente ()
        self._construir_interfaz()
 
    def _construir_interfaz(self):
        # ... construye todos los widgets (pestañas, botones, tabla, etc.)
        pass
 
    def analizar(self):
        texto = self.texto_entrada.get('1.0', tk.END).strip()
        if not texto:
            messagebox.showwarning('Aviso', 'Escribe un texto para analizar')
            return
        resultado_b = basico(texto, self.client)
        resultado_i = intermedio(texto, self.client)
        resultado_a = avanzado(texto, self.client)
        rutas = guardar_resultado(texto, {'basico': resultado_b, 'intermedio': resultado_i, 'avanzado': resultado_a})
        self.barra_estado.config(text=f'Análisis completado y guardado: {rutas["txt"]}')
 
if __name__ == '__main__':
    root = tk.Tk()
    app = AppSentimiento(root)
    root.mainloop()