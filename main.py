import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QColor, QFontMetrics, QClipboard
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog


# Defines
WINDOW_W = 1600
WINDOW_H = 900
WINDOW_MIN_W = 800
WINDOW_MIN_H = 400
MIN_SCALE = 1
MAX_SCALE = 100

TXT_INFO = 0
TXT_SUCCESS = 1
TXT_ERROR = 2
TXT_COLORS = ["white", "green", "red"]

COLOR_PADDING = 3
COLOR_HEIGHT = 50

COLORS_BASIC = [
    True, True, True, False, True, True, True, False, True, False, False, True, True, True, True, False, False, False, False, False, False, True, True, True, True, True, True, False, True, False, True, True,
    False, False, True, True, False, False, False, True, True, True, True, True, True, False, False, False, True, True, False, False, False, False, False, True, False, False, False, False, False, False, False, True
]
COLORS_RBG = [
    (  0,  0,  0), ( 60, 60, 60), (120,120,120), (170,170,170), (210,210,210), (255,255,255), ( 96,  0, 24), (165, 14, 30),
    (237, 28, 36), (250,128,114), (228, 92, 26), (255,127, 39), (246,170,  9), (249,221, 59), (255,250, 88), (156,132, 49),
    (197,173, 49), (232,212, 95), ( 74,107, 58), ( 90,148, 74), (132,197,115), ( 14,185,104), ( 19,230,123), (135,255, 94),
    ( 12,129,110), ( 16,174,166), ( 19,225,190), ( 15,121,159), ( 96,247,242), (187,250,242), ( 40, 80,158), ( 64,147,228),
    (125,199,255), ( 77, 49,184), (107, 80,246), (153,177,251), ( 74, 66,132), (122,113,196), (181,174,241), (120, 12,153),
    (170, 56,185), (224,159,249), (203,  0,122), (236, 31,128), (243,141,169), (155, 82, 73), (209,128,120), (250,182,164),
    (104, 70, 52), (149,142, 42), (219,164, 99), (123, 99, 82), (156,132,107), (214,181,148), (209,128, 81), (248,178,119),
    (255,197,165), (109,100, 63), (148,140,107), (215,197,158), ( 51, 57, 65), (109,117,141), (179,185,209), (  0,  0,  0),
]

# Color class
class Color:
    def __init__(self, id, window:'Window'):
        self.id = id
        self.color = COLORS_RBG[id]
        self.basic = COLORS_BASIC[id]
        self.button = QPushButton(window)
        self.button.clicked.connect(self.clickOnButton)
        self.setSelected(self.basic)


    def setRect(self, x, y, w, h):
        self.button.setGeometry(x, y, w, h)


    def clickOnButton(self):
        self.setSelected(not self.selected)


    def setSelected(self, selected):
        self.selected = selected
        if self.id != 63:
            r, g, b = self.color
            styleBackground = f"background-color: rgb({r}, {g}, {b});"
        else:
            styleBackground = ""

        if self.selected:
            if self.basic:
                styleBorder = "border: 2px solid cyan;border-radius: 4px;"
            else:
                styleBorder = "border: 2px solid yellow;border-radius: 4px;"
        else:
            styleBorder = "border: 2px solid black;border-radius: 4px;"
        self.button.setStyleSheet(styleBackground + styleBorder)


