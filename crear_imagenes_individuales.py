import cv2
import numpy as np
import os

def crear_imagen_con_figura(forma, nombre_archivo, tamaño=(600, 600)):
    """
    Args:
        forma: tipo de figura ('triangulo', 'cuadrado', 'rectangulo', 'pentagono', 'hexagono', 'circulo')
        nombre_archivo: nombre del archivo de salida
        tamaño: tupla con (ancho, alto) de la imagen
    """
    # Crear imagen blanca
    img = np.ones((tamaño[1], tamaño[0], 3), dtype=np.uint8) * 255
    
    # Centro de la imagen
    centro_x, centro_y = tamaño[0] // 2, tamaño[1] // 2
    
    # Color de la figura (azul oscuro)
    color = (180, 100, 50)
    grosor = 3
    relleno = -1  # -1 para rellenar, grosor para solo contorno
    
    if forma == 'triangulo':
        # Triángulo equilátero
        lado = 200
        altura = int(lado * np.sqrt(3) / 2)
        pts = np.array([
            [centro_x, centro_y - altura // 2],
            [centro_x - lado // 2, centro_y + altura // 2],
            [centro_x + lado // 2, centro_y + altura // 2]
        ], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(img, [pts], color)
        cv2.polylines(img, [pts], True, (0, 0, 0), 2)
        
    elif forma == 'cuadrado':
        # Cuadrado
        lado = 200
        top_left = (centro_x - lado // 2, centro_y - lado // 2)
        bottom_right = (centro_x + lado // 2, centro_y + lado // 2)
        cv2.rectangle(img, top_left, bottom_right, color, relleno)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 2)
        
    elif forma == 'rectangulo':
        # Rectángulo
        ancho, alto = 250, 150
        top_left = (centro_x - ancho // 2, centro_y - alto // 2)
        bottom_right = (centro_x + ancho // 2, centro_y + alto // 2)
        cv2.rectangle(img, top_left, bottom_right, color, relleno)
        cv2.rectangle(img, top_left, bottom_right, (0, 0, 0), 2)
        
    elif forma == 'pentagono':
        # Pentágono regular
        radio = 120
        pts = []
        for i in range(5):
            angulo = i * 2 * np.pi / 5 - np.pi / 2
            x = int(centro_x + radio * np.cos(angulo))
            y = int(centro_y + radio * np.sin(angulo))
            pts.append([x, y])
        pts = np.array(pts, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(img, [pts], color)
        cv2.polylines(img, [pts], True, (0, 0, 0), 2)
        
    elif forma == 'hexagono':
        # Hexágono regular
        radio = 120
        pts = []
        for i in range(6):
            angulo = i * 2 * np.pi / 6
            x = int(centro_x + radio * np.cos(angulo))
            y = int(centro_y + radio * np.sin(angulo))
            pts.append([x, y])
        pts = np.array(pts, np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.fillPoly(img, [pts], color)
        cv2.polylines(img, [pts], True, (0, 0, 0), 2)
        
    elif forma == 'circulo':
        # Círculo
        radio = 120
        cv2.circle(img, (centro_x, centro_y), radio, color, relleno)
        cv2.circle(img, (centro_x, centro_y), radio, (0, 0, 0), 2)
    
    # Guardar la imagen
    cv2.imwrite(nombre_archivo, img)
    print(f"✓ Creada: {nombre_archivo}")
    
    return img


def main():
    """Función principal para crear todas las imágenes de ejemplo"""
    print("\n" + "=" * 60)
    print("  GENERADOR DE IMÁGENES DE EJEMPLO")
    print("  Una figura por imagen")
    print("=" * 60 + "\n")
    
    # Crear carpeta para las imágenes si no existe
    carpeta_salida = "ejemplos"
    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)
        print(f" Carpeta creada: {carpeta_salida}\n")
    
    # Lista de figuras a crear
    figuras = [
        ('triangulo', 'ejemplo_triangulo.png'),
        ('cuadrado', 'ejemplo_cuadrado.png'),
        ('rectangulo', 'ejemplo_rectangulo.png'),
        ('pentagono', 'ejemplo_pentagono.png'),
        ('hexagono', 'ejemplo_hexagono.png'),
        ('circulo', 'ejemplo_circulo.png')
    ]
    
    print("Generando imágenes...\n")
    
    # Crear cada imagen
    for forma, nombre in figuras:
        ruta_completa = os.path.join(carpeta_salida, nombre)
        crear_imagen_con_figura(forma, ruta_completa)
    
    print("\n" + "=" * 60)
    print(f"¡Completado! Se crearon {len(figuras)} imágenes")
    print(f"Ubicación: {os.path.abspath(carpeta_salida)}")
    print("=" * 60 + "\n")
    


if __name__ == "__main__":
    main()
