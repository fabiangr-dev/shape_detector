import sys
import os
import cv2
import numpy as np
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem, QFileDialog,
    QMessageBox, QSplitter, QStatusBar, QHeaderView
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage


class ShapeDetectorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Detector de Figuras Geométricas")
        self.setMinimumSize(1000, 700)
        
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.shapes_list = []
        
        self._setup_ui()
        self._apply_styles()
        self.statusBar().showMessage("Listo para cargar una imagen")
    
    def _setup_ui(self):
        """Configura la interfaz gráfica con PySide6"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)
        
        # Barra de botones
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.load_btn = QPushButton("Cargar imagen")
        self.load_btn.setMinimumHeight(40)
        self.load_btn.clicked.connect(self.load_image)
        button_layout.addWidget(self.load_btn)
        
        self.detect_btn = QPushButton("Detectar figuras")
        self.detect_btn.setMinimumHeight(40)
        self.detect_btn.setEnabled(False)
        self.detect_btn.clicked.connect(self.detect_shapes)
        button_layout.addWidget(self.detect_btn)
        
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
        
        # Splitter para imágenes
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel imagen original
        original_container = QWidget()
        original_layout = QVBoxLayout(original_container)
        original_layout.setContentsMargins(0, 0, 0, 0)
        original_label = QLabel("Imagen original")
        original_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 6px;")
        original_layout.addWidget(original_label)
        
        self.original_display = QLabel()
        self.original_display.setAlignment(Qt.AlignCenter)
        self.original_display.setStyleSheet("background-color: #E9EEF5; border-radius: 6px;")
        self.original_display.setMinimumSize(300, 300)
        self.original_display.setScaledContents(False)
        original_layout.addWidget(self.original_display)
        
        # Panel imagen procesada
        processed_container = QWidget()
        processed_layout = QVBoxLayout(processed_container)
        processed_layout.setContentsMargins(0, 0, 0, 0)
        processed_label = QLabel("Figuras detectadas")
        processed_label.setStyleSheet("font-weight: bold; font-size: 13px; padding: 6px;")
        processed_layout.addWidget(processed_label)
        
        self.processed_display = QLabel()
        self.processed_display.setAlignment(Qt.AlignCenter)
        self.processed_display.setStyleSheet("background-color: #E9EEF5; border-radius: 6px;")
        self.processed_display.setMinimumSize(300, 300)
        self.processed_display.setScaledContents(False)
        processed_layout.addWidget(self.processed_display)
        
        splitter.addWidget(original_container)
        splitter.addWidget(processed_container)
        splitter.setSizes([500, 500])
        main_layout.addWidget(splitter, stretch=2)
        
        # Tabla de resultados
        results_header = QLabel("Resultados del análisis")
        results_header.setStyleSheet("font-weight: bold; font-size: 13px; padding: 6px;")
        main_layout.addWidget(results_header)
        
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["#", "Tipo", "Vértices", "Área (px²)", "Centro (x, y)"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.results_table.setMaximumHeight(200)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.results_table.setSelectionBehavior(QTableWidget.SelectRows)
        main_layout.addWidget(self.results_table, stretch=1)
        
        # Barra de estado
        self.setStatusBar(QStatusBar())
    
    def _apply_styles(self):
        """Aplica estilos modernos a la aplicación"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F8F9FA;
            }
            QPushButton {
                background-color: #2563EB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1D4ED8;
            }
            QPushButton:pressed {
                background-color: #1E40AF;
            }
            QPushButton:disabled {
                background-color: #CBD5E1;
                color: #94A3B8;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #E5E7EB;
                border-radius: 6px;
                gridline-color: #E5E7EB;
            }
            QTableWidget::item {
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: #DBEAFE;
                color: #1E40AF;
            }
            QHeaderView::section {
                background-color: #F3F4F6;
                padding: 10px;
                border: none;
                border-bottom: 2px solid #E5E7EB;
                font-weight: bold;
                color: #374151;
            }
            QStatusBar {
                background-color: #F3F4F6;
                color: #6B7280;
                font-size: 12px;
            }
        """)
    
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
            
            self.display_image(self.original_image, self.original_display)
            self.detect_btn.setEnabled(True)
            self.save_btn.setEnabled(False)
            self._clear_results_table()
            self.statusBar().showMessage(f"Imagen cargada: {os.path.basename(file_path)}")
    
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
    
    def detect_shapes(self):
        """Detecta figuras geométricas en la imagen"""
        if self.original_image is None:
            QMessageBox.warning(self, "Advertencia", "Primero debes cargar una imagen")
            return
        
        self.statusBar().showMessage("Procesando imagen...")
        self._clear_results_table()
        QApplication.processEvents()
        
        image = self.original_image.copy()
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        shapes_list = []
        
        for i, contour in enumerate(contours):
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
            
            shapes_list.append({
                'numero': len(shapes_list) + 1,
                'nombre': shape_name,
                'area': area,
                'vertices': vertices,
                'centro': (cX, cY)
            })
            
            color = self.get_color_for_shape(shape_name)
            cv2.drawContours(image, [approx], -1, color, 3)
            
            cv2.putText(
                image,
                f"#{len(shapes_list)}",
                (cX - 20, cY - 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.8,
                color,
                2
            )
            
            cv2.putText(
                image,
                shape_name,
                (cX - 40, cY + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2
            )
        
        self.processed_image = image
        self.display_image(image, self.processed_display)
        
        self.shapes_list = shapes_list
        self.results_table.setRowCount(len(shapes_list))
        
        for i, shape in enumerate(shapes_list):
            self.results_table.setItem(i, 0, QTableWidgetItem(str(shape['numero'])))
            self.results_table.setItem(i, 1, QTableWidgetItem(shape['nombre']))
            self.results_table.setItem(i, 2, QTableWidgetItem(str(shape['vertices'])))
            self.results_table.setItem(i, 3, QTableWidgetItem(f"{shape['area']:.0f}"))
            self.results_table.setItem(i, 4, QTableWidgetItem(f"({shape['centro'][0]}, {shape['centro'][1]})"))
            
            for col in range(5):
                self.results_table.item(i, col).setTextAlignment(Qt.AlignCenter)
        
        total_shapes = len(shapes_list)
        if total_shapes > 0:
            self.save_btn.setEnabled(True)
            self.statusBar().showMessage(f"Análisis completado - {total_shapes} figura(s) detectada(s)")
        else:
            self.save_btn.setEnabled(False)
            self.statusBar().showMessage("No se detectaron figuras. Prueba con una imagen de mayor contraste.")
    
    def identify_shape(self, vertices, contour, approx):
        """Identifica el tipo de figura según sus características"""
        if vertices == 3:
            return "Triángulo"
        elif vertices == 4:
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
            "Triángulo": (0, 255, 0),
            "Cuadrado": (255, 0, 0),
            "Rectángulo": (0, 165, 255),
            "Pentágono": (255, 0, 255),
            "Hexágono": (255, 255, 0),
            "Círculo": (0, 0, 255),
        }
        return colors.get(shape_name, (255, 255, 255))
    
    def save_result(self):
        """Guardar la imagen procesada en disco"""
        if self.processed_image is None:
            QMessageBox.information(self, "Info", "No hay imagen procesada para guardar.")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar imagen",
            "resultado.png",
            "PNG (*.png);;JPEG (*.jpg *.jpeg);;BMP (*.bmp);;Todos los archivos (*.*)"
        )
        
        if file_path:
            try:
                cv2.imwrite(file_path, self.processed_image)
                self.statusBar().showMessage(f"Imagen guardada: {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo guardar la imagen: {e}")
    
    def clear_all(self):
        """Limpia todas las imágenes y resultados"""
        self.original_display.clear()
        self.processed_display.clear()
        self._clear_results_table()
        self.image_path = None
        self.original_image = None
        self.processed_image = None
        self.detect_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.statusBar().showMessage("Listo para cargar una nueva imagen")
    
    def _clear_results_table(self):
        """Limpia la tabla de resultados"""
        self.results_table.setRowCount(0)
        self.shapes_list = []


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = ShapeDetectorApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
