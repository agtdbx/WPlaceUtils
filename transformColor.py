import math
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QColor

from color import Color
from transformAlpha import transformAlphaColor


class ColorTransformWorker(QObject):
    # Signals to give data to main thread
    progress = pyqtSignal(int)
    finished = pyqtSignal(QImage, int)

    # Constructor for get all parameter for async transformation
    def __init__(self,
                 image: QImage,
                 ignoreAlpha: int,
                 alphaMode: str,
                 transformMode: str,
                 colors: list[Color]):
        super().__init__(None)

        self.image = image
        self.ignoreAlpha = ignoreAlpha
        self.alphaMode = alphaMode
        self.transformMode = transformMode
        self.colors = []
        for color in colors:
            self.colors.append(color.copy())
        self._abort = False


    # The async transformation
    def run(self):
        nbPixel = 0
        for y in range(self.image.height()):
            # Stop if needed
            if self._abort:
                break

            # Update progress
            self.progress.emit(int(y / self.image.height() * 100))

            for x in range(self.image.width()):
                # Stop if needed
                if self._abort:
                    break

                # Get color of current pixel
                color = self.image.pixelColor(x, y)

                # Alpha transformation
                r, g, b, a = transformAlphaColor(color.getRgb(), self.ignoreAlpha, self.alphaMode)

                # Ignore pixel if transparent
                if a == 0:
                    self.image.setPixelColor(x, y, QColor(r, g, b, a))
                    continue

                # Choose right color
                nbPixel += 1
                minDiff = math.inf
                minColorId = -1

                for i in range(64):
                    # Skip if color isn't selected
                    if not self.colors[i].selected:
                        continue

                    # Compute distance between test color and current pixel color
                    testColor = self.colors[i].color
                    rDiff = testColor[0] - r
                    gDiff = testColor[1] - g
                    bDiff = testColor[2] - b

                    if self.transformMode == "Vectorial":
                        testDiff = rDiff**2 + gDiff**2 + bDiff**2

                    elif self.transformMode == "Vectorial red shift":
                        rMean = (testColor[0] + r) / 2
                        rShift = int((512 + rMean) * rDiff * rDiff) >> 8
                        gShift = 4 * gDiff * gDiff
                        bShift = int((767 - rMean) * bDiff * bDiff) >> 8
                        testDiff = rShift**2 + gShift**2 + bShift**2

                    elif self.transformMode == "Vectorial green shift":
                        gMean = (testColor[1] + g) / 2
                        rShift = int((767 - gMean) * rDiff * rDiff) >> 8
                        gShift = int((512 + gMean) * gDiff * gDiff) >> 8
                        bShift = 4 * bDiff * bDiff
                        testDiff = rShift**2 + gShift**2 + bShift**2

                    elif self.transformMode == "Vectorial blue shift":
                        bMean = (testColor[2] + b) / 2
                        rShift = 4 * rDiff * rDiff
                        gShift = int((767 - bMean) * gDiff * gDiff) >> 8
                        bShift = int((512 + bMean) * bDiff * bDiff) >> 8
                        testDiff = rShift**2 + gShift**2 + bShift**2

                    else:
                        testDiff = abs(rDiff) + abs(gDiff) + abs(bDiff)

                    # Save closest color
                    if testDiff < minDiff:
                        minDiff = testDiff
                        minColorId = i

                # Update pixel in image
                if minColorId != -1:
                    closestColor = self.colors[minColorId].color
                    r = closestColor[0]
                    g = closestColor[1]
                    b = closestColor[2]
                else:
                    r, g, b, a = (0, 0, 0, 0)

                self.image.setPixelColor(x, y, QColor(r, g, b, a))

        # Send transformation result
        self.finished.emit(self.image, nbPixel)


    def abort(self):
        self._abort = True
