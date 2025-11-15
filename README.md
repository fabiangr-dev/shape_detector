# 🔍 Detector de Figuras Geométricas

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green.svg)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

</div>

## 📖 Descripción

Aplicación de escritorio moderna en Python con interfaz gráfica PySide6 que utiliza visión por computadora para reconocer y clasificar automáticamente figuras geométricas en imágenes.

## ✨ Características

- 🔷 **Detección Automática**: Reconoce triángulos, cuadrados, rectángulos, círculos, pentágonos y hexágonos
- 🎨 **Colores Distintivos**: Cada tipo de figura se marca con un color diferente
- 🖼️ **Visualización Dual**: Muestra imagen original y procesada lado a lado con panel redimensionable
- 📊 **Tabla de Resultados**: Presenta los datos en formato tabular ordenado
- 📏 **Análisis Completo**: Para cada figura muestra tipo, vértices, área y centro
- 💻 **Interfaz Moderna**: GUI elegante construida con PySide6 (Qt6)
- 💾 **Guardar Resultados**: Exporta la imagen procesada con las figuras detectadas
- 🚀 **Fácil de Usar**: Interfaz intuitiva y simplificada

## 🎨 Código de Colores

| Figura | Color | Criterio |
|--------|-------|----------|
| 🔺 Triángulos | Verde | 3 vértices |
| 🔵 Cuadrados | Azul | 4 vértices, proporción ~1:1 |
| 🟠 Rectángulos | Naranja | 4 vértices |
| 🟣 Pentágonos | Magenta | 5 vértices |
| 🔷 Hexágonos | Cian | 6 vértices |
| 🔴 Círculos | Rojo | Alta circularidad |

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación

1. Clona este repositorio:
```bash
git clone https://github.com/fabiangr-dev/shape_detector.git
cd shape_detector
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

### Ejecución

```bash
python geometric_shape_detector.py
```

## 📋 Uso

1. **Cargar Imagen**: Haz clic en "📂 Cargar imagen" y selecciona una imagen desde tu computadora
2. **Detectar**: Haz clic en "🔍 Detectar figuras" para iniciar el análisis
3. **Resultados**: Revisa las figuras detectadas en la tabla y la imagen procesada
4. **Guardar**: Usa "💾 Guardar resultado" para exportar la imagen con las figuras marcadas
5. **Limpiar**: Usa "🧹 Limpiar" para reiniciar y cargar una nueva imagen

## 🛠️ Tecnologías Utilizadas

- **Python 3.8+**: Lenguaje de programación
- **OpenCV**: Procesamiento de imágenes y detección de contornos
- **NumPy**: Operaciones matemáticas y manipulación de arrays
- **PySide6**: Interfaz gráfica moderna basada en Qt6

## 📂 Estructura del Proyecto

```
shape_detector/
│
├── geometric_shape_detector.py    # Aplicación principal
├── requirements.txt               # Dependencias del proyecto
├── .gitignore                     # Archivos ignorados por Git
├── LICENSE                        # Licencia MIT
└── README.md                      # Este archivo
```

## 💡 Consejos para Mejores Resultados

- ✅ Usa imágenes con **buen contraste** entre figuras y fondo
- ✅ Las figuras deben estar **claramente definidas**
- ✅ Fondo **simple y uniforme** funciona mejor
- ✅ Las figuras deben tener al menos **500 píxeles de área**
- ✅ Evita imágenes borrosas o con mucho ruido

## 💻 Requisitos del Sistema

- **Sistema Operativo**: Windows, Linux, macOS
- **Python**: 3.8 o superior
- **RAM**: Mínimo 2GB
- **Espacio en Disco**: ~100MB (incluyendo dependencias)

## 📦 Dependencias

```
opencv-python>=4.8.0
numpy>=1.24.0
PySide6>=6.5.0
```

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 👤 Autor

**Fabian GR**

## 🌟 Agradecimientos

- OpenCV por su excelente librería de visión por computadora
- Qt/PySide6 por el framework de interfaz gráfica
- La comunidad de Python por las herramientas y recursos

---

<div align="center">

**¡Disfruta detectando figuras geométricas!** 🎉

⭐ Si este proyecto te resultó útil, considera darle una estrella

</div>
