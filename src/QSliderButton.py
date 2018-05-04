'''
Created on May 1, 2018

@author: zhenfengzhao
'''
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QSlider
from PyQt5 import QtGui, QtCore
from PyQt5.QtGui import QPainter, QFont, QColor, QPen, QIntValidator

class QSliderButton(QSlider):

    def __init__(self, parent=None):
        super(QSliderButton, self).__init__(parent)
        
        self.setFont(QFont("Arial",12))
        
        self.stylesheet = """
        QSlider::groove:horizontal {
            background: red;
        }
        
        QSlider::handle:horizontal {
            background: white;
            border: 1px solid #5c5c5c;
            width: 50px;
            height: 40px;
            border-radius: 20px;
        }
        
        QSlider::add-page:horizontal {
            background: #BDBDBD;
        }
        
        QSlider::sub-page:horizontal {
            background: #62DEF0;
        }
        """
        self.setStyleSheet(self.stylesheet)

    def paintEvent(self, event):
        QSlider.paintEvent(self, event)

        painter = QtGui.QPainter(self)
        painter.setPen(QtGui.QPen(QtCore.Qt.white))

        font_metrics = QtGui.QFontMetrics(self.font())
        font_width = font_metrics.boundingRect(str('OFF')).width()
        font_height = font_metrics.boundingRect(str('OFF')).height()

        rect = self.geometry()
        if self.orientation() == QtCore.Qt.Horizontal:
            horizontal_x_pos  = rect.width() - font_width - 5
            horizontal_y_pos = (rect.height()+font_height) / 2 
            painter.drawText(QtCore.QPoint(5, horizontal_y_pos), str('ON'))
            painter.drawText(QtCore.QPoint(horizontal_x_pos, horizontal_y_pos), str('OFF'))
        else:
            pass

        #painter.drawRect(rect)