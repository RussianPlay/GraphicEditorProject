from GraphicEditor.config import *


#  Классы фигур и инструментов
class Rectangle:
    def __init__(self, sx, sy, ex, ey, color, bg_color, is_rounded_corners, is_filled):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.color = color
        self.bg_color = bg_color
        self.is_rounded_corners = is_rounded_corners
        self.is_filled = is_filled

    def draw(self, painter):
        if self.is_filled:
            painter.setBrush(QBrush(self.color))
            painter.setPen(self.color)
        else:
            painter.setBrush(QBrush(self.bg_color))
            painter.setPen(self.color)

        if self.is_rounded_corners:
            painter.drawRoundedRect(QtCore.QRectF(self.sx, self.sy,
                                                  self.ex - self.sx, self.ey - self.sy), 15, 15)
        else:
            painter.drawRect(self.sx, self.sy, self.ex - self.sx, self.ey - self.sy)


class Triangle:
    def __init__(self, sx, sy, ex, ey, color, bg_color, is_right_angle, is_filled):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.color = color
        self.bg_color = bg_color
        self.is_right_angle = is_right_angle
        self.is_filled = is_filled

    def draw(self, painter):
        if self.is_filled:
            painter.setBrush(QBrush(self.color))
            painter.setPen(self.color)
        else:
            painter.setBrush(QBrush(self.bg_color))
            painter.setPen(self.color)

        if self.is_right_angle:
            points = QPolygon([QPoint(self.sx, self.ey),
                               QPoint(self.sx, self.sy),
                               QPoint(self.ex, self.ey)])
        else:
            points = QPolygon([QPoint(self.sx, self.ey),
                               QPoint(self.sx + (self.ex - self.sx) // 2, self.sy),
                               QPoint(self.ex, self.ey)])

        painter.drawPolygon(points)


class Star:
    def __init__(self, sx, sy, ex, ey, n, color, initial):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.n = n
        self.color = color
        self.initial = initial

    def draw(self, painter):
        painter.setPen(self.color)
        side = self.ex - self.sx
        nodes = [(side * cos(i * 2 * pi / self.n),
                  side * sin(i * 2 * pi / self.n))
                 for i in range(self.n)]
        nodes2 = [(self.sx + int(node[0]), self.sy + int(node[1])) for node in nodes]
        if self.initial:
            for i in range(-1, len(nodes2) - 1):
                painter.drawLine(*nodes2[i], *nodes2[i + 1])
        else:
            for i in range(-2, len(nodes2) - 2):
                painter.drawLine(*nodes2[i], *nodes2[i + 2])


class BrushPoint:
    def __init__(self, x, y, color, cur_width):
        self.x = x
        self.y = y
        self.color = color
        self.cur_width = cur_width

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(self.color)
        painter.drawEllipse(self.x - self.cur_width, self.y - self.cur_width, 5 + self.cur_width, 5 + self.cur_width)


class Pencil(BrushPoint):
    def __init__(self, x, y, cur_width):
        super().__init__(x, y, QColor("#000000"), cur_width)


class Rubber(BrushPoint):
    def __init__(self, x, y, color, cur_width):
        super().__init__(x, y, color, cur_width)


class FillColorBucket:
    def __init__(self, color):
        self.color = color

    def draw(self, painter):
        windp.set_style(self.color)


class Palette:
    def __init__(self, x, y, ind):
        self.x = x
        self.y = y
        self.ind = ind

    def draw(self, painter):
        screen = windp.save_w()
        if screen is not None:
            screenpixmap = screen.grabWindow(windp.winId())
            wind.changing_colors[self.ind] = QColor(screenpixmap.toImage().pixel(self.x, self.y)).name()
            wind.set_color_changing_color_buttons()


class Line:
    def __init__(self, sx, sy, ex, ey, color):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
        self.color = color

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(self.color)
        painter.drawLine(self.sx, self.sy, self.ex, self.ey)


class Circle:
    def __init__(self, cx, cy, x, y, color):
        self.cx = cx
        self.cy = cy
        self.x = x
        self.y = y
        self.color = color

    def draw(self, painter):
        painter.setBrush(QBrush(self.color))
        painter.setPen(self.color)
        radius = int(((self.cx - self.x) ** 2 + (self.cy - self.y) ** 2) ** 0.5)
        painter.drawEllipse(self.cx - radius, self.cy - radius, radius * 2, radius * 2)


#  Класс для области рисования
class Canvas(QWidget):
    def __init__(self):
        super().__init__()
        self.objects = []
        self.instrument = "brush"
        self.ind_changing_color_btn = 0
        self.cur_width = 5
        self.color = None
        self.bg_color = QColor("#FFFFFF")
        self.pal = None
        self.background_pixmap = None
        self.rubber_color = QColor("#FFFFFF")
        self.set_style()
        self.painter = QPainter()

    def set_style(self, color=QColor("#FFFFFF")):
        # Инициализация фона "Canvas". Используется лишь при запуске
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"background-color: {color.name()};")

    def save_w(self):
        # Возвращение картинки с рисуемой области. Используется исключительно для "Палитры"
        return QApplication.primaryScreen()

    #  Рисование Qpixmap и фигур
    def paintEvent(self, event):
        self.painter.begin(self)
        if not self.background_pixmap is None:
            windp.painter.drawPixmap(0, 0, self.background_pixmap)
        for obj in self.objects:
            obj.draw(self.painter)
        self.update()
        self.painter.end()

    #  Добавление объектов соответствующего инструмента при клике
    def mousePressEvent(self, event):
        if self.instrument == "palette":
            self.pal = Palette(event.x(), event.y(), self.ind_changing_color_btn)
            self.pal.draw(self.painter)
            self.update()
            self.checking_adding_index()
        elif self.color is not None:
            if self.instrument == "brush":
                self.objects.append(BrushPoint(event.x(), event.y(), self.color, self.cur_width))
                self.update()
            elif self.instrument == "line":
                self.objects.append(Line(event.x(), event.y(), event.x(), event.y(), self.color))
                self.update()
            elif self.instrument == "circle":
                self.objects.append(Circle(event.x(), event.y(), event.x(), event.y(), self.color))
                self.update()
            elif self.instrument == "rectangle":
                self.objects.append(Rectangle(event.x(), event.y(), event.x(), event.y(),
                                              self.color, self.bg_color, False, False))
                self.update()
            elif self.instrument == "rounded_rectangle":
                self.objects.append(Rectangle(event.x(), event.y(), event.x(), event.y(),
                                              self.color, self.bg_color, True, False))
                self.update()
            elif self.instrument == "filled_rectangle":
                self.objects.append(Rectangle(event.x(), event.y(), event.x(), event.y(),
                                              self.color, self.bg_color, False, True))
                self.update()
            elif self.instrument == "filled_rounded_rectangle":
                self.objects.append(Rectangle(event.x(), event.y(), event.x(), event.y(),
                                              self.color, self.bg_color, True, True))
                self.update()
            elif self.instrument == "triangle":
                self.objects.append(Triangle(event.x(), event.y(), event.x(), event.y(),
                                             self.color, self.bg_color, False, False))
                self.update()
            elif self.instrument == "right_triangle":
                self.objects.append(Triangle(event.x(), event.y(), event.x(), event.y(),
                                             self.color, self.bg_color, True, False))
                self.update()
            elif self.instrument == "five-p_star":
                self.objects.append(Star(event.x(), event.y(), event.x(), event.y(), 5, self.color, False))
                self.update()
            elif self.instrument == "six-p_star":
                self.objects.append(Star(event.x(), event.y(), event.x(), event.y(), 6, self.color, False))
                self.update()
            elif self.instrument == "filled_triangle":
                self.objects.append(Triangle(event.x(), event.y(), event.x(), event.y(),
                                             self.color, self.bg_color, False, True))
                self.update()
            elif self.instrument == "filled_right_triangle":
                self.objects.append(Triangle(event.x(), event.y(), event.x(), event.y(),
                                             self.color, self.bg_color, True, True))
                self.update()
            elif self.instrument == "initial_five-p_star":
                self.objects.append(Star(event.x(), event.y(), event.x(), event.y(), 5, self.color, True))
                self.update()
            elif self.instrument == "initial_six-p_star":
                self.objects.append(Star(event.x(), event.y(), event.x(), event.y(), 6, self.color, True))
                self.update()
            elif self.instrument == "pencil":
                self.objects.append(Pencil(event.x(), event.y(), self.cur_width))
                self.update()
            elif self.instrument == "rubber":
                self.objects.append(Rubber(event.x(), event.y(), self.rubber_color, self.cur_width))
                self.update()
            elif self.instrument == "fill_color_bucket":
                self.objects.clear()
                self.objects.append(FillColorBucket(self.color))
                self.rubber_color = self.color
                self.background_pixmap = None
                self.bg_color = self.color
                self.update()

    #  Добавление объектов соответствующего инструмента при движении
    def mouseMoveEvent(self, event):
        if self.instrument == "pencil":
            self.objects.append(Pencil(event.x(), event.y(), self.cur_width))
            self.update()
        elif self.instrument == "rubber":
            self.objects.append(Rubber(event.x(), event.y(), self.rubber_color, self.cur_width))
            self.update()
        elif self.color is not None:
            if self.instrument == "brush":
                self.objects.append(BrushPoint(event.x(), event.y(), self.color, self.cur_width))
                self.update()
            elif self.instrument == "circle":
                self.objects[-1].x = event.x()
                self.objects[-1].y = event.y()
                self.update()
            elif self.instrument == "fill_color_bucket":
                self.objects.clear()
                self.objects.append(FillColorBucket(self.color))
                self.rubber_color = self.color
                self.background_pixmap = None
                self.bg_color = self.color
                self.update()
            elif self.instrument != "palette":
                self.objects[-1].ex = event.x()
                self.objects[-1].ey = event.y()
                self.update()

    def checking_adding_index(self):
        # Выбор индекса кнопки, которая будет изменять цвет при использовании "Палитры"
        if self.ind_changing_color_btn == len(wind.changingcolbuttongroup.buttons()) - 1:
            self.ind_changing_color_btn = 0
        else:
            self.ind_changing_color_btn += 1

    #  Установка инструмета и соответсующей картинки для курсора
    def setBrush(self):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        self.instrument = "brush"

    def setLine(self):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        self.instrument = "line"

    def setCircle(self):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        self.instrument = "circle"

    def setRectange(self, is_filled=False):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        if is_filled:
            self.instrument = "filled_rectangle"
        else:
            self.instrument = "rectangle"

    def setRoundedRectangle(self, is_filled=False):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        if is_filled:
            self.instrument = "filled_rounded_rectangle"
        else:
            self.instrument = "rounded_rectangle"

    def setTriangle(self, is_filled=False):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        if is_filled:
            self.instrument = "filled_triangle"
        else:
            self.instrument = "triangle"

    def setRightTriangle(self, is_filled=False):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        if is_filled:
            self.instrument = "filled_right_triangle"
        else:
            self.instrument = "right_triangle"

    def setFivePStar(self, is_initial=False):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        if is_initial:
            self.instrument = "initial_five-p_star"
        else:
            self.instrument = "five-p_star"

    def setSixPStar(self, is_initial=False):
        QApplication.setOverrideCursor(QCursor(QtCore.Qt.ArrowCursor))
        if is_initial:
            self.instrument = "initial_six-p_star"
        else:
            self.instrument = "six-p_star"

    def setPencil(self):
        pixmap = QPixmap("images/pencil.png").scaled(20, 20)
        cursor = QCursor(pixmap)
        QApplication.setOverrideCursor(cursor)
        self.instrument = "pencil"

    def setFillColorBucket(self):
        pixmap = QPixmap("images/fill_color_bucket.png").scaled(25, 25)
        cursor = QCursor(pixmap)
        QApplication.setOverrideCursor(cursor)
        self.instrument = "fill_color_bucket"

    def setPal(self):
        pixmap = QPixmap("images/palette.png").scaled(20, 20)
        cursor = QCursor(pixmap)
        QApplication.setOverrideCursor(cursor)
        self.instrument = "palette"

    def setRubber(self):
        pixmap = QPixmap("images/rubber.png").scaled(20, 20)
        cursor = QCursor(pixmap)
        QApplication.setOverrideCursor(cursor)
        self.instrument = "rubber"

    def changing_color_of_tools(self):
        # Для кнопок с изменяющимся цветом. Изменяется с помощью кнопки "Палитры"
        self.color = self.sender().palette().color(QPalette.Window)

    def set_color(self):
        # Выбор цвета
        color = QColorDialog.getColor()
        if color.isValid():
            wind.changing_colors[self.ind_changing_color_btn] = color.name()
            wind.set_color_changing_color_buttons()
            self.checking_adding_index()

    def set_width(self):
        # Выбор толщины. Для кнопки с выбором толщины кисточки
        if self.sender().currentText() == "low":
            self.cur_width = 5
        elif self.sender().currentText() == "medium":
            self.cur_width = 10
        elif self.sender().currentText() == "hard":
            self.cur_width = 20


