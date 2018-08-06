from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPainter

class rollLabel(QLabel):
    def __init__(self, parent=None):
        super(rollLabel, self).__init__(parent)

        self.speed = 3
        self.x = 0;
        self.max_x = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.roll)
        self.timer.start(10)

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        metrics = qp.fontMetrics()
        ascent = metrics.ascent()
        self.max_x = metrics.width(self.text())
        if self.max_x > self.width():  
            qp.drawText(self.x, ascent, self.text())
        else:
            qp.drawText(0, ascent, self.text())
        qp.end()
        
    def roll(self):
        if self.max_x + self.x < 0:
            self.x = self.max_x
        else:
            self.x = self.x - self.speed
        self.update()