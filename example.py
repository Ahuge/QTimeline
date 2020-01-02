import os
import random
import sys

from Qt import QtWidgets

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "python"
    )
)

from timeline_controller import TimelineContainer

def main():

    app = QtWidgets.QApplication(sys.argv)

    # 10 Key frames
    keyframes = [random.randrange(1001, 1100) for _ in range(10)]
    # 5 errors
    errors = [random.randrange(1001, 1100) for _ in range(5)]

    ex = TimelineContainer(start=1001, end=1100, keyframes=keyframes, errors=errors, parent=None)
    ex.setStyle(QtWidgets.QStyleFactory.create("motif"))
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
