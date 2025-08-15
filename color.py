from PyQt6.QtWidgets import QPushButton

from define import COLORS_RBG, COLORS_BASIC

class Color:
    def __init__(self, id, window):
        self.id = id
        self.color = COLORS_RBG[id]
        self.basic = COLORS_BASIC[id]
        self.button = QPushButton(window)
        self.button.clicked.connect(self.clickOnButton)
        self.textStatsSize = None
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
            styleBorder = "border: 2px solid gray;border-radius: 4px;"
        self.button.setStyleSheet(styleBackground + styleBorder)
