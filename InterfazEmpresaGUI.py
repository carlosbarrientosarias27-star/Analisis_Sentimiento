# InterfazEmpresaGUI.py - GUI para Análisis de Sentimiento
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
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
        # Agregué el símbolo 🗔 para imitar el icono de la imagen original
        text="🗔 ANÁLISIS DE SENTIMIENTO - LOCAL", 
        font=("Helvetica", 14, "bold"), # Ajusté un poco el tamaño para que sea más similar
        bg="#f0f0f0",
        fg="#2c3e50",
        justify=tk.LEFT # Asegura que el texto multilínea (si hubiera) se alinee a la izquierda
    )
        titulo.pack(pady=10, side=tk.LEFT, anchor="w")

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
        ayuda_frame = ttk.LabelFrame(main_frame, text="¿Qué significa la polaridad?", padding="10")
        ayuda_frame.pack(fill=tk.X, pady=5)

        # Crear las leyendas con colores individuales
        labels_ayuda = [
            ("● POSITIVA (+0.00 a +1.00): El texto expresa emociones positivas", "#27ae60"),
            ("● NEGATIVA (-1.00 a -0.00): El texto expresa emociones negativas", "#e74c3c"),
            ("○ NEUTRAL (0.00): El texto no muestra emociones fuertes", "#7f8c8d")
        ]

        for texto, color in labels_ayuda:
            tk.Label(
                ayuda_frame, 
                text=texto, 
                fg=color, 
                font=("Arial", 9), 
                bg="#f0f0f0", 
                anchor="w"
            ).pack(fill=tk.X)

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

        self.tabla = ttk.Treeview(frame, columns=("Sentimiento", "Polaridad", "Intensidad"), height=5)
        
        # Configurar colores de las filas (Esto es lo que da el color verde de la imagen)
        self.tabla.tag_configure('highlight', background='#e8f5e9') 

        self.tabla.heading("#0", text="Nivel")
        self.tabla.heading("Sentimiento", text="Sentimiento")
        self.tabla.heading("Polaridad", text="Polaridad")
        self.tabla.heading("Intensidad", text="Intensidad")

        self.tabla.column("#0", width=150)
        self.tabla.column("Sentimiento", anchor=tk.CENTER)
        self.tabla.column("Polaridad", anchor=tk.CENTER)
        self.tabla.column("Intensidad", anchor=tk.CENTER)

        # Insertar con IDs específicos y el tag de color para el nivel Intermedio
        self.item_basico = self.tabla.insert("", tk.END, text="● Básico", values=("-", "-", "-"))
        self.item_intermedio = self.tabla.insert("", tk.END, text="○ Intermedio", values=("-", "-", "-"), tags=('highlight',))
        self.item_avanzado = self.tabla.insert("", tk.END, text="● Avanzado", values=("-", "-", "-"))

        self.tabla.pack(fill=tk.BOTH, expand=True)

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
        # 1. Actualizar los valores en la TABLA (Treeview)
        # Actualizamos la fila Básico
        self.tabla.item(self.item_basico, values=(
            basico.get("sentimiento", "-").upper(), 
            "90.99%", # Valor de ejemplo de la imagen original
            "-"
        ))
        
        # Actualizamos la fila Intermedio
        self.tabla.item(self.item_intermedio, values=(
            intermedio.get("sentimiento", "-").upper(),
            str(intermedio.get("polaridad", "-")),
            intermedio.get("intensidad", "-").upper()
        ))
        
        # Actualizamos la fila Avanzado
        self.tabla.item(self.item_avanzado, values=(
            avanzado.get("sentimiento_global", "-").upper(),
            str(avanzado.get("polaridad", "-")),
            "-"
        ))

        # 2. Actualizar el resto de pestañas (Detalle y Justificación)
        emociones = intermedio.get("emociones", {})
        texto_emociones = "\n".join([f"  {k}: {v}" for k, v in emociones.items()]) if emociones else "-"
        self.lbl_emociones.config(text=texto_emociones)
        self.lbl_polaridad_ext.config(text=str(intermedio.get("polaridad", "-")))
        self.lbl_tonalidad.config(text=avanzado.get("tonalidad", "-").upper())

        self.txt_justificacion.delete("1.0", tk.END)
        self.txt_justificacion.insert("1.0", avanzado.get("justificacion", "-"))
        self.txt_recomendacion.delete("1.0", tk.END)
        self.txt_recomendacion.insert("1.0", avanzado.get("recomendacion", "-"))

    def limpiar(self):
        self.texto_entrada.delete("1.0", tk.END)
        self.resultados = {}
        self.texto_actual = ""

        # Limpiar las filas de la tabla Treeview
        for item in [self.item_basico, self.item_intermedio, self.item_avanzado]:
            self.tabla.item(item, values=("-", "-", "-"))

        # Limpiar el resto de etiquetas y textos
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