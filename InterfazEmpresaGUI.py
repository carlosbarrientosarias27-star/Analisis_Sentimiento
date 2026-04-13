# InterfazEmpresaGUI.py - GUI para Análisis de Sentimiento
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from tkinter import font as tkfont
from sentimiento.cliente import crear_cliente
from sentimiento.niveles import basico, intermedio, avanzado
from almacenamiento.guardar import guardar_resultado
from almacenamiento.leer import listar_analisis
import json
from pathlib import Path


class AppSentimiento:
    def __init__(self, root):
        self.root = root
        self.root.title("Analisis de Sentimiento - Local")
        self.root.geometry("950x750")
        self.root.configure(bg="#f0f0f0")

        self.cliente = None
        self.resultados = {}
        self.texto_actual = ""

        self._construir_interfaz()
        self._inicializar_cliente()

    def _inicializar_cliente(self):
        try:
            self.cliente = crear_cliente()
            self.barra_estado.config(text="Conectado a OpenAI", fg="green")
        except Exception as e:
            self.barra_estado.config(text=f"Error de conexion: {str(e)}", fg="red")

    def _construir_interfaz(self):
        # Marco principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titulo
        titulo = tk.Label(
            main_frame,
            text="Analisis de Sentimiento - Local",
            font=("Helvetica", 18, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        titulo.pack(pady=10, anchor=tk.CENTER)

        # Marco de entrada de texto
        entrada_frame = ttk.LabelFrame(main_frame, text="Texto a analizar", padding="10")
        entrada_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.texto_entrada = scrolledtext.ScrolledText(
            entrada_frame,
            height=6,
            font=("Arial", 11),
            wrap=tk.WORD
        )
        self.texto_entrada.pack(fill=tk.BOTH, expand=True)

        # Marco de botones
        botones_frame = tk.Frame(main_frame, bg="#f0f0f0")
        botones_frame.pack(pady=10, anchor=tk.CENTER)

        self.btn_analizar = tk.Button(
            botones_frame,
            text="ANALIZAR SENTIMIENTO",
            command=self.analizar,
            font=("Arial", 11, "bold"),
            bg="#3498db",
            fg="white",
            activebackground="#2980b9",
            activeforeground="white",
            padx=20,
            pady=8
        )
        self.btn_analizar.pack(side=tk.LEFT, padx=10)

        self.btn_limpiar = tk.Button(
            botones_frame,
            text="LIMPIAR",
            command=self.limpiar,
            font=("Arial", 11, "bold"),
            bg="#95a5a6",
            fg="white",
            activebackground="#7f8c8d",
            activeforeground="white",
            padx=20,
            pady=8
        )
        self.btn_limpiar.pack(side=tk.LEFT, padx=10)

        self.btn_guardar = tk.Button(
            botones_frame,
            text="GUARDAR",
            command=self.guardar_manual,
            font=("Arial", 11, "bold"),
            bg="#27ae60",
            fg="white",
            activebackground="#219150",
            activeforeground="white",
            padx=20,
            pady=8
        )
        self.btn_guardar.pack(side=tk.LEFT, padx=10)

        # Notebook para pestanas
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=5)

        # Pestanas
        self.tab_resultados = ttk.Frame(self.notebook)
        self.tab_detalle = ttk.Frame(self.notebook)
        self.tab_justificacion = ttk.Frame(self.notebook)
        self.tab_historial = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_resultados, text="Resultados por Nivel")
        self.notebook.add(self.tab_detalle, text="Analisis Detallado")
        self.notebook.add(self.tab_justificacion, text="Justificacion & Recomendacion")
        self.notebook.add(self.tab_historial, text="Historial")

        # Contenido de cada pestana
        self._crear_tabla_resultados()
        self._crear_tabla_detalle()
        self._crear_tabla_justificacion()
        self._crear_tabla_historial()

        # Panel de ayuda - Polaridad
        ayuda_frame = ttk.LabelFrame(main_frame, text="Que significa la polaridad?", padding="10")
        ayuda_frame.pack(fill=tk.X, pady=5)

        ayuda_texto = "POSITIVA (+0 a +1)  |  NEGATIVA (-1 a 0)  |  NEUTRAL (0)"
        tk.Label(
            ayuda_frame,
            text=ayuda_texto,
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#2c3e50"
        ).pack()

        # Barra de estado
        self.barra_estado = tk.Label(
            main_frame,
            text="Listo",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d",
            anchor=tk.W,
            width=80
        )
        self.barra_estado.pack(pady=5)

    def _crear_tabla_resultados(self):
        frame = ttk.Frame(self.tab_resultados, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Encabezados de columna
        headers = ["Nivel", "Sentimiento", "Polaridad", "Intensidad"]
        for i, h in enumerate(headers):
            tk.Label(frame, text=h, font=("Arial", 11, "bold"), bg="#ecf0f1").grid(row=0, column=i, padx=20, pady=5, sticky=tk.W)

        # Filas para cada nivel
        self.lbl_basico = [tk.Label(frame, text="-", font=("Arial", 10), bg="#f0f0f0") for _ in range(3)]
        self.lbl_intermedio = [tk.Label(frame, text="-", font=("Arial", 10), bg="#f0f0f0") for _ in range(3)]
        self.lbl_avanzado = [tk.Label(frame, text="-", font=("Arial", 10), bg="#f0f0f0") for _ in range(3)]

        row_b = 1
        tk.Label(frame, text="Basico", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=row_b, column=0, padx=20, pady=5, sticky=tk.W)
        for i, lbl in enumerate(self.lbl_basico):
            lbl.grid(row=row_b, column=i+1, padx=20, pady=5, sticky=tk.W)

        row_i = 2
        tk.Label(frame, text="Intermedio", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=row_i, column=0, padx=20, pady=5, sticky=tk.W)
        for i, lbl in enumerate(self.lbl_intermedio):
            lbl.grid(row=row_i, column=i+1, padx=20, pady=5, sticky=tk.W)

        row_a = 3
        tk.Label(frame, text="Avanzado", font=("Arial", 10, "bold"), bg="#f0f0f0").grid(row=row_a, column=0, padx=20, pady=5, sticky=tk.W)
        for i, lbl in enumerate(self.lbl_avanzado):
            lbl.grid(row=row_a, column=i+1, padx=20, pady=5, sticky=tk.W)

    def _crear_tabla_detalle(self):
        frame = ttk.Frame(self.tab_detalle, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Emociones detectadas:", font=("Arial", 11, "bold"), bg="#f0f0f0").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.lbl_emociones = tk.Label(frame, text="-", font=("Arial", 10), fg="#34495e", justify=tk.LEFT, bg="#f0f0f0")
        self.lbl_emociones.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Polaridad extendida:", font=("Arial", 11, "bold"), bg="#f0f0f0").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.lbl_polaridad_ext = tk.Label(frame, text="-", font=("Arial", 10), fg="#34495e", bg="#f0f0f0")
        self.lbl_polaridad_ext.grid(row=1, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Tonalidad:", font=("Arial", 11, "bold"), bg="#f0f0f0").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.lbl_tonalidad = tk.Label(frame, text="-", font=("Arial", 10), fg="#34495e", bg="#f0f0f0")
        self.lbl_tonalidad.grid(row=2, column=1, sticky=tk.W, pady=5)

    def _crear_tabla_justificacion(self):
        frame = ttk.Frame(self.tab_justificacion, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Explicacion del analisis:", font=("Arial", 11, "bold"), bg="#f0f0f0").grid(row=0, column=0, sticky=tk.NW, pady=5)
        self.txt_justificacion = scrolledtext.ScrolledText(frame, height=8, font=("Arial", 10), wrap=tk.WORD)
        self.txt_justificacion.grid(row=0, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Recomendacion de mejora:", font=("Arial", 11, "bold"), bg="#f0f0f0").grid(row=1, column=0, sticky=tk.NW, pady=5)
        self.txt_recomendacion = scrolledtext.ScrolledText(frame, height=8, font=("Arial", 10), wrap=tk.WORD)
        self.txt_recomendacion.grid(row=1, column=1, sticky=tk.W, pady=5)

    def _crear_tabla_historial(self):
        frame = ttk.Frame(self.tab_historial, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # Listbox con scrollbar
        scrollbar = ttk.Scrollbar(frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.list_historial = tk.Listbox(frame, font=("Arial", 10), yscrollcommand=scrollbar.set)
        self.list_historial.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.list_historial.yview)

        self.list_historial.bind("<Double-Button-1>", self.cargar_desde_historial)

        # Boton actualizar historial
        btn_actualizar = tk.Button(
            frame,
            text="Actualizar",
            command=self.actualizar_historial,
            font=("Arial", 10),
            bg="#3498db",
            fg="white"
        )
        btn_actualizar.pack(pady=5)

        self.actualizar_historial()

    def actualizar_historial(self):
        self.list_historial.delete(0, tk.END)
        try:
            archivos = listar_analisis()
            for ruta in archivos:
                self.list_historial.insert(tk.END, f"{ruta.name}")
        except Exception as e:
            self.list_historial.insert(tk.END, f"Error: {str(e)}")

    def cargar_desde_historial(self, event):
        seleccion = self.list_historial.curselection()
        if not seleccion:
            return

        nombre = self.list_historial.get(seleccion[0])
        ruta_json = Path("almacenamiento/resultados/json") / nombre

        try:
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)

            if "basico" in datos:
                self._mostrar_resultados(datos["basico"], datos.get("intermedio", {}), datos.get("avanzado", {}))
                self.barra_estado.config(text=f"Cargado desde historial: {nombre}", fg="blue")
            else:
                messagebox.showinfo("Info", "El archivo no contiene formato completo")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar: {str(e)}")

    def analizar(self):
        texto = self.texto_entrada.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Escribe un texto para analizar")
            return

        if not self.cliente:
            messagebox.showerror("Error", "Cliente no inicializado. Verifica la API key.")
            return

        try:
            self.barra_estado.config(text="Analizando...", fg="orange")
            self.root.update()

            resultado_b = basico(texto, self.cliente)
            resultado_i = intermedio(texto, self.cliente)
            resultado_a = avanzado(texto, self.cliente)

            self.resultados = {
                "basico": resultado_b,
                "intermedio": resultado_i,
                "avanzado": resultado_a
            }
            self.texto_actual = texto

            rutas = guardar_resultado(texto, self.resultados)

            self._mostrar_resultados(resultado_b, resultado_i, resultado_a)
            self.actualizar_historial()

            self.barra_estado.config(text="Analisis completado y guardado automaticamente", fg="green")

        except Exception as e:
            self.barra_estado.config(text=f"Error: {str(e)}", fg="red")
            messagebox.showerror("Error", f"Error al analizar: {str(e)}")

    def _mostrar_resultados(self, basico, intermedio, avanzado):
        # Pestaña Resultados por Nivel
        self.lbl_basico[0].config(text=basico.get("sentimiento", "-").upper(), fg=self._color_sentimiento(basico.get("sentimiento", "")))
        self.lbl_basico[1].config(text="-")
        self.lbl_basico[2].config(text="-")

        self.lbl_intermedio[0].config(text=intermedio.get("sentimiento", "-").upper())
        self.lbl_intermedio[1].config(text=str(intermedio.get("polaridad", "-")))
        self.lbl_intermedio[2].config(text=intermedio.get("intensidad", "-").upper())

        self.lbl_avanzado[0].config(text=avanzado.get("sentimiento_global", "-").upper())
        self.lbl_avanzado[1].config(text=str(avanzado.get("polaridad", "-")))
        self.lbl_avanzado[2].config(text="-")

        # Pestaña Analisis Detallado
        emociones = intermedio.get("emociones", {})
        if emociones:
            texto_emociones = "\n".join([f"  {k}: {v}" for k, v in emociones.items()])
            self.lbl_emociones.config(text=texto_emociones)
        else:
            self.lbl_emociones.config(text="-")

        self.lbl_polaridad_ext.config(text=str(intermedio.get("polaridad", "-")))
        self.lbl_tonalidad.config(text=avanzado.get("tonalidad", "-").upper())

        # Pestaña Justificación & Recomendación
        self.txt_justificacion.delete("1.0", tk.END)
        self.txt_justificacion.insert("1.0", avanzado.get("justificacion", "-"))

        self.txt_recomendacion.delete("1.0", tk.END)
        self.txt_recomendacion.insert("1.0", avanzado.get("recomendacion", "-"))

    def limpiar(self):
        self.texto_entrada.delete("1.0", tk.END)
        self.resultados = {}
        self.texto_actual = ""

        for lbl in self.lbl_basico + self.lbl_intermedio + self.lbl_avanzado:
            lbl.config(text="-", fg="#2c3e50")

        self.lbl_emociones.config(text="-")
        self.lbl_polaridad_ext.config(text="-")
        self.lbl_tonalidad.config(text="-")

        self.txt_justificacion.delete("1.0", tk.END)
        self.txt_recomendacion.delete("1.0", tk.END)

        self.barra_estado.config(text="Campos limpiados", fg="#7f8c8d")

    def guardar_manual(self):
        if not self.resultados:
            messagebox.showwarning("Aviso", "No hay resultados para guardar. Realiza un analisis primero.")
            return

        texto = self.texto_entrada.get("1.0", tk.END).strip()
        if not texto:
            messagebox.showwarning("Aviso", "Escribe un texto para guardar")
            return

        try:
            rutas = guardar_resultado(texto, self.resultados)
            self.actualizar_historial()
            self.barra_estado.config(text=f"Guardado manualmente: {rutas['json']}", fg="green")
            messagebox.showinfo("Guardado", f"Archivos guardados:\nTXT: {rutas['txt']}\nJSON: {rutas['json']}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar: {str(e)}")

    def _color_sentimiento(self, sentimiento):
        colores = {
            "positivo": "#27ae60",
            "negativo": "#e74c3c",
            "neutral": "#95a5a6"
        }
        return colores.get(sentimiento.lower(), "#2c3e50")


if __name__ == "__main__":
    root = tk.Tk()
    app = AppSentimiento(root)
    root.mainloop()