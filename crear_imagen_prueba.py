import cv2
import numpy as np


def create_test_image():
    # Crear lienzo blanco
    width, height = 900, 600
    img = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Colores (BGR)
    green = (0, 255, 0)
    blue = (255, 0, 0)
    red = (0, 0, 255)
    orange = (0, 165, 255)
    magenta = (255, 0, 255)
    cyan = (255, 255, 0)
    black = (0, 0, 0)
    
    # Fila superior
    # Triángulo
    pts_triangle = np.array([[100, 180], [150, 80], [200, 180]], np.int32)
    cv2.fillPoly(img, [pts_triangle], green)
    cv2.polylines(img, [pts_triangle], True, black, 2)
    
    # Cuadrado
    cv2.rectangle(img, (280, 80), (400, 200), blue, -1)
    cv2.rectangle(img, (280, 80), (400, 200), black, 2)
    
    # Círculo
    cv2.circle(img, (520, 140), 60, red, -1)
    cv2.circle(img, (520, 140), 60, black, 2)
    
    # Rectángulo horizontal
    cv2.rectangle(img, (650, 100), (850, 180), orange, -1)
    cv2.rectangle(img, (650, 100), (850, 180), black, 2)
    
    # Fila inferior
    # Pentágono
    pts_pentagon = np.array([
        [100, 350],
        [150, 320],
        [180, 370],
        [150, 420],
        [100, 420]
    ], np.int32)
    cv2.fillPoly(img, [pts_pentagon], magenta)
    cv2.polylines(img, [pts_pentagon], True, black, 2)
    
    # Hexágono
    pts_hexagon = np.array([
        [300, 350],
        [350, 330],
        [400, 350],
        [400, 410],
        [350, 430],
        [300, 410]
    ], np.int32)
    cv2.fillPoly(img, [pts_hexagon], cyan)
    cv2.polylines(img, [pts_hexagon], True, black, 2)
    
    # Rectángulo vertical
    cv2.rectangle(img, (490, 310), (570, 470), orange, -1)
    cv2.rectangle(img, (490, 310), (570, 470), black, 2)
    
    # Otro triángulo
    pts_triangle2 = np.array([[700, 320], [750, 450], [650, 450]], np.int32)
    cv2.fillPoly(img, [pts_triangle2], green)
    cv2.polylines(img, [pts_triangle2], True, black, 2)
    
    # Añadir título
    cv2.putText(
        img,
        "Imagen de Prueba - Figuras Geometricas",
        (180, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        black,
        2
    )
    
    return img


def main():
    print("Generando imagen de prueba...")
    
    # Crear imagen
    test_image = create_test_image()
    
    # Guardar imagen
    output_path = "test_shapes.png"
    cv2.imwrite(output_path, test_image)
    
    print(f"Imagen de prueba creada exitosamente: {output_path}")
    print("\nFiguras incluidas:")
    print("  • 2 Triángulos (verde)")
    print("  • 1 Cuadrado (azul)")
    print("  • 1 Círculo (rojo)")
    print("  • 2 Rectángulos (naranja)")
    print("  • 1 Pentágono (magenta)")
    print("  • 1 Hexágono (cian)")


if __name__ == "__main__":
    main()
