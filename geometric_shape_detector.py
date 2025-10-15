import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import os


class ShapeDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Detector de Figuras Geométricas")
        self.root.geometry("900x700")
        self.root.resizable(True, True)
        
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Configura la interfaz gráfica"""
        # Frame superior para botones
        control_frame = tk.Frame(self.root, bg="#f0f0f0", padx=10, pady=10)
        control_frame.pack(side=tk.TOP, fill=tk.X)
        
        # Botón para cargar imagen
        self.load_btn = tk.Button(
            control_frame,
            text="📁 Cargar Imagen",
            command=self.load_image,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para detectar figuras
        self.detect_btn = tk.Button(
            control_frame,
            text="🔍 Detectar Figuras",
            command=self.detect_shapes,
            bg="#2196F3",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2",
            state=tk.DISABLED
        )
        self.detect_btn.pack(side=tk.LEFT, padx=5)
        
        # Botón para limpiar
        self.clear_btn = tk.Button(
            control_frame,
            text="🗑️ Limpiar",
            command=self.clear_all,
            bg="#f44336",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            cursor="hand2"
        )
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
        # Frame para las imágenes
        images_frame = tk.Frame(self.root, bg="white")
        images_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para imagen original
        self.original_frame = tk.LabelFrame(
            images_frame,
            text="Imagen Original",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=5,
            pady=5
        )
        self.original_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.original_canvas = tk.Canvas(self.original_frame, bg="gray90", width=400, height=400)
        self.original_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Canvas para imagen procesada
        self.processed_frame = tk.LabelFrame(
            images_frame,
            text="Figuras Detectadas",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=5,
            pady=5
        )
        self.processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        self.processed_canvas = tk.Canvas(self.processed_frame, bg="gray90", width=400, height=400)
        self.processed_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Frame inferior para resultados
        self.results_frame = tk.LabelFrame(
            self.root,
            text="Resultados del Análisis",
            font=("Arial", 11, "bold"),
            bg="white",
            padx=10,
            pady=10
        )
        self.results_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.results_text = tk.Text(
            self.results_frame,
            height=6,
            font=("Courier", 10),
            bg="#f9f9f9",
            wrap=tk.WORD
        )
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar para resultados
        scrollbar = tk.Scrollbar(self.results_text)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.results_text.yview)
    
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
            self.results_text.delete(1.0, tk.END)
            self.results_text.insert(tk.END, f"Imagen cargada: {os.path.basename(file_path)}\n")
    
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
        """Detecta figuras geométricas en la imagen"""
        if self.original_image is None:
            messagebox.showwarning("Advertencia", "Primero debes cargar una imagen")
            return
        
        # Limpiar resultados anteriores
        self.results_text.delete(1.0, tk.END)
        self.results_text.insert(tk.END, "Procesando imagen...\n\n")
        self.root.update()
        
        # Crear copia de la imagen
        image = self.original_image.copy()
        
        # Preprocesamiento
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        # Encontrar contornos
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes_found = {}
        total_shapes = 0
        
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
            
            # Contar figuras
            if shape_name in shapes_found:
                shapes_found[shape_name] += 1
            else:
                shapes_found[shape_name] = 1
            
            total_shapes += 1
            
            # Dibujar el contorno y el nombre
            color = self.get_color_for_shape(shape_name)
            cv2.drawContours(image, [approx], -1, color, 3)
            
            # Añadir texto con el nombre de la figura
            cv2.putText(
                image,
                shape_name,
                (cX - 40, cY),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
        
        # Mostrar imagen procesada
        self.processed_image = image
        self.display_image(image, self.processed_canvas)
        
        # Mostrar resultados
        self.results_text.insert(tk.END, f"Total de figuras detectadas: {total_shapes}\n\n")
        self.results_text.insert(tk.END, "Resumen por tipo de figura:\n")
        self.results_text.insert(tk.END, "-" * 50 + "\n")
        
        for shape, count in sorted(shapes_found.items()):
            self.results_text.insert(tk.END, f"  • {shape}: {count}\n")
        
        if total_shapes == 0:
            self.results_text.insert(tk.END, "\n⚠️ No se detectaron figuras geométricas claras.\n")
            self.results_text.insert(tk.END, "Intenta con una imagen con mayor contraste.\n")
    
    def identify_shape(self, vertices, contour, approx):
        """Identifica el tipo de figura según sus características"""
        if vertices == 3:
            return "Triángulo"
        
        elif vertices == 4:
            # Verificar si es cuadrado o rectángulo
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            
            if 0.95 <= aspect_ratio <= 1.05:
                return "Cuadrado"
            else:
                return "Rectángulo"
        
        elif vertices == 5:
            return "Pentágono"
        
        elif vertices == 6:
            return "Hexágono"
        
        elif vertices > 6:
            # Verificar si es un círculo
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            
            if circularity > 0.8:
                return "Círculo"
            else:
                return f"Polígono ({vertices} lados)"
        
        return "Figura desconocida"
    
    def get_color_for_shape(self, shape_name):
        """Asigna un color específico a cada tipo de figura"""
        colors = {
            "Triángulo": (0, 255, 0),      # Verde
            "Cuadrado": (255, 0, 0),       # Azul
            "Rectángulo": (0, 165, 255),   # Naranja
            "Pentágono": (255, 0, 255),    # Magenta
            "Hexágono": (255, 255, 0),     # Cian
            "Círculo": (0, 0, 255),        # Rojo
        }
        
        return colors.get(shape_name, (255, 255, 255))  # Blanco por defecto
    
    def clear_all(self):
        """Limpia todas las imágenes y resultados"""
        self.original_canvas.delete("all")
        self.processed_canvas.delete("all")
        self.results_text.delete(1.0, tk.END)
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.detect_btn.config(state=tk.DISABLED)
        self.results_text.insert(tk.END, "Listo para cargar una nueva imagen.\n")


def main():
    root = tk.Tk()
    app = ShapeDetectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
