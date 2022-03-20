from GraphicEditor.window import Ui_MainWindow
from GraphicEditor.helpwindow import Ui_Form
from GraphicEditor.saving_window import Ui_SaveForm
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFrame, QColorDialog, \
    QInputDialog, QFileDialog, QGraphicsView
from PyQt5.QtGui import QColor, QPixmap, QPainter, QBrush, QPalette, QIcon, QPolygon, QCursor
from PyQt5.QtCore import QPoint, Qt, QSize
from PyQt5 import QtCore
from math import sin, cos, pi