#  Главное окно, которая запускается первым
class Window(QMainWindow, Ui_MainWindow):
    def __init__(self, wp):
        super().__init__()
        self.setupUi(self)
        self.colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (190, 190, 190), (255, 255, 0), (255, 181, 197),
                  (255, 0, 255), (255, 165, 0), (0, 255, 255), (211, 211, 211), (46, 139, 87), (160, 32, 240)]
        self.centralWidget().setStyleSheet(f"background-color: #AFDAFC;")
        self.changing_colors = ["#FFFFFF" for _ in range(len(self.changingcolbuttongroup.buttons()))]
        self.set_button_colors()
        self.set_color_changing_color_buttons()
        [i.clicked.connect(wp.changing_color_of_tools)
         for i in self.colorbuttongroup.buttons()]
        [i.clicked.connect(wp.changing_color_of_tools)
         for i in self.changingcolbuttongroup.buttons()]

        self.paintgridLayout.addWidget(wp)
        self.setcolorbutton.clicked.connect(wp.set_color)
        self.pushButtonWhite.clicked.connect(wp.changing_color_of_tools)
        self.pushButtonBlack.clicked.connect(wp.changing_color_of_tools)
        self.action_brush.triggered.connect(wp.setBrush)
        self.action_line.triggered.connect(wp.setLine)
        self.action_circle.triggered.connect(wp.setCircle)
        self.action_helptext.triggered.connect(self.set_help_text)
        self.action_modulestext.triggered.connect(self.set_modules_text)
        self.action_open.triggered.connect(self.open_image)
        self.action_save.triggered.connect(self.save_painter_image)
        self.action_exit.triggered.connect(self.code_exit)
        self.pencilbutton.clicked.connect(wp.setPencil)
        self.fillcolorbucketbutton.clicked.connect(wp.setFillColorBucket)
        self.palletebutton.clicked.connect(wp.setPal)
        self.rubberbutton.clicked.connect(wp.setRubber)

        self.rectanglebutton.clicked.connect(wp.setRectange)
        self.roundedrectanglebutton.clicked.connect(wp.setRoundedRectangle)
        self.trianglebutton.clicked.connect(wp.setTriangle)
        self.righttrianglebutton.clicked.connect(wp.setRightTriangle)
        self.fivepstarbutton.clicked.connect(wp.setFivePStar)
        self.sixpstarbutton.clicked.connect(wp.setSixPStar)

        self.filrectanglebutton.clicked.connect(lambda: wp.setRectange(True))
        self.filroundedrectanglebutton.clicked.connect(lambda: wp.setRoundedRectangle(True))
        self.filtrianglebutton.clicked.connect(lambda: wp.setTriangle(True))
        self.filrighttrianglebutton.clicked.connect(lambda: wp.setRightTriangle(True))
        self.initialfivepstarbutton.clicked.connect(lambda: wp.setFivePStar(True))
        self.initialsixpstarbutton.clicked.connect(lambda: wp.setSixPStar(True))

        self.comboBoxWidth.addItem(QIcon('images/low_width.png'), "low")
        self.comboBoxWidth.addItem(QIcon('images/medium_width.png'), "medium")
        self.comboBoxWidth.addItem(QIcon('images/hard_width.png'), "hard")
        self.comboBoxWidth.currentIndexChanged.connect(wp.set_width)

    def set_button_colors(self):
        #  Задаются иконки кнопкам с выбором фигур, инструментов, кнопка с диалогом, задающая индивидуальный цвет
        for i in range(len(self.colorbuttongroup.buttons())):
            self.colorbuttongroup.buttons()[i].setStyleSheet(f'background: rgb{self.colors[i]};')

        self.pushButtonBlack.setStyleSheet(f'background: rgb(0, 0, 0);')
        self.pushButtonWhite.setStyleSheet(f'background: rgb(255, 255, 255);')
        self.setcolorbutton.setStyleSheet(f'background: rgb(255, 255, 255);')
        self.setcolorbutton.setIcon(QIcon('images/rainbow.png'))

        self.palletebutton.setIcon(QIcon('images/palette.png'))
        self.fillcolorbucketbutton.setIcon(QIcon('images/fill_color_bucket.png'))
        self.pencilbutton.setIcon(QIcon('images/pencil.png'))
        self.rubberbutton.setIcon(QIcon('images/rubber.png'))

        self.rectanglebutton.setIcon(QIcon('images/rectangle.png'))
        self.roundedrectanglebutton.setIcon(QIcon('images/rounded_rectangle.png'))
        self.trianglebutton.setIcon(QIcon('images/triangle.png'))
        self.righttrianglebutton.setIcon(QIcon('images/right_triangle.png'))
        self.fivepstarbutton.setIcon(QIcon('images/five-p_star.png'))
        self.sixpstarbutton.setIcon(QIcon('images/six-p_star.png'))

        self.filrectanglebutton.setIcon(QIcon('images/fil_rectangle.png'))
        self.filroundedrectanglebutton.setIcon(QIcon('images/fil_rounded_rectangle.png'))
        self.filtrianglebutton.setIcon(QIcon('images/fil_triangle.png'))
        self.filrighttrianglebutton.setIcon(QIcon('images/fil_right_triangle.png'))
        self.initialfivepstarbutton.setIcon(QIcon('images/initial_five-p_star.png'))
        self.initialsixpstarbutton.setIcon(QIcon('images/initial_six-p_star.png'))

    def set_color_changing_color_buttons(self):
        #  Задается фон кнопкам с выбором цветов
        ch_color_buttons = self.changingcolbuttongroup.buttons()
        for i in range(len(ch_color_buttons)):
            ch_color_buttons[i].setStyleSheet(f'background: {self.changing_colors[i]};')

    #  Запуск побочных окон
    def set_help_text(self):
        self.hw = HelpWindow()
        self.hw.set_helping_text()
        self.hw.show()

    def set_modules_text(self):
        self.hw = HelpWindow()
        self.hw.set_modules_text()
        self.hw.show()

    #  Функция сохранения Qpixmap в папке your_drawn_pictures
    def save_painter_image(self):
        text, ok = QInputDialog.getText(self, "Сохранение", "Название файла")
        if ok:
            screen = windp.save_w()
            if screen is not None:
                screenpixmap = screen.grabWindow(windp.winId())
                screenpixmap.toImage().save(f"your_drawn_pictures/{text}.png")

    #  Функция выбора и рисования на Qpainter Qpixmap
    def open_image(self):
        file_path = QFileDialog.getOpenFileName(self, "Выбрать картинку", "", "Картинка (*.jpg);;Картинка (*.png)")[0]
        if file_path:
            windp.background_pixmap = QPixmap(file_path)
            windp.objects = []
        windp.update()

    #  Функция закрытия программы
    def code_exit(self):
        sys.exit()


#  Побочное окно. Запускается после нажатия на кнопки "Помощь->О программе" и "Помощь->Используемые модули"
class HelpWindow(QWidget, Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

    def set_helping_text(self):
        with open("README.txt", "r", encoding="utf-8") as f:
            [self.textedit.appendPlainText(line) for line in f.readlines()]

    def set_modules_text(self):
        with open("config.py", "r", encoding="utf-8") as f:
            [self.textedit.appendPlainText(line) for line in f.readlines()]


if __name__ == "__main__":
    app = QApplication(sys.argv)
    windp = Canvas()
    wind = Window(windp)
    windp.show()
    wind.show()
    sys.exit(app.exec())