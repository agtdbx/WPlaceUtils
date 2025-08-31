import sys, math
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QColor, QFontMetrics, QClipboard
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QComboBox, QSlider, QFileDialog

from define import *
from color import Color


# Window class
class Window(QMainWindow):
    def __init__(self):
        super().__init__()

        self.image = None
        self.baseImage = None
        self.imagePath = None
        self.imageScale  = 10
        self.clipboard = QApplication.clipboard()
        self.windowW = WINDOW_W
        self.windowH = WINDOW_H
        self.textStatsSize = None
        self.initUI()
        self.updateDynamicUi(WINDOW_W, WINDOW_H)


    def initUI(self):
        self.setWindowTitle("WPlace image transfomator")
        self.setGeometry(100, 100, WINDOW_W, WINDOW_H)
        self.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.setStyleSheet("background-color: rgb(50, 50, 50)")

        # Load section
        self.labelLoadSection = QLabel(f"Loading", self)
        self.labelLoadSection.setGeometry(20, 0, 180, 75)
        self.labelLoadSection.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.buttonOpen = QPushButton("From file", self)
        self.buttonOpen.clicked.connect(self.loadImage)
        self.buttonOpen.setGeometry(20, 50, 150, 30)

        self.buttonOpen = QPushButton("From clipboard", self)
        self.buttonOpen.clicked.connect(self.loadImageFromClipboard)
        self.buttonOpen.setGeometry(20, 90, 150, 30)

        # Alpha section
        self.labelAlphaSection = QLabel(f"Alpha", self)
        self.labelAlphaSection.setGeometry(20, 150, 180, 20)
        self.labelAlphaSection.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.labelAlphaMode = QLabel(f"Transformation mode :", self)
        self.labelAlphaMode.setGeometry(20, 180, 180, 20)

        self.selectAlphaMode = QComboBox(self)
        self.selectAlphaMode.addItems(["Ignore channel", "Darken", "Lighten"])
        self.selectAlphaMode.setGeometry(20, 200, 150, 30)

        self.labelTransformAlpha = QLabel(f"Ignore alpha < {MAX_ALPHA_TRANSPARENT:3}", self)
        self.labelTransformAlpha.setGeometry(20, 240, 180, 20)

        self.sliderTransformAlpha = QSlider(Qt.Orientation.Horizontal, self)
        self.sliderTransformAlpha.setMinimum(0)
        self.sliderTransformAlpha.setMaximum(256)
        self.sliderTransformAlpha.setValue(MAX_ALPHA_TRANSPARENT)
        self.sliderTransformAlpha.setGeometry(20, 260, 150, 30)
        self.sliderTransformAlpha.valueChanged.connect(self.sliderAlpha)
        self.transformAlpha = MAX_ALPHA_TRANSPARENT

        self.buttonTransform = QPushButton("Transform alpha only", self)
        self.buttonTransform.clicked.connect(self.transformImageAlphaOnly)
        self.buttonTransform.setGeometry(20, 290, 150, 30)

        # Transformation section
        self.labelTransformationSection = QLabel(f"Transformation", self)
        self.labelTransformationSection.setGeometry(20, 350, 180, 20)
        self.labelTransformationSection.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.labelTransformMode = QLabel(f"Mode :", self)
        self.labelTransformMode.setGeometry(20, 380, 180, 20)

        self.selectTransformMode = QComboBox(self)
        self.selectTransformMode.addItems(["Vectorial", "Closest"])
        self.selectTransformMode.setGeometry(20, 400, 150, 30)

        self.buttonTransform = QPushButton("Transform image", self)
        self.buttonTransform.clicked.connect(self.transformImage)
        self.buttonTransform.setGeometry(20, 440, 150, 30)

        # Save section
        self.labelSaveSection = QLabel(f"Saving", self)
        self.labelSaveSection.setGeometry(20, 500, 180, 20)
        self.labelSaveSection.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.buttonSave = QPushButton("Save as file", self)
        self.buttonSave.clicked.connect(self.saveImage)
        self.buttonSave.setGeometry(20, 530, 150, 30)

        self.buttonCopy = QPushButton("Copy in clipboard", self)
        self.buttonCopy.clicked.connect(self.saveImageInClipboard)
        self.buttonCopy.setGeometry(20, 570, 150, 30)

        # Colors section
        self.labelColorsSection = QLabel(f"Colors", self)
        self.labelColorsSection.setStyleSheet("font-size: 20px; font-weight: bold;")

        self.buttonAllColor = QPushButton("Select all", self)
        self.buttonAllColor.clicked.connect(self.allColor)

        self.buttonResetColor = QPushButton("Reset selection", self)
        self.buttonResetColor.clicked.connect(self.resetColor)

        # Middle section
        self.text = QLabel("", self)

        self.imageDisplayed = QLabel(self)
        self.imageDisplayed.setGeometry(200, 50, WINDOW_W - 210, WINDOW_H - 60)
        self.imageDisplayed.setStyleSheet("border: 2px solid red;border-radius: 4px;")

        # Right section
        self.buttonFlagToggle = QPushButton("Flag Off", self)
        self.buttonFlagToggle.clicked.connect(self.flagToggle)
        self.isFlagToggle = False

        self.textStats = QLabel("", self)


        self.colors: list[Color] = []
        for i in range(64):
            self.colors.append(Color(i, self))


    def updateDynamicUi(self, width, height):
        self.windowW = width
        self.windowH = height
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

        # Left section
        self.labelColorsSection.setGeometry(20, height - allColorHeight - 110, 180, 20)
        self.buttonAllColor.setGeometry(20, height - allColorHeight - 80, 150, 30)
        self.buttonResetColor.setGeometry(20, height - allColorHeight - 40, 150, 30)

        # Middle section
        self.imageDisplayed.setGeometry(200, 50, width - 410, height - allColorHeight - 50)

        # Right section
        self.buttonFlagToggle.setGeometry(self.windowW - 150, 50, 70, 30)

        if self.textStatsSize != None:
            width, height = self.textStatsSize
            self.textStats.setGeometry(self.windowW - width - 10, 90, width, height)


    def setImage(self, image: QImage):
        self.image = image
        self.baseImage = self.image.copy()
        self.computeTextStat()
        w = self.image.width() * self.imageScale
        h = self.image.height() * self.imageScale
        tmpImg = self.image.scaled(w, h,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.FastTransformation)
        self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))


    def loadImage(self):
        self.setText()

        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Open Image")
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setViewMode(QFileDialog.ViewMode.Detail)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            self.imagePath = selected_files[0]

            image = QImage(self.imagePath)
            if image.isNull():
                self.setText("You must select an image", TXT_ERROR)
                return

            self.setImage(image)

        else:
            self.setText("You must select an image", TXT_ERROR)


    def loadImageFromClipboard(self):
        self.setText()

        image = self.clipboard.image(QClipboard.Mode.Clipboard)
        if image.isNull():
            image = None
            self.setText("You must have an image in your clipboard", TXT_ERROR)
            return

        self.setImage(image)


    def transformImageAlphaOnly(self):
        self.setText()

        if self.image == None:
            self.setText("You must load an image before transform it", TXT_ERROR)
            return

        nbPixel = 0
        self.image = self.baseImage.copy()
        for y in range(self.image.height()):
            for x in range(self.image.width()):
                color = self.image.pixelColor(x, y)

                r, g, b, a = color.getRgb()

                if a > self.transformAlpha:
                    darkenRatio = a / 255
                    r = int(r * darkenRatio)
                    g = int(g * darkenRatio)
                    b = int(b * darkenRatio)
                    a = 255
                else:
                    a = 0

                self.image.setPixelColor(x, y, QColor(r, g, b, a))

        self.computeTextStat(nbPixel)

        self.computeTextStat()
        w = self.image.width() * self.imageScale
        h = self.image.height() * self.imageScale
        tmpImg = self.image.scaled(w, h,
                                    Qt.AspectRatioMode.KeepAspectRatio,
                                    Qt.TransformationMode.FastTransformation)
        self.imageDisplayed.setPixmap(QPixmap.fromImage(tmpImg))


    def transformImage(self):
        self.setText()

        if self.image == None:
            self.setText("You must load an image before transform it", TXT_ERROR)
            return

        if self.selectTransformMode.currentText() == "Closest":
            closestMode = True
        else:
            closestMode = False

        nbPixel = 0
        self.image = self.baseImage.copy()
        for y in range(self.image.height()):
            for x in range(self.image.width()):
                color = self.image.pixelColor(x, y)

                r, g, b, a = color.getRgb()

                if a > self.transformAlpha:
                    darkenRatio = a / 255
                    r = int(r * darkenRatio)
                    g = int(g * darkenRatio)
                    b = int(b * darkenRatio)
                    a = 255
                else:
                    a = 0

                if a > 0:
                    nbPixel += 1
                    minDiff = 447697125
                    minColorId = -1

                    for i in range(64):
                        if not self.colors[i].selected:
                            continue
                        testColor = self.colors[i].color
                        dr = abs(r - testColor[0])
                        dg = abs(g - testColor[1])
                        db = abs(b - testColor[2])

                        if closestMode:
                            testDiff = dr + dg + db
                        else:
                            testDiff = dr**2 + dg**2 + db**2

                        if testDiff < minDiff:
                            minDiff = testDiff
                            minColorId = i

                    if minColorId != -1:
                        closestColor = self.colors[minColorId].color
                        r = closestColor[0]
                        g = closestColor[1]
                        b = closestColor[2]
                    else:
                        r, g, b, a = (0, 0, 0, 0)

                self.image.setPixelColor(x, y, QColor(r, g, b, a))

        self.computeTextStat(nbPixel)

        self.computeTextStat()
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


    def computeTextStat(self, nbPixel = None):
        if self.image == None:
            return

        # Count nb pixels to draw
        if nbPixel == None:
            nbPixel = 0
            for y in range(self.image.height()):
                for x in range(self.image.width()):
                    if self.image.pixelColor(x, y).alpha() > self.transformAlpha:
                        nbPixel += 1

        # Compute estimed time
        if self.isFlagToggle:
            estimedTime = nbPixel * 27
        else:
            estimedTime = nbPixel * 30
        idUnit = 0
        remains = []
        while idUnit < len(UNITS_SIZE):
            remains.append(estimedTime % UNITS_SIZE[idUnit])
            if estimedTime < UNITS_SIZE[idUnit]:
                break
            estimedTime //= UNITS_SIZE[idUnit]
            idUnit += 1

        idUnit = min(idUnit, len(UNITS_SIZE))

        # Compute estimed time string
        strEstimedTime = ""
        while idUnit >= 0:
            unitValue = remains[idUnit]
            if unitValue > 0:
                unitName = UNITS_NAMES[idUnit]
                if unitValue > 1:
                    unitName += "s"

                strEstimedTime += f"  {unitValue} {unitName}\n"

            idUnit -= 1

        # Create text for image stats
        text = f"     IMAGE STATS\n\n" \
                + f"size : {self.image.width()}x{self.image.height()}\n" \
                + f"nb pixels to draw : {nbPixel}\n" \
                + f"estimed time :\n{strEstimedTime}"

        metrics = QFontMetrics(self.textStats.font())
        size = metrics.size(0, text)
        width = size.width()
        height = size.height()

        self.textStatsSize = (width, height)

        self.textStats.setText(text)
        self.textStats.setGeometry(self.windowW - width - 10, 90, width, height)


    def sliderAlpha(self, value):
        self.labelTransformAlpha.setText(f"Ignore alpha < {value:3}")
        self.transformAlpha = value


    def flagToggle(self):
        self.isFlagToggle = not self.isFlagToggle
        if self.isFlagToggle:
            self.buttonFlagToggle.setText("Flag On")
        else:
            self.buttonFlagToggle.setText("Flag Off")

        self.computeTextStat()


    def allColor(self):
        for color in self.colors:
            color.setSelected(True)


    def resetColor(self):
        for color in self.colors:
            color.setSelected(color.basic)


    def keyPressEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            # Ctrl C
            if event.key() == Qt.Key.Key_C:
                if self.image == None:
                    return
                self.clipboard.setImage(self.image)
                self.setText("Image put in clipboard !", TXT_SUCCESS)

            # Ctrl V
            if event.key() == Qt.Key.Key_V:
                image = self.clipboard.image(QClipboard.Mode.Clipboard)
                if image.isNull():
                    return
                self.setImage(image)


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
