import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont
from PIL import Image, ImageTk
import os


class Tooltip:
    """Tooltip simple para widgets Tk/ttk."""
    def __init__(self, widget, text, delay=500):
        self.widget = widget
        self.text = text
        self.delay = delay
        self._after_id = None
        self.tipwindow = None
        widget.bind("<Enter>", self._schedule)
        widget.bind("<Leave>", self._unschedule)
        widget.bind("<ButtonPress>", self._unschedule)

    def _schedule(self, _event=None):
        self._after_id = self.widget.after(self.delay, self._show)

    def _unschedule(self, _event=None):
        if self._after_id:
            self.widget.after_cancel(self._after_id)
            self._after_id = None
        self._hide()

    def _show(self):
        if self.tipwindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox("insert") or (0, 0, 0, 0)
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + cy + 10
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(tw, text=self.text, style="Tooltip.TLabel")
        label.pack(ipadx=8, ipady=5)

    def _hide(self):
        if self.tipwindow:
            self.tipwindow.destroy()
            self.tipwindow = None


class ShapeDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Figuras Geométricas")
        self.root.geometry("1000x720")
        self.root.resizable(True, True)
        self.dark_mode = False
        
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.shapes_list = []
        self.status_var = tk.StringVar(value="Listo")
        self.summary_var = tk.StringVar(value="Sin resultados")

        self._setup_fonts()
        self._setup_style()
        self._setup_menubar()
        
        self.setup_ui()
        self._setup_key_bindings()
    
    def setup_ui(self):
        """Configura la interfaz gráfica moderna con ttk"""
        # Barra de controles
        control_frame = ttk.Frame(self.root, padding=(12, 10))
        control_frame.pack(side=tk.TOP, fill=tk.X)

        self.load_btn = ttk.Button(
            control_frame,
            text="📂  Cargar imagen",
            command=self.load_image,
            style="Success.TButton",
            cursor="hand2",
            width=20
        )
        self.load_btn.pack(side=tk.LEFT)
        Tooltip(self.load_btn, "Abrir una imagen desde el disco")

        self.detect_btn = ttk.Button(
            control_frame,
            text="🔍  Detectar figuras",
            command=self.detect_shapes,
            style="Accent.TButton",
            cursor="hand2",
            state=tk.DISABLED,
            width=22
        )
        self.detect_btn.pack(side=tk.LEFT, padx=(10, 0))
        Tooltip(self.detect_btn, "Analizar la imagen y detectar figuras")

        self.save_btn = ttk.Button(
            control_frame,
            text="💾  Guardar resultado",
            command=self.save_result,
            style="Info.TButton",
            cursor="hand2",
            state=tk.DISABLED,
            width=22
        )
        self.save_btn.pack(side=tk.LEFT, padx=(10, 0))
        Tooltip(self.save_btn, "Guardar la imagen con figuras dibujadas")

        self.clear_btn = ttk.Button(
            control_frame,
            text="🧹  Limpiar",
            command=self.clear_all,
            style="Danger.TButton",
            cursor="hand2",
            width=14
        )
        self.clear_btn.pack(side=tk.LEFT, padx=(10, 0))
        Tooltip(self.clear_btn, "Limpiar imágenes y resultados")

        ttk.Separator(self.root).pack(fill=tk.X)

        # Zona de imágenes con PanedWindow redimensionable
        self.paned = ttk.Panedwindow(self.root, orient=tk.HORIZONTAL)
        self.paned.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=12, pady=12)

        self.original_frame = ttk.Labelframe(self.paned, text="Imagen original", padding=(8, 8))
        self.processed_frame = ttk.Labelframe(self.paned, text="Figuras detectadas", padding=(8, 8))

        # Canvases
        self.original_canvas = tk.Canvas(self.original_frame, bg="#e9eef5", highlightthickness=0)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)

        self.processed_canvas = tk.Canvas(self.processed_frame, bg="#e9eef5", highlightthickness=0)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)

        self.paned.add(self.original_frame, weight=1)
        self.paned.add(self.processed_frame, weight=1)

        # Resultados: resumen + tabla
        results_container = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        results_container.pack(side=tk.BOTTOM, fill=tk.BOTH)

        header = ttk.Frame(results_container)
        header.pack(fill=tk.X)
        ttk.Label(header, text="Resultados del análisis", style="Heading.TLabel").pack(side=tk.LEFT)
        ttk.Label(header, textvariable=self.summary_var, style="Subtle.TLabel").pack(side=tk.RIGHT)

        table_frame = ttk.Frame(results_container)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(6, 0))

        columns = ("numero", "tipo", "vertices", "area", "centro")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=6)
        self.tree.heading("numero", text="#")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("vertices", text="Vértices")
        self.tree.heading("area", text="Área (px²)")
        self.tree.heading("centro", text="Centro (x, y)")
        self.tree.column("numero", width=60, anchor=tk.CENTER)
        self.tree.column("tipo", width=160, anchor=tk.W)
        self.tree.column("vertices", width=90, anchor=tk.CENTER)
        self.tree.column("area", width=130, anchor=tk.E)
        self.tree.column("centro", width=150, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Barra de estado
        status_bar = ttk.Frame(self.root, padding=(12, 6))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_bar, textvariable=self.status_var, style="Subtle.TLabel")
        self.status_label.pack(side=tk.LEFT)

        # Estado inicial
        self._set_status("Listo para cargar una imagen.")

    def _setup_fonts(self):
        """Configura fuentes predeterminadas para una apariencia nativa más cuidada."""
        try:
            default_font = tkfont.nametofont("TkDefaultFont")
            text_font = tkfont.nametofont("TkTextFont")
            fixed_font = tkfont.nametofont("TkFixedFont")
            default_font.configure(family="Segoe UI", size=10)
            text_font.configure(family="Segoe UI", size=10)
            fixed_font.configure(family="Consolas", size=10)
        except Exception:
            pass

    def _setup_style(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Paleta de colores (claro/oscuro)
        if self.dark_mode:
            bg = "#0F172A"  # slate-900
            surface = "#111827"  # gray-900
            fg = "#E5E7EB"  # gray-200
            border = "#374151"
            accent = "#3B82F6"
            success = "#22C55E"
            danger = "#EF4444"
            info = "#0EA5E9"
            select = "#1F3B8A"
        else:
            bg = "#F3F4F6"  # gray-100
            surface = "#FFFFFF"
            fg = "#1F2937"  # gray-800
            border = "#E5E7EB"
            accent = "#2563EB"
            success = "#16A34A"
            danger = "#DC2626"
            info = "#0284C7"
            select = "#DBEAFE"

        self.root.configure(bg=bg)

        style.configure("TFrame", background=bg)
        style.configure("TLabelframe", background=surface, bordercolor=border)
        style.configure("TLabelframe.Label", background=surface, foreground=fg)
        style.configure("TLabel", background=bg, foreground=fg)
        style.configure("Heading.TLabel", background=bg, foreground=fg, font=("Segoe UI", 11, "bold"))
        style.configure("Subtle.TLabel", background=bg, foreground="#6B7280")
        style.configure("Treeview", background=surface, fieldbackground=surface, foreground=fg, bordercolor=border, rowheight=26)
        style.configure("Treeview.Heading", background=surface, foreground=fg)
        style.map("Treeview", background=[("selected", select)])

        # Botones por intención
        style.configure("TButton", padding=8, font=("Segoe UI", 10, "bold"))
        style.configure("Accent.TButton", background=accent, foreground="#FFFFFF")
        style.map("Accent.TButton", background=[("active", accent)], foreground=[("disabled", "#D1D5DB")])
        style.configure("Success.TButton", background=success, foreground="#FFFFFF")
        style.configure("Danger.TButton", background=danger, foreground="#FFFFFF")
        style.configure("Info.TButton", background=info, foreground="#FFFFFF")
        for btn in ("Accent.TButton", "Success.TButton", "Danger.TButton", "Info.TButton"):
            style.map(btn, relief=[("pressed", "sunken")])

        # Tooltip
        style.configure("Tooltip.TLabel", background="#111827" if self.dark_mode else "#111827",
                        foreground="#F9FAFB", borderwidth=1, padding=(8, 5))

    def _setup_menubar(self):
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Cargar imagen	Ctrl+O", command=self.load_image)
        filemenu.add_command(label="Detectar figuras	Ctrl+D", command=self.detect_shapes, state=tk.DISABLED)
        filemenu.add_separator()
        filemenu.add_command(label="Salir	Ctrl+Q", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=filemenu)

        viewmenu = tk.Menu(menubar, tearoff=0)
        viewmenu.add_command(label="Alternar modo claro/oscuro", command=self.toggle_theme)
        menubar.add_cascade(label="Ver", menu=viewmenu)

        helpmenu = tk.Menu(menubar, tearoff=0)
        helpmenu.add_command(label="Acerca de", command=lambda: messagebox.showinfo(
            "Acerca de", "Detector de Figuras Geométricas\nMejorado con una interfaz más agradable."
        ))
        menubar.add_cascade(label="Ayuda", menu=helpmenu)

        self.root.config(menu=menubar)
        self._filemenu_detect_item = filemenu

    def _setup_key_bindings(self):
        self.root.bind_all("<Control-o>", lambda e: self.load_image())
        self.root.bind_all("<Control-d>", lambda e: self.detect_shapes())
        self.root.bind_all("<Control-l>", lambda e: self.clear_all())
        self.root.bind_all("<Control-q>", lambda e: self.root.quit())

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self._setup_style()
        # refrescar canvases de fondo acorde a tema
        bg_canvas = "#1f2937" if self.dark_mode else "#e9eef5"
        for c in (self.original_canvas, self.processed_canvas):
            c.configure(bg=bg_canvas)
        self._set_status("Modo oscuro activado" if self.dark_mode else "Modo claro activado")

    def _set_status(self, text):
        self.status_var.set(text)
    
    def load_image(self):
        """Carga una imagen desde el sistema de archivos"""
        file_path = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=[
                ("Archivos de Imagen", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            
            if self.original_image is None:
                messagebox.showerror("Error", "No se pudo cargar la imagen")
                return
            
            self.display_image(self.original_image, self.original_canvas)
            self.detect_btn.config(state=tk.NORMAL)
            try:
                self._filemenu_detect_item.entryconfig(1, state=tk.NORMAL)
            except Exception:
                pass
            self.save_btn.config(state=tk.DISABLED)
            self._clear_results_table()
            self.summary_var.set("Imagen cargada: " + os.path.basename(file_path))
            self._set_status("Imagen cargada correctamente")
    
    def display_image(self, cv_image, canvas):
        """Muestra una imagen en un canvas específico"""
        # Convertir de BGR a RGB
        cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        
        # Obtener dimensiones del canvas
        canvas.update()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        
        # Redimensionar imagen manteniendo aspecto
        h, w = cv_image_rgb.shape[:2]
        scale = min(canvas_width / w, canvas_height / h) * 0.95
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(cv_image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        # Convertir a formato PIL y mostrar
        pil_image = Image.fromarray(resized)
        photo = ImageTk.PhotoImage(pil_image)
        
        canvas.delete("all")
        canvas.create_image(canvas_width // 2, canvas_height // 2, image=photo, anchor=tk.CENTER)
        canvas.image = photo  # Mantener referencia
    
    def detect_shapes(self):
        """Detecta figuras geométricas en la imagen y llena la tabla."""
        if self.original_image is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar una imagen")
            return
        
        # Limpiar resultados anteriores
        self._set_status("Procesando imagen...")
        self._clear_results_table()
        self.summary_var.set("Procesando...")
        self.root.update_idletasks()
        
        # Crear copia de la imagen
        image = self.original_image.copy()
        
        # Preprocesamiento
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes_list = []
        
        for i, contour in enumerate(contours):
            # Filtrar contornos muy pequeños
            area = cv2.contourArea(contour)
            if area < 500:
                continue
            
            # Aproximar el contorno
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            
            # Calcular el centro del contorno
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            # Identificar la figura según el número de vértices
            vertices = len(approx)
            shape_name = self.identify_shape(vertices, contour, approx)
            
            # Guardar información de la figura
            shapes_list.append({
                'numero': len(shapes_list) + 1,
                'nombre': shape_name,
                'area': area,
                'vertices': vertices,
                'centro': (cX, cY)
            })
            
            # Dibujar el contorno y el número
            color = self.get_color_for_shape(shape_name)
            cv2.drawContours(image, [approx], -1, color, 3)
            
            # Añadir número de figura
            cv2.putText(
                image,
                f"#{len(shapes_list)}",
                (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )
            
            # Añadir texto con el nombre de la figura
            cv2.putText(
                image,
                shape_name,
                (cX - 40, cY + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
        
        # Mostrar imagen procesada
        self.processed_image = image
        self.display_image(image, self.processed_canvas)
        
        # Llenar tabla de resultados
        self.shapes_list = shapes_list
        for shape in shapes_list:
            self.tree.insert("", tk.END, values=(
                shape['numero'],
                shape['nombre'],
                shape['vertices'],
                f"{shape['area']:.0f}",
                f"({shape['centro'][0]}, {shape['centro'][1]})"
            ))

        total_shapes = len(shapes_list)
        if total_shapes > 0:
            self.summary_var.set(f"Total: {total_shapes} figura(s)")
            self.save_btn.config(state=tk.NORMAL)
            self._set_status("Análisis completado")
        else:
            self.summary_var.set("No se detectaron figuras. Prueba con mayor contraste.")
            self.save_btn.config(state=tk.DISABLED)
            self._set_status("Sin resultados")
    
    def identify_shape(self, vertices, contour, approx):
        """Identifica el tipo de figura según sus características"""
        if vertices == 3:
            return "Triangulo"
        
        elif vertices == 4:
            # Verificar si es cuadrado o rectángulo
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            
            if 0.95 <= aspect_ratio <= 1.05:
                return "Cuadrado"
            else:
                return "Rectangulo"
        
        elif vertices == 5:
            return "Pentagono"
        
        elif vertices == 6:
            return "Hexagono"

        elif vertices > 6:
            # Verificar si es un círculo
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity > 0.8:
                return "Circulo"
            else:
                return f"Poligono ({vertices} lados)"

        return "Figura desconocida"
    
    def get_color_for_shape(self, shape_name):
        """Asigna un color específico a cada tipo de figura"""
        colors = {
            "Triangulo": (0, 255, 0),      # Verde
            "Cuadrado": (255, 0, 0),       # Azul
            "Rectangulo": (0, 165, 255),   # Naranja
            "Pentagono": (255, 0, 255),    # Magenta
            "Hexagono": (255, 255, 0),     # Cian
            "Circulo": (0, 0, 255),        # Rojo
        }
        
        return colors.get(shape_name, (255, 255, 255))  # Blanco por defecto
    
    def clear_all(self):
        """Limpia todas las imágenes y resultados"""
        self.original_canvas.delete("all")
        self.processed_canvas.delete("all")
        self._clear_results_table()
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.detect_btn.config(state=tk.DISABLED)
        try:
            self._filemenu_detect_item.entryconfig(1, state=tk.DISABLED)
        except Exception:
            pass
        self.save_btn.config(state=tk.DISABLED)
        self.summary_var.set("Sin resultados")
        self._set_status("Listo para cargar una nueva imagen.")

    def _clear_results_table(self):
        for item in getattr(self, 'tree', []).get_children() if hasattr(self, 'tree') else []:
            self.tree.delete(item)
        self.shapes_list = []

    def save_result(self):
        """Guardar la imagen procesada en disco"""
        if self.processed_image is None:
            messagebox.showinfo("Info", "No hay imagen procesada para guardar.")
            return
        initial = "resultado.png"
        out_path = filedialog.asksaveasfilename(
            title="Guardar imagen",
            defaultextension=".png",
            initialfile=initial,
            filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp"), ("Todos", "*.*")]
        )
        if out_path:
            ext = os.path.splitext(out_path)[1].lower()
            save_img = self.processed_image
            # Convert BGR to RGB for PIL save, but cv2.imwrite expects BGR; use cv2 for simplicity
            try:
                cv2.imwrite(out_path, save_img)
                self._set_status(f"Imagen guardada en {os.path.basename(out_path)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la imagen: {e}")


def main():
    root = tk.Tk()
    app = ShapeDetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
