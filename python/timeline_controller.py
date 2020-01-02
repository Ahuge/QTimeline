from Qt import QtWidgets, QtCore

from .timeline import TimelineWidget

class TimelineButtons(QtWidgets.QWidget):
    GoToStart = QtCore.Signal()
    GoToPreviousKeyFrame = QtCore.Signal()
    PlayBackwards = QtCore.Signal()
    GoToFrame = QtCore.Signal(int)
    PlayForwards = QtCore.Signal()
    GoToNextKeyFrame = QtCore.Signal()
    GoToEnd = QtCore.Signal()
    Stop = QtCore.Signal()

    def __init__(self, parent=None):
        super(TimelineButtons, self).__init__(parent)

        self.startButton = None
        self.previousKeyButton = None
        self.playBackwardsButton = None
        self.frameInput = None
        self.playForwardsButton = None
        self.nextKeyButton = None
        self.endButton = None

        self._previous_text = ""
        self.buildUI()

    def buildUI(self):
        self.setLayout(QtWidgets.QHBoxLayout())

        self.startButton = QtWidgets.QPushButton("Go To Start")
        self.previousKeyButton = QtWidgets.QPushButton("Previous Key")
        self.playBackwardsButton = QtWidgets.QPushButton("Reverse")
        self.frameInput = QtWidgets.QLineEdit("")
        rxv = QtGui.QRegExpValidator(QtCore.QRegExp("\\d*"), self)
        self.frameInput.setValidator(rxv)
        self.playForwardsButton = QtWidgets.QPushButton("Play")
        self.nextKeyButton = QtWidgets.QPushButton("Next Key")
        self.endButton = QtWidgets.QPushButton("Go To End")

        self.layout().addStretch(1)
        self.layout().addWidget(self.startButton)
        self.layout().addWidget(self.previousKeyButton)
        self.layout().addWidget(self.playBackwardsButton)
        self.layout().addWidget(self.frameInput)
        self.layout().addWidget(self.playForwardsButton)
        self.layout().addWidget(self.nextKeyButton)
        self.layout().addWidget(self.endButton)
        self.layout().addStretch(1)

        self.startButton.clicked.connect(self._handle_startButton)
        self.previousKeyButton.clicked.connect(self._handle_previousKeyButton)
        self.playBackwardsButton.clicked.connect(self._handle_playBackwardsButton)
        self.frameInput.textChanged.connect(self._handle_frameInput)
        self.playForwardsButton.clicked.connect(self._handle_playForwardsButton)
        self.nextKeyButton.clicked.connect(self._handle_nextKeyButton)
        self.endButton.clicked.connect(self._handle_endButton)

    @QtCore.Slot()
    def _handle_startButton(self):
        self.GoToStart.emit()

    @QtCore.Slot()
    def _handle_previousKeyButton(self):
        self.GoToPreviousKeyFrame.emit()

    @QtCore.Slot()
    def _handle_playBackwardsButton(self):
        if self.playBackwardsButton.text() == "Stop":
            self.Stop.emit()
            self.playBackwardsButton.setText("Reverse")
        else:
            self.PlayBackwards.emit()
            self.playBackwardsButton.setText("Stop")
            self.playForwardsButton.setText("Play")

    @QtCore.Slot(str)
    def _handle_frameInput(self, text):
        try:
            int(text)
            self.GoToFrame.emit(int(text))
            self._previous_text = text
        except:
            self.blockSignals(True)
            self.frameInput.setText(self._previous_text)
            self.blockSignals(False)

    @QtCore.Slot()
    def _handle_playForwardsButton(self):
        if self.playForwardsButton.text() == "Stop":
            self.Stop.emit()
            self.playForwardsButton.setText("Play")
        else:
            self.PlayForwards.emit()
            self.playForwardsButton.setText("Stop")
            self.playBackwardsButton.setText("Reverse")

    @QtCore.Slot()
    def _handle_nextKeyButton(self):
        self.GoToNextKeyFrame.emit()

    @QtCore.Slot()
    def _handle_endButton(self):
        self.GoToEnd.emit()



class TimelineContainer(QtWidgets.QWidget):
    def __init__(self, start=1001, end=1100, keyframes=[], errors=[], parent=None):
        super(TimelineContainer, self).__init__(parent)
        self._current_timer = None

        self.setLayout(QtWidgets.QVBoxLayout())
        self.timeline_widget = TimelineWidget(self)
        self.timeline_widget.setRange(start, end)
        self.timeline_widget.setKeyframes(keyframes)
        self.timeline_widget.setErrors(errors)
        self.layout().addWidget(self.timeline_widget)

        self.timeline_buttons = TimelineButtons(self)
        self.layout().addWidget(self.timeline_buttons)

        self.timeline_buttons.GoToStart.connect(self.timeline_widget.goStart)
        self.timeline_buttons.GoToPreviousKeyFrame.connect(self.timeline_widget.goPreviousKeyFrame)
        self.timeline_buttons.PlayBackwards.connect(self._start_play_backwards)
        self.timeline_buttons.GoToFrame.connect(self.timeline_widget.setValue)
        self.timeline_buttons.PlayForwards.connect(self._start_play_forwards)
        self.timeline_buttons.GoToNextKeyFrame.connect(self.timeline_widget.goNextKeyFrame)
        self.timeline_buttons.GoToEnd.connect(self.timeline_widget.goEnd)
        self.timeline_buttons.Stop.connect(self._end_play)

        self.timeline_widget.valueChanged.connect(self.recieveValueChanged)


    @QtCore.Slot(int)
    def recieveValueChanged(self, value):
        self.timeline_buttons.frameInput.setText(str(value))

    def resetTimer(self):
        if self._current_timer:
            self._current_timer.stop()
            self._current_timer.deleteLater()
            self._current_timer = None

    @QtCore.Slot()
    def _end_play(self):
        self.resetTimer()

    @QtCore.Slot()
    def _start_play_backwards(self):
        if self._current_timer:
            self.resetTimer()
        self._current_timer = QtCore.QTimer(self)
        self._current_timer.timeout.connect(self.timeline_widget.previousFrame)
        self._current_timer.start(1000/30)  # 30fps?

    @QtCore.Slot()
    def _start_play_forwards(self):
        if self._current_timer:
            self.resetTimer()
        self._current_timer = QtCore.QTimer(self)
        self._current_timer.timeout.connect(self.timeline_widget.nextFrame)
        self._current_timer.start(1000/30)  # 30fps?
