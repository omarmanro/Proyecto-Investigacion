from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QVBoxLayout, QStyleFactory, QHBoxLayout, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6 import QtCore
from PyQt6.QtCore import *
import sys



app = QApplication(sys.argv)
app.setStyle('windowsvista')

class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        

        self.setWindowTitle("Weather Info")
        self.setStyleSheet("background-color: #88BDF2;")
        #self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        
        widget = QWidget()
        layout = QVBoxLayout()
        layout1 = QVBoxLayout()
        layout2 = QVBoxLayout()
        layout3 = QHBoxLayout()

        
        wind_label = QLabel("Viento:")
        wind_edit = QLineEdit()
        wind_edit.setFrame(False)
        
        temperature_label = QLabel("Temperatura:")
        temperature_edit = QLineEdit()
        temperature_edit.setFrame(False)
        
        sensation_label = QLabel("Sensación:")
        sensation_edit = QLineEdit()
        sensation_edit.setFrame(False)

        precipitation_label = QLabel("Precipitacion:")
        precipitation_edit = QLineEdit()
        precipitation_edit.setFrame(False)

        humudity_label = QLabel("Humedad:")
        humudity_edit = QLineEdit()
        humudity_edit.setFrame(False)

        cloudiness_label = QLabel("Nubosidad:")
        cloudiness_edit = QLineEdit()
        cloudiness_edit.setFrame(False)

        
        layout1.addWidget(wind_label)
        layout1.addWidget(wind_edit)
        layout1.addWidget(temperature_label)
        layout1.addWidget(temperature_edit)
        layout1.addWidget(sensation_label)
        layout1.addWidget(sensation_edit)

        layout2.addWidget(precipitation_label)
        layout2.addWidget(precipitation_edit)
        layout2.addWidget(humudity_label)
        layout2.addWidget(humudity_edit)
        layout2.addWidget(cloudiness_label)
        layout2.addWidget(cloudiness_edit)

        layout3.addLayout(layout1)
        layout3.addLayout(layout2)
        

        layout.addLayout(layout3)

        
        image_label = QLabel(self)
        pixmap = QPixmap('recursos/mapa.jpg')

        
       
        resized_pixmap = pixmap.scaled(600, 900, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
        image_label.setPixmap(resized_pixmap)
        
        layout.addWidget(image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        


window = Window()
window.show()
sys.exit(app.exec())
