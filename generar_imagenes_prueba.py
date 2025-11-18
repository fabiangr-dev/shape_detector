"""
Script para generar imágenes de prueba con figuras geométricas de colores RGB
Genera 9 imágenes: Cuadrado (Rojo, Verde, Azul), Rectángulo (Rojo, Verde, Azul), Círculo (Rojo, Verde, Azul)
"""

import cv2
import numpy as np
import os


def create_test_images():
    """Crea las 9 imágenes de prueba"""
    
    # Crear carpeta para las imágenes
    output_dir = "imagenes_prueba"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Carpeta '{output_dir}' creada.")
    
    # Dimensiones de la imagen
    width, height = 800, 600
    
    # Colores BGR (OpenCV usa BGR en lugar de RGB)
    colors = {
        "rojo": (0, 0, 255),      # Rojo puro
        "verde": (0, 255, 0),     # Verde puro
        "azul": (255, 0, 0)       # Azul puro
    }
    
    # Generar imágenes
    image_count = 0
    
    for shape_name, shape_func in [
        ("cuadrado", draw_square),
        ("rectangulo", draw_rectangle),
        ("circulo", draw_circle)
    ]:
        for color_name, color_bgr in colors.items():
            # Crear imagen con fondo blanco
            image = np.ones((height, width, 3), dtype=np.uint8) * 255
            
            # Dibujar la figura
            shape_func(image, color_bgr)
            
            # Guardar imagen
            filename = f"{shape_name}_{color_name}.png"
            filepath = os.path.join(output_dir, filename)
            cv2.imwrite(filepath, image)
            
            image_count += 1
            print(f"✓ Creada: {filename}")
    
    print(f"\n✅ Total: {image_count} imágenes generadas en '{output_dir}/'")


def draw_square(image, color):
    """Dibuja un cuadrado centrado"""
    height, width = image.shape[:2]
    size = 300
    top_left = ((width - size) // 2, (height - size) // 2)
    bottom_right = (top_left[0] + size, top_left[1] + size)
    cv2.rectangle(image, top_left, bottom_right, color, -1)


def draw_rectangle(image, color):
    """Dibuja un rectángulo centrado (horizontal)"""
    height, width = image.shape[:2]
    rect_width = 400
    rect_height = 200
    top_left = ((width - rect_width) // 2, (height - rect_height) // 2)
    bottom_right = (top_left[0] + rect_width, top_left[1] + rect_height)
    cv2.rectangle(image, top_left, bottom_right, color, -1)


def draw_circle(image, color):
    """Dibuja un círculo centrado"""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    radius = 200
    cv2.circle(image, center, radius, color, -1)


if __name__ == "__main__":
    print("Generando imágenes de prueba...\n")
    create_test_images()
    print("\n¡Listo! Puedes usar estas imágenes para probar el detector.")