# Window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = None
        self.imagePath = None
        self.imageScale  = 10
        self.clipboard = QApplication.clipboard()
        self.initUI()
        self.updateDynamicUi(WINDOW_W, WINDOW_H)


    def initUI(self):
        self.setWindowTitle("WPlace image transfomator")
        self.setGeometry(100, 100, WINDOW_W, WINDOW_H)
        self.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)

        self.text = QLabel("", self)

        self.buttonOpen = QPushButton("Load image", self)
        self.buttonOpen.clicked.connect(self.loadImage)
        self.buttonOpen.setGeometry(20, 20, 150, 30)

        self.buttonOpen = QPushButton("Load from clipboard", self)
        self.buttonOpen.clicked.connect(self.loadImageFromClipboard)
        self.buttonOpen.setGeometry(20, 70, 150, 30)

        self.buttonTransform = QPushButton("Modify image", self)
        self.buttonTransform.clicked.connect(self.modifyImage)
        self.buttonTransform.setGeometry(20, 120, 150, 30)

        self.buttonTransform = QPushButton("Save image", self)
        self.buttonTransform.clicked.connect(self.saveImage)
        self.buttonTransform.setGeometry(20, 170, 150, 30)

        self.buttonTransform = QPushButton("Copy in clipboard", self)
        self.buttonTransform.clicked.connect(self.saveImageInClipboard)
        self.buttonTransform.setGeometry(20, 220, 150, 30)

        self.imageDisplayed = QLabel(self)
        self.imageDisplayed.setGeometry(200, 50, WINDOW_W - 210, WINDOW_H - 60)
        self.imageDisplayed.setStyleSheet("border: 2px solid red;border-radius: 4px;")

        self.colors: list[Color] = []
        for i in range(64):
            self.colors.append(Color(i, self))


    def updateDynamicUi(self, width, height):
        bw = (width - 33 * COLOR_PADDING) // 32 + 1
        bh = COLOR_HEIGHT
        for i in range(64):
            if i < 32:
                bx = i * (bw + COLOR_PADDING) + COLOR_PADDING
                by = height - (COLOR_PADDING + COLOR_HEIGHT) * 2
                self.colors[i].setRect(bx, by, bw, bh)
            else:
                bx = (i - 32) * (bw + COLOR_PADDING) + COLOR_PADDING
                by = height - (COLOR_PADDING + COLOR_HEIGHT)
                self.colors[i].setRect(bx, by, bw, bh)

        allColorHeight = (COLOR_PADDING * 3) + (COLOR_HEIGHT * 2)
        self.imageDisplayed.setGeometry(200, 50, width - 210, height - allColorHeight - 50)



    def loadImage(self):
        self.setText()

        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open Image")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.imagePath = selected_files[0]

            self.image = QImage(self.imagePath)
            if self.image.isNull():
                self.image = None
                self.setText("You must select an image", TXT_ERROR)
                return

            w = self.image.width() * self.imageScale
            h = self.image.height() * self.imageScale
            tmpImg = self.image.scaled(w, h,
                                        Qt.AspectRatioMode.KeepAspectRatio,
                                        Qt.TransformationMode.FastTransformation)
            self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))

        else:
            self.setText("You must select an image", TXT_ERROR)


    def loadImageFromClipboard(self):
        self.setText()

        self.image = self.clipboard.image(QClipboard.Mode.Clipboard)
        if self.image.isNull():
            self.image = None
            self.setText("You must have an image in your clipboard", TXT_ERROR)
            return

        w = self.image.width() * self.imageScale
        h = self.image.height() * self.imageScale
        tmpImg = self.image.scaled(w, h,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.FastTransformation)
        self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))


    def modifyImage(self):
        self.setText()

        if self.image == None:
            self.setText("You must load an image before transform it", TXT_ERROR)
            return

        for y in range(self.image.height()):
            for x in range(self.image.width()):
                color = QColor(self.image.pixel(x, y))

                r, g, b, a =  color.getRgb()
                print(f"Color : {r:3} {g:3} {b:3} {a:3}  {color.alpha()}")

                color.setAlpha(10)

                self.image.setPixelColor(x, y, color)

        w = self.image.width() * self.imageScale
        h = self.image.height() * self.imageScale
        tmpImg = self.image.scaled(w, h,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.FastTransformation)
        self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))


    def saveImage(self):
        self.setText()

        if self.image == None:
            self.setText("You must load an image before save it", TXT_ERROR)
            return

        savePath = self.imagePath

        i = len(savePath) - 1
        while i >= 0:
            if savePath[i] == '.':
                break
            if savePath[i] == '/':
                i = -1
                break
            i -= 1

        if i != -1:
            savePath = savePath[0:i]
        savePath += "_wplace.png"
        self.image.save(savePath, "png")
        self.setText(f"Image save here : {savePath}", TXT_SUCCESS)


    def saveImageInClipboard(self):
        self.setText()

        if self.image == None:
            self.setText("You must load an image before put it in clipboard", TXT_ERROR)
            return

        self.clipboard.setImage(self.image)
        self.setText("Image put in clipboard !", TXT_SUCCESS)


    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.key() == Qt.Key.Key_C:
                if self.image == None:
                    return

                self.clipboard.setImage(self.image)
                self.setText("Image put in clipboard !", TXT_SUCCESS)

            if event.key() == Qt.Key.Key_V:
                self.image = self.clipboard.image(QClipboard.Mode.Clipboard)
                if self.image.isNull():
                    self.image = None
                    return

                w = self.image.width() * self.imageScale
                h = self.image.height() * self.imageScale
                tmpImg = self.image.scaled(w, h,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.FastTransformation)
                self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))


    def wheelEvent(self, event):
        if self.image != None:
            change = False

            if event.angleDelta().y() > 0:
                if self.imageScale < MAX_SCALE:
                    self.imageScale += 1
                    change = True
            else:
                if self.imageScale > MIN_SCALE:
                    self.imageScale -= 1
                    change = True

            if change:
                w = self.image.width() * self.imageScale
                h = self.image.height() * self.imageScale
                tmpImg = self.image.scaled(w, h,
                                            Qt.AspectRatioMode.KeepAspectRatio,
                                            Qt.TransformationMode.FastTransformation)
                self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))

        event.accept()


    def resizeEvent(self, event):
        new_size = event.size()  # QSize object
        self.updateDynamicUi(new_size.width(), new_size.height())
        super().resizeEvent(event)  # Call base class implementation


    def setText(self, text="", type=TXT_INFO):
        if text == "":
            self.text.setText("")
            return

        metrics = QFontMetrics(self.text.font())
        size = metrics.size(0, text)  # QSize object
        width = size.width()
        height = size.height()

        self.text.setText(text)
        self.text.setGeometry(WINDOW_W // 2 - width // 2, 10, width, height)

        self.text.setStyleSheet(f"color: {TXT_COLORS[type]};")



def main():
    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
