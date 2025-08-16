from PyQt6.QtWidgets import QPushButton

from define import COLORS_RBG, COLORS_BASIC, COLORS_NAMES

def rgbToStyleColor(text, color):
    return f"{text} rgb({color[0]}, {color[1]}, {color[2]});"

def invertRgb(color):
    return (255 - color[0], 255 - color[1], 255 - color[2])


class Color:
    def __init__(self, id, window):
        self.id = id
        self.color = COLORS_RBG[id]
        self.basic = COLORS_BASIC[id]
        self.button = QPushButton(window)
        self.button.clicked.connect(self.clickOnButton)
        self.button.setToolTip(COLORS_NAMES[id])
        self.textStatsSize = None
        self.setSelected(self.basic)


    def setRect(self, x, y, w, h):
        self.button.setGeometry(x, y, w, h)


    def clickOnButton(self):
        self.setSelected(not self.selected)


    def setSelected(self, selected):
        self.selected = selected
        if self.id != 63:
            styleBackground = rgbToStyleColor("background-color :", self.color)
        else:
            styleBackground = ""

        if self.selected:
            if self.basic:
                styleBorder = "border: 2px solid cyan;"
            else:
                styleBorder = "border: 2px solid yellow;"
        else:
            styleBorder = "border: 2px solid gray;"
        styleBorder += "border-radius: 8px;"
        styleQtoolType = rgbToStyleColor("color :", invertRgb(self.color))
        self.button.setStyleSheet(styleBackground + styleBorder + styleQtoolType)
