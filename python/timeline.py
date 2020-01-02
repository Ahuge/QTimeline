# -*- coding: utf-8 -*-
import sys
from Qt import QtGui, QtCore, QtWidgets

styleSheet = """
QSlider,QSlider:disabled,QSlider:focus     {
                          background: qcolor(0,0,0,0);   }
QSlider:item:hover    {   background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #eaa553);
                          color: #000000;              }
QWidget:item:selected {   background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);      }
 QSlider::groove:horizontal {

    border: 1px solid #999999;
    background: qcolor(0,0,0,0);
 }
QSlider::handle:horizontal {
    background:  qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,160,47, 141), stop:0.497175 rgba(255,160,47, 200), stop:0.497326 rgba(255,160,47, 200), stop:1 rgba(255,160,47, 147));
    width: 3px;
 }
"""


class TimelineWidget(QtWidgets.QSlider):
    STEPPING_CHUNKS = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 2500, 5000]

    def __init__(self, parent, *args):
        super(TimelineWidget, self).__init__(parent=parent, *args)
        self.parent = parent
        self.keyFrames = []
        self.erroredFrames = []
        self.hover = False
        self.hoverPos = None
        self.PressPos = None
        self.MovePos = None
        self.setRange(0, 30)
        self.origMax = self.maximum()
        self.oriMin = self.minimum()
        self.setOrientation(QtCore.Qt.Horizontal)
        self.setStyleSheet(styleSheet)
        self.setMouseTracking(True)
        self.setPageStep(1)
        self.setMinimumSize(1, 40)
        self.installEventFilter(self)
        self._large_step = 1

    def setRange(self, start, end, setOrig=True):
        if setOrig:
            self.origMax = start
            self.oriMin = end
        return super(TimelineWidget, self).setRange(start, end)

    def addKeyFrame(self, frame):
        self.keyFrames.append(frame)
        self.keyFrames.sort()

    def setKeyframes(self, cached):
        self.keyFrames = sorted(cached)

    def setErrors(self, missing):
        self.erroredFrames = missing

    def paintEvent(self, event):
        qpainter = QtGui.QPainter()
        qpainter.begin(self)
        self.drawWidget(qpainter)
        qpainter.end()
        super(TimelineWidget, self).paintEvent(event)

    def drawWidget(self, qpainter):
        font = QtGui.QFont("Serif", 7, QtGui.QFont.Light)
        qpainter.setFont(font)

        width = self.width()
        height = self.height()
        frame_count = self.maximum() - self.minimum()
        float_step = float(width) / frame_count
        step = max(1, int(round(float_step)))

        pen = QtGui.QPen(QtGui.QColor(200, 200, 200), 1, QtCore.Qt.SolidLine)

        qpainter.setPen(pen)
        qpainter.setBrush(QtCore.Qt.NoBrush)
        # qpainter.drawRect(0, 0, w-50, h-50)

        pxNb = int(round((frame_count + 1) * step))
        numbers = range(self.minimum(), self.maximum() + 1, 1)
        metrics = qpainter.fontMetrics()
        font_height = metrics.height()

        _character_width = metrics.width(str(self.maximum())) + 8
        _parts = self.width() / _character_width

        number_step = max([5, frame_count / (_parts or 1)])
        for lower, higher in zip(self.STEPPING_CHUNKS[::], self.STEPPING_CHUNKS[1::]):
            if higher > number_step > lower:
                number_step = higher
                break
        self.large_step = number_step

        _line_count = self.width() / 3
        frame_line_step = max([1, frame_count / (_line_count or 1)])

        for index, _ in enumerate(range(0, pxNb, step)):
            current_value = numbers[index]
            position = self.style().sliderPositionFromValue(
                self.minimum(), self.maximum(), current_value, self.width()
            )
            half_height = height / 2
            spacing = 1.5
            if current_value in self.keyFrames:
                # Green Keyframes
                qpainter.setPen(QtGui.QColor(0, 255, 0))
                qpainter.setBrush(QtGui.QColor(0, 255, 0))
                qpainter.drawRect(
                    position - (float_step / 2), half_height + 5, float_step, 1.5
                )
                qpainter.setPen(pen)
                qpainter.setBrush(QtCore.Qt.NoBrush)
            elif current_value in self.erroredFrames:
                # Red error frames
                qpainter.setPen(QtGui.QColor(255, 0, 0))
                qpainter.setBrush(QtGui.QColor(255, 0, 0))
                qpainter.drawRect(
                    position - (float_step / 2), half_height + 5, float_step, 1.5
                )
                qpainter.setPen(pen)
                qpainter.setBrush(QtCore.Qt.NoBrush)

            if (current_value % number_step) == 0:
                # Big frame steps
                spacing = 4
                text = current_value
                font_width = metrics.width(str(text))
                qpainter.drawText(
                    position - font_width / 2, height - font_height / 3, str(text)
                )

            # Draw individual frame lines
            if (current_value % frame_line_step) == 0:
                qpainter.drawLine(
                    position, half_height + spacing, position, half_height - spacing
                )

        # Draw the current frame
        current_frame_position = self.style().sliderPositionFromValue(
            self.minimum(), self.maximum(), self.value(), self.width()
        )
        font_width = metrics.width(str(self.value()))
        qpainter.setPen(QtGui.QColor(255, 160, 47))
        qpainter.drawText(
            current_frame_position + font_width / 2, 0 + font_height, str(self.value())
        )
        if self.hover:
            hover_position = self.style().sliderValueFromPosition(
                self.minimum(), self.maximum(), self.hoverPos.x(), self.width()
            )
            if hover_position != self.value():
                hover_line_pos = self.style().sliderPositionFromValue(
                    self.minimum(), self.maximum(), hover_position, self.width()
                )
                font_width = metrics.width(str(hover_position))
                pen2 = QtGui.QPen(
                    QtGui.QColor(255, 160, 47, 100), 2, QtCore.Qt.SolidLine
                )
                qpainter.setPen(pen2)
                qpainter.drawLine(hover_line_pos, 0, hover_line_pos, height)
                qpainter.drawText(
                    hover_line_pos + font_width / 2,
                    0 + font_height,
                    str(hover_position),
                )
        qpainter.setPen(pen)

    def mousePressEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            self.PressPos = event.globalPos()
            self.MovePos = event.globalPos()
        if event.button() == QtCore.Qt.LeftButton:
            butts = QtCore.Qt.MouseButtons(QtCore.Qt.MidButton)
            nevent = QtGui.QMouseEvent(
                event.type(),
                event.pos(),
                event.globalPos(),
                QtCore.Qt.MidButton,
                butts,
                event.modifiers(),
            )
            super(TimelineWidget, self).mousePressEvent(nevent)
        else:
            super(TimelineWidget, self).mousePressEvent(event)

    def wheelEvent(self, event):
        total_delta = round(120 / event.delta()) * 2
        hover_position = self.style().sliderValueFromPosition(
            self.minimum(), self.maximum(), self.hoverPos.x(), self.width()
        )

        percent = (float(hover_position) - self.minimum()) / (self.maximum() - self.minimum())

        newMin = self.minimum() + (percent * total_delta)
        newMax = self.maximum() - ((1 - percent) * total_delta)

        self.setMinimum(round(newMin))
        self.setMaximum(round(newMax))
        self.repaint()

    def eventFilter(self, widget, event):
        if event.type() == QtCore.QEvent.MouseMove:
            self.hover = True
            self.hoverPos = event.pos()
            self.repaint()
        elif event.type() == QtCore.QEvent.Leave:
            self.hover = False
            self.repaint()
        return super(TimelineWidget, self).eventFilter(widget, event)

    def keyPressEvent(self, event):
        if (
            event.key() == QtCore.Qt.Key_Left
            and event.modifiers() == QtCore.Qt.AltModifier
        ):
            self.goPreviousKeyFrame()
            return event.accept()
        elif (
            event.key() == QtCore.Qt.Key_Right
            and event.modifiers() == QtCore.Qt.AltModifier
        ):
            self.goNextKeyFrame()
            return event.accept()
        elif (
            event.key() == QtCore.Qt.Key_Left
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self.goPreviousStepFrame()
            return event.accept()
        elif (
            event.key() == QtCore.Qt.Key_Right
            and event.modifiers() == QtCore.Qt.ControlModifier
        ):
            self.goNextStepFrame()
            return event.accept()
        return super(TimelineWidget, self).keyPressEvent(event)

    def mouseMoveEvent(self, event):
        if event.modifiers() == QtCore.Qt.AltModifier:
            if event.buttons() in [QtCore.Qt.MidButton, QtCore.Qt.LeftButton]:
                globalPos = event.globalPos()
                diff = globalPos - self.MovePos
                a = self.width() / (self.maximum() - self.minimum())
                if abs(diff.x()) > a:
                    self.MovePos = globalPos
                    newMin = self.minimum() - (1 * (diff.x() / abs(diff.x())))
                    newMax = self.maximum() - (1 * (diff.x() / abs(diff.x())))
                    self.setRange(newMin, newMax)
                    self.repaint()
        else:
            return super(TimelineWidget, self).mouseMoveEvent(event)

    @QtCore.Slot()
    def nextFrame(self):
        if self.value() >= self.maximum():
            self.setValue(self.minimum())
        else:
            self.setValue(self.value() + 1)

    @QtCore.Slot()
    def previousFrame(self):
        if self.value() <= self.minimum():
            self.setValue(self.maximum())
        else:
            self.setValue(self.value() - 1)

    @QtCore.Slot()
    def goStart(self):
        self.setValue(self.minimum())

    @QtCore.Slot()
    def goPreviousKeyFrame(self):
        frame = self.value()
        if frame <= self.keyFrames[0]:
            return
        _keys = self.keyFrames[:]
        _keys.append(frame)
        _keys.sort()
        self.setValue(_keys[_keys.index(frame)-1])

    @QtCore.Slot()
    def goNextKeyFrame(self):
        frame = self.value()
        if frame >= self.keyFrames[-1]:
            return
        _keys = self.keyFrames[:]
        _keys.append(frame)
        _keys.sort()
        _new_value = _keys[_keys.index(frame)+1]
        print("New_value: %s" % _new_value)
        self.setValue(_new_value)

    @QtCore.Slot()
    def goPreviousStepFrame(self):
        offset = self.value() % self.large_step
        if not offset:
            offset = self.large_step
        self.setValue(self.value() - offset + 1)

    @QtCore.Slot()
    def goNextStepFrame(self):
        self.setValue(
            self.value() + (self.large_step - self.value() % self.large_step) - 1
        )

    @QtCore.Slot()
    def goEnd(self):
        self.setValue(self.maximum())
