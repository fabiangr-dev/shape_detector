import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QSplitter,
    QStatusBar
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage, QIcon, QPainter, QColor, QPen


class ShapeDetectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control Panel")
        self.setWindowIcon(self._create_icon())
        self.setMinimumSize(1200, 750)
        
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.shapes_list = []
        self.selected_shape = None
        self.selected_color = None
        self.detection_mode = "automatico"  # "automatico" o "manual"
        
        self._setup_ui()
        self._apply_styles()
        self.statusBar().showMessage("Modo Automático: Detecta todas las figuras")
    
    def _create_icon(self):
        """Crea un ícono simple para la aplicación usando QPixmap"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setPen(QPen(QColor(37, 99, 235), 4))
        painter.setBrush(QColor(59, 130, 246))
        painter.drawEllipse(8, 8, 48, 48)
        
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        painter.setBrush(QColor(255, 255, 255))
        painter.drawRect(24, 24, 16, 16)
        
        painter.end()
        return QIcon(pixmap)
    
    def _setup_ui(self):
        """Configura la interfaz gráfica con PySide6"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Selector de modo de detección
        mode_container = QWidget()
        mode_container.setStyleSheet("""
            background-color: #2D3748;
            border-radius: 8px;
            padding: 12px;
        """)
        mode_layout = QHBoxLayout(mode_container)
        mode_layout.setSpacing(12)
        
        mode_label = QLabel("Modo:")
        mode_label.setStyleSheet("""
            color: #E2E8F0;
            font-size: 14px;
            font-weight: bold;
            background: transparent;
        """)
        mode_layout.addWidget(mode_label)
        
        # Botón Modo Automático
        self.auto_mode_btn = QPushButton("Automático")
        self.auto_mode_btn.setMinimumHeight(36)
        self.auto_mode_btn.setMinimumWidth(140)
        self.auto_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: white;
                border: 2px solid #4A5568;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #718096;
            }
        """)
        self.auto_mode_btn.clicked.connect(lambda: self.set_detection_mode("automatico"))
        mode_layout.addWidget(self.auto_mode_btn)
        
        # Botón Modo Manual
        self.manual_mode_btn = QPushButton("Manual")
        self.manual_mode_btn.setMinimumHeight(36)
        self.manual_mode_btn.setMinimumWidth(140)
        self.manual_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #CBD5E0;
                border: 2px solid #4A5568;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #374151;
            }
        """)
        self.manual_mode_btn.clicked.connect(lambda: self.set_detection_mode("manual"))
        mode_layout.addWidget(self.manual_mode_btn)
        
        mode_layout.addStretch()
        
        main_layout.addWidget(mode_container)
        
        # Barra de botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("Cargar imagen")
        self.load_btn.setMinimumHeight(40)
        self.load_btn.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_btn)
        
        self.save_btn = QPushButton("Guardar resultado")
        self.save_btn.setMinimumHeight(40)
        self.save_btn.setEnabled(False)
        self.save_btn.clicked.connect(self.save_result)
        button_layout.addWidget(self.save_btn)
        
        self.clear_btn = QPushButton("Limpiar")
        self.clear_btn.setMinimumHeight(40)
        self.clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(self.clear_btn)
        
        button_layout.addStretch()
        main_layout.addLayout(button_layout)
        
        # Panel imagen procesada (único)
        processed_container = QWidget()
        processed_layout = QVBoxLayout(processed_container)
        processed_layout.setContentsMargins(0, 0, 0, 0)
        processed_label = QLabel("Resultado de Detección")
        processed_label.setStyleSheet("""
            font-weight: bold; 
            font-size: 14px; 
            padding: 8px;
            color: #E2E8F0;
        """)
        processed_layout.addWidget(processed_label)
        
        self.processed_display = QLabel()
        self.processed_display.setAlignment(Qt.AlignCenter)
        self.processed_display.setStyleSheet("""
            background-color: #1A202C; 
            border-radius: 8px;
            border: 2px solid #2D3748;
        """)
        self.processed_display.setMinimumSize(700, 350)
        self.processed_display.setScaledContents(False)
        processed_layout.addWidget(self.processed_display)
        
        main_layout.addWidget(processed_container, stretch=2)
        
        # Control Manual - Sección de selección
        selector_header = QLabel("Control Manual")
        selector_header.setStyleSheet("""
            font-weight: bold; 
            font-size: 15px; 
            padding: 8px;
            color: #E2E8F0;
        """)
        main_layout.addWidget(selector_header)
        
        # Contenedor principal para control manual
        control_container = QWidget()
        control_container.setStyleSheet("""
            background-color: #2D3748;
            border-radius: 8px; 
            padding: 12px;
            border: 2px solid #4A5568;
        """)
        control_layout = QVBoxLayout(control_container)
        control_layout.setSpacing(12)
        
        # Label para figuras
        shapes_label = QLabel("Selecciona una figura:")
        shapes_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #E2E8F0;")
        control_layout.addWidget(shapes_label)
        
        # Contenedor de botones de figuras
        shapes_widget = QWidget()
        shapes_layout = QHBoxLayout(shapes_widget)
        shapes_layout.setSpacing(10)
        shapes_layout.setContentsMargins(0, 0, 0, 0)
        
        # Lista de figuras disponibles
        shapes = [
            ("Cuadrado", "■", "#3B82F6"),
            ("Rectángulo", "▬", "#8B5CF6"),
            ("Círculo", "●", "#EF4444")
        ]
        
        # Crear botones de figuras
        self.shape_buttons = {}
        for shape_name, symbol, color in shapes:
            btn = QPushButton(f"{symbol}\n{shape_name}")
            btn.setMinimumHeight(60)
            btn.setMinimumWidth(150)
            btn.setProperty("shape_name", shape_name)
            btn.setProperty("color", color)
            btn.setProperty("selected", False)
            btn.setStyleSheet(self._get_shape_button_style(color, False))
            btn.clicked.connect(lambda checked, name=shape_name, b=btn: self.shape_selected(name, b))
            shapes_layout.addWidget(btn)
            self.shape_buttons[shape_name] = btn
        
        shapes_layout.addStretch()
        control_layout.addWidget(shapes_widget)
        
        # Label para colores
        colors_label = QLabel("Selecciona un color:")
        colors_label.setStyleSheet("font-weight: bold; font-size: 12px; color: #E2E8F0; margin-top: 4px;")
        control_layout.addWidget(colors_label)
        
        # Contenedor de botones RGB
        colors_widget = QWidget()
        colors_layout = QHBoxLayout(colors_widget)
        colors_layout.setSpacing(10)
        colors_layout.setContentsMargins(0, 0, 0, 0)
        
        # Botones RGB
        rgb_colors = [
            ("Rojo", "R", "#EF4444"),
            ("Verde", "G", "#10B981"),
            ("Azul", "B", "#3B82F6")
        ]
        
        self.color_buttons = []
        for color_name, letter, color_hex in rgb_colors:
            btn = QPushButton(f"{letter}\n{color_name}")
            btn.setMinimumHeight(55)
            btn.setMinimumWidth(150)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: white;
                    color: {color_hex};
                    border: 3px solid {color_hex};
                    border-radius: 12px;
                    padding: 12px;
                    font-size: 15px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color_hex};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: {color_hex};
                    border: 3px solid #1F2937;
                }}
                QPushButton:disabled {{
                    background-color: #F3F4F6;
                    color: #D1D5DB;
                    border: 3px solid #E5E7EB;
                }}
            """)
            btn.setEnabled(False)
            btn.clicked.connect(lambda checked=False, cname=color_name: self.color_selected(cname))
            colors_layout.addWidget(btn)
            self.color_buttons.append(btn)
        
        colors_layout.addStretch()
        control_layout.addWidget(colors_widget)
        
        main_layout.addWidget(control_container)
        
        # Barra de estado
        self.setStatusBar(QStatusBar())
    
    def _apply_styles(self):
        """Aplica estilos modernos a la aplicación (modo oscuro)"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1A202C;
            }
            QWidget {
                color: #E2E8F0;
            }
            QPushButton {
                background-color: #3182CE;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2C5282;
            }
            QPushButton:pressed {
                background-color: #2A4365;
            }
            QPushButton:disabled {
                background-color: #2D3748;
                color: #4A5568;
            }
            QStatusBar {
                background-color: #2D3748;
                color: #A0AEC0;
                font-size: 12px;
            }
            QLabel {
                color: #E2E8F0;
            }
        """)
    
    def _get_shape_button_style(self, color, selected):
        """Genera el estilo para los botones de figura según si están seleccionados"""
        if selected:
            return f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: 4px solid #1F2937;
                    border-radius: 12px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: white;
                    color: {color};
                    border: 3px solid {color};
                    border-radius: 12px;
                    padding: 15px;
                    font-size: 16px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {color};
                    color: white;
                }}
                QPushButton:pressed {{
                    background-color: {color};
                    border: 3px solid #1F2937;
                }}
            """
    
    def load_image(self):
        """Carga una imagen desde el sistema de archivos"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Imagen",
            "",
            "Archivos de Imagen (*.png *.jpg *.jpeg *.bmp *.gif *.tiff);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self.image_path = file_path
            self.original_image = cv2.imread(file_path)
            
            if self.original_image is None:
                QMessageBox.critical(self, "Error", "No se pudo cargar la imagen")
                return
            
            self.save_btn.setEnabled(False)
            self.statusBar().showMessage(f"Imagen cargada: {os.path.basename(file_path)}. Detectando...")
            
            # Detectar automáticamente
            self.detect_shapes()
    
    def display_image(self, cv_image, label):
        """Muestra una imagen en un QLabel"""
        cv_image_rgb = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        h, w, ch = cv_image_rgb.shape
        
        label_size = label.size()
        scale = min(label_size.width() / w, label_size.height() / h) * 0.95
        new_w, new_h = int(w * scale), int(h * scale)
        
        resized = cv2.resize(cv_image_rgb, (new_w, new_h), interpolation=cv2.INTER_AREA)
        
        bytes_per_line = ch * new_w
        q_image = QImage(resized.data, new_w, new_h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        
        label.setPixmap(pixmap)
    
    def get_dominant_color_name(self, cv_image, contour):
        """Detecta el color dominante en la región del contorno"""
        mask = np.zeros(cv_image.shape[:2], dtype=np.uint8)
        cv2.drawContours(mask, [contour], -1, 255, -1)
        
        mean_color = cv2.mean(cv_image, mask=mask)[:3]  # BGR
        b, g, r = mean_color
        
        # Determinar color dominante
        if r > g and r > b and r > 100:
            return "Rojo"
        elif g > r and g > b and g > 100:
            return "Verde"
        elif b > r and b > g and b > 100:
            return "Azul"
        else:
            return None
    
    def detect_shapes(self):
        """Detecta figuras geométricas y sus colores en la imagen"""
        if self.original_image is None:
            QMessageBox.warning(self, "Advertencia", "Primero debes cargar una imagen")
            return
        
        # Validar según el modo
        if self.detection_mode == "manual":
            if not self.selected_shape or not self.selected_color:
                QMessageBox.warning(self, "Advertencia", "En Modo Manual debes seleccionar una figura y un color")
                return
        elif self.detection_mode == "automatico":
            # En modo automático, limpiar cualquier selección previa
            self.selected_shape = None
            self.selected_color = None
        
        self.statusBar().showMessage("Procesando imagen...")
        QApplication.processEvents()
        
        image = self.original_image.copy()
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes_list = []
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < 500:
                continue
            
            perimeter = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.04 * perimeter, True)
            
            M = cv2.moments(contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            vertices = len(approx)
            shape_name = self.identify_shape(vertices, contour, approx)
            
            if shape_name is None:
                continue
            
            color_name = self.get_dominant_color_name(self.original_image, contour)
            
            # Determinar resultado según el modo
            if self.detection_mode == "manual":
                # Modo Manual: validar contra selección
                if shape_name == self.selected_shape and color_name == self.selected_color:
                    detection_result = "PRODUCCIÓN EXITOSA"
                    drawing_color = self.get_color_for_detection(True)
                else:
                    detection_result = "ERROR DE PRODUCCIÓN"
                    drawing_color = self.get_color_for_detection(False)
            else:
                # Modo Automático: solo detectar sin validar
                detection_result = "DETECTADO"
                drawing_color = (0, 255, 0)  # Verde para todos
            
            shapes_list.append({
                'numero': len(shapes_list) + 1,
                'nombre': shape_name,
                'color': color_name if color_name else "Desconocido",
                'resultado': detection_result
            })
            
            cv2.drawContours(image, [approx], -1, drawing_color, 3)
            
            cv2.putText(image, f"#{len(shapes_list)}", (cX - 20, cY - 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, drawing_color, 2)
            cv2.putText(image, shape_name, (cX - 40, cY),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, drawing_color, 2)
            cv2.putText(image, color_name if color_name else "?", (cX - 30, cY + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, drawing_color, 2)
            cv2.putText(image, detection_result, (cX - 80, cY + 40),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.4,
                       (0, 255, 0) if detection_result == "PRODUCCIÓN EXITOSA" else (0, 0, 255), 2)
        
        self.processed_image = image
        self.display_image(image, self.processed_display)
        self.shapes_list = shapes_list
        
        if len(shapes_list) > 0:
            self.save_btn.setEnabled(True)
            if self.detection_mode == "manual":
                success_count = sum(1 for s in shapes_list if s['resultado'] == "PRODUCCIÓN EXITOSA")
                error_count = len(shapes_list) - success_count
                self.statusBar().showMessage(
                    f"Análisis: {len(shapes_list)} figura(s) - {success_count} exitosa(s), {error_count} error(es)")
            else:
                self.statusBar().showMessage(f"Detectadas {len(shapes_list)} figura(s) automáticamente")
        else:
            self.save_btn.setEnabled(False)
            self.statusBar().showMessage("No se detectaron figuras válidas.")
    
    def identify_shape(self, vertices, contour, approx):
        """Identifica el tipo de figura (solo Cuadrado, Rectángulo, Círculo)"""
        if vertices == 4:
            x, y, w, h = cv2.boundingRect(approx)
            aspect_ratio = float(w) / h
            if 0.85 <= aspect_ratio <= 1.15:
                return "Cuadrado"
            else:
                return "Rectángulo"
        elif vertices > 6:
            area = cv2.contourArea(contour)
            perimeter = cv2.arcLength(contour, True)
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity > 0.75:
                return "Círculo"
        return None
    
    def get_color_for_detection(self, is_success):
        """Color para dibujar según si es éxito o error"""
        return (0, 255, 0) if is_success else (128, 128, 128)
    
    def set_detection_mode(self, mode):
        """Cambia el modo de detección entre automático y manual"""
        self.detection_mode = mode
        
        if mode == "automatico":
            # Estilo botón automático activo
            self.auto_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3182CE;
                    color: white;
                    border: 2px solid #3182CE;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #2C5282;
                }
            """)
            # Estilo botón manual inactivo
            self.manual_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #CBD5E0;
                    border: 2px solid #4A5568;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
            """)
            
            # Limpiar selecciones y deshabilitar control manual
            self.selected_shape = None
            self.selected_color = None
            for btn in self.shape_buttons.values():
                color = btn.property("color")
                btn.setProperty("selected", False)
                btn.setStyleSheet(self._get_shape_button_style(color, False))
                btn.setEnabled(False)  # Deshabilitar botones de figura
            for btn in self.color_buttons:
                btn.setEnabled(False)
            
            self.statusBar().showMessage("Modo Automático: Detecta todas las figuras")
        
        else:  # manual
            # Estilo botón manual activo
            self.manual_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: #805AD5;
                    color: white;
                    border: 2px solid #805AD5;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #6B46C1;
                }
            """)
            # Estilo botón automático inactivo
            self.auto_mode_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #CBD5E0;
                    border: 2px solid #4A5568;
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #374151;
                }
            """)
            
            # Habilitar botones de figura en modo manual
            for btn in self.shape_buttons.values():
                btn.setEnabled(True)
            
            self.statusBar().showMessage("Modo Manual: Selecciona figura y color para validar")
    
    def shape_selected(self, shape_name, button):
        """Maneja la selección de una figura geométrica"""
        if self.detection_mode != "manual":
            QMessageBox.information(self, "Info", "Activa el Modo Manual para usar los botones de selección")
            return
        
        for btn in self.shape_buttons.values():
            color = btn.property("color")
            btn.setProperty("selected", False)
            btn.setStyleSheet(self._get_shape_button_style(color, False))
        
        color = button.property("color")
        button.setProperty("selected", True)
        button.setStyleSheet(self._get_shape_button_style(color, True))
        
        self.selected_shape = shape_name
        
        for btn in self.color_buttons:
            btn.setEnabled(True)
        
        self.statusBar().showMessage(f"✓ Figura seleccionada: {shape_name}. Ahora selecciona un color.")
        
        # Redetectar si hay imagen cargada y modo manual
        if self.original_image is not None and self.detection_mode == "manual":
            if self.selected_color:  # Solo si ya hay color seleccionado
                self.detect_shapes()
    
    def color_selected(self, color_name):
        """Maneja la selección de un color RGB"""
        if self.detection_mode != "manual":
            QMessageBox.information(self, "Info", "Activa el Modo Manual para usar los botones de selección")
            return
        
        if not self.selected_shape:
            QMessageBox.warning(self, "Advertencia", "Primero debes seleccionar una figura.")
            return
        
        self.selected_color = color_name
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Selección Completa")
        msg.setText(f"✓ Figura: {self.selected_shape}\n✓ Color: {color_name}")
        msg.setIcon(QMessageBox.Information)
        msg.exec()
        
        self.statusBar().showMessage(
            f"✓ {self.selected_shape} + {color_name} seleccionados. Detectando...")
        
        # Redetectar automáticamente con la nueva selección
        if self.original_image is not None:
            self.detect_shapes()
    
    def save_result(self):
        """Guardar la imagen procesada en disco"""
        if self.processed_image is None:
            QMessageBox.information(self, "Info", "No hay imagen procesada para guardar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Guardar imagen", "resultado.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;Todos (*.*)"
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.processed_image)
                self.statusBar().showMessage(f"Imagen guardada: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar: {e}")
    
    def clear_all(self):
        """Limpia todas las imágenes y resultados"""
        self.processed_display.clear()
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.shapes_list = []
        self.selected_shape = None
        self.selected_color = None
        
        for btn in self.shape_buttons.values():
            color = btn.property("color")
            btn.setProperty("selected", False)
            btn.setStyleSheet(self._get_shape_button_style(color, False))
        
        for btn in self.color_buttons:
            btn.setEnabled(False)
        
        self.save_btn.setEnabled(False)
        self.statusBar().showMessage("Listo para cargar una nueva imagen")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ShapeDetectorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
