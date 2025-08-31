from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QImage, QColor

# Functions
def lerpColor(s: tuple[int], e: tuple[int], t: float) -> tuple[int]:
        return (
            int(s[0] + (e[0] - s[0]) * t),
            int(s[1] + (e[1] - s[1]) * t),
            int(s[2] + (e[2] - s[2]) * t)
        )


def transformAlphaColor(color: tuple[int], ignoreAlpha: int, alphaMode: str) -> tuple[int]:
    r, g, b, a = color

    if a == 255:
        pass

    elif a > ignoreAlpha:
        if alphaMode == "Darken":
            ratio = 1.0 - (a / 255)
            r, g, b = lerpColor((r, g, b), (0, 0, 0), ratio)

        elif alphaMode == "Lighten":
            ratio = 1.0 - (a / 255)

            r, g, b = lerpColor((r, g, b), (255, 255, 255), ratio)
        a = 255

    else:
        a = 0

    return (r, g, b, a)


# Class
class AlphaTransformWorker(QObject):
    # Signals to give data to main thread
    progress = pyqtSignal(int)
    finished = pyqtSignal(QImage, int)

    # Constructor for get all parameter for async transformation
    def __init__(self,
                 image: QImage,
                 ignoreAlpha: int,
                 alphaMode: str):
        super().__init__(None)

        self.image = image
        self.ignoreAlpha = ignoreAlpha
        self.alphaMode = alphaMode
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

                # Transform it if it has some alpha
                r, g, b, a = transformAlphaColor(color.getRgb(), self.ignoreAlpha, self.alphaMode)

                # Count the number of pixel to draw
                if a != 0:
                    nbPixel += 1

                # Update pixel in image
                self.image.setPixelColor(x, y, QColor(r, g, b, a))

        # Send result of transformation
        self.finished.emit(self.image, nbPixel)


    def abort(self):
        self._abort = True
