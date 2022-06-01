from PyQt5 import QtWidgets
from PyQt5 import QtCore

from functools import partial


class Frame(QtWidgets.QFrame):
    """ 
    Is is QFrame with arguments in constructor for setting color,
    style and fixed height
    """
    def __init__(self, parent=None, color=None, style=None, height=None):
        super().__init__(parent)

        if color is not None:
            self.setFrameStyle(style)
        if style is not None:
            self.setStyleSheet(f"background-color: {color};")
        if height is not None:
            self.setFixedHeight(height)



class PopUpWindow(QtWidgets.QWidget):
    """
    Base class for all pop up windows in gui
    """
    def __init__(self, parent, size_w, size_h):
        super().__init__()
        self.parent = parent

        self.setStyleSheet("background-color: #444444;")
        self.outer_frame_layout = QtWidgets.QVBoxLayout(self)
        self.outer_frame = Frame(self, "gray", QtWidgets.QFrame.StyledPanel|QtWidgets.QFrame.Sunken)
        self.outer_frame_layout.addWidget(self.outer_frame)

        self.setFixedSize(size_w, size_h)
        self.center()

    def center(self):
        """ Center pop up window on parent window """
        qt = self.frameGeometry()
        cp = self.parent.frameGeometry().center()
        qt.moveCenter(cp)
        self.move(qt.topLeft())


class ColorButton(QtWidgets.QPushButton):
    """ 
    It is small QPushButton with solid color, mostly used to open QColorDialog
    """
    def __init__(self, color_r, color_g, color_b, text=None, parent=None):
        super().__init__(text, parent)
        self.setFixedHeight(20)
        self.setFixedWidth(20)
        color_style = f"QPushButton {{ background-color: rgb({color_r}, {color_g}, {color_b}); border-radius: 0px; }}"
        self.setStyleSheet(color_style)

    def get_button_color(self):
        """ Get list of three color values: r, g, b """
        return list(self.palette().color(self.backgroundRole()).getRgb()[:-1])

    def set_button_color(self, color_r, color_g, color_b):
        """ Set three color values: r, g, b """
        color_style = f"QPushButton {{ background-color: rgb({color_r}, {color_g}, {color_b}); border-radius: 0px; }}"
        self.setStyleSheet(color_style)


class JumpSlider(QtWidgets.QSlider):
    """ 
    It is QSlider with the feature of instant jumping to
    current pointer position
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.setTickInterval(1)

    def mousePressEvent(self, ev):
        """ Jump to click position """
        self.setValue(QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width()))

    def mouseMoveEvent(self, ev):
        """ Jump to pointer position while moving """
        self.setValue(QtWidgets.QStyle.sliderValueFromPosition(self.minimum(), self.maximum(), ev.x(), self.width()))


class ComboBox(QtWidgets.QComboBox):
    """ 
    Is is QComboBox with some methods overriden methods in order to make 
    ComboBox remember previous selected item
    """

    new_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.item_counter = 0
        self.lastSelected = ""
        self.activated[str].connect(self.onActivated)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed);

    def add_item(self, item):
        if self.item_counter < 1:
            self.lastSelected = item
        self.addItem(item)
        self.item_counter += 1
    
    def set_current_text(self, text):
        self.setCurrentText(text)
        self.lastSelected = text

    def onActivated(self, text):
        self.new_signal.emit(self.currentText(), text)
        self.lastSelected = text


class RadioButton(QtWidgets.QRadioButton):
    """ 
    Is is QRadioButton with some constructor that allows to set text color
    """
    def __init__(self, text, *, color="", bold="", parent=None):
        super().__init__(text, parent)
        color_style = f"QRadioButton{{ color: {color}; font: {bold}; }}"
        self.setStyleSheet(color_style)


class Label(QtWidgets.QLabel):
    """ 
    Is is QLabel with some constructor that allows to set label width and height
    """
    def __init__(self, text, *,  width=None, height=None, parent=None):
        super().__init__(text, parent)
        if width is not None:
            self.setFixedWidth(width)

        if height is not None:
            self.setFixedHeight(height)


class Button(QtWidgets.QPushButton):
    """ 
    Is is QPushButton with some constructor that allows to set button width and height etc.
    """
    def __init__(self, text, *,  width=None, height=None, func=None, parent=None):
        super().__init__(text, parent)
        if width is not None:
            self.setFixedWidth(width)

        if height is not None:
            self.setFixedHeight(height)

        if func is not None:
            self.clicked.connect(func)


class SpinBox(QtWidgets.QSpinBox):
    """ 
    Is is QSpinBox with some constructor that allows to set spin box minimum, maximum value etc.
    """
    def __init__(self, *,  width=None, height=None, minv=None, maxv=None, parent=None):
        super().__init__(parent)

        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setStyleSheet("background: white;")

        if width is not None:
            self.setFixedWidth(width)

        if height is not None:
            self.setFixedHeight(height)

        if minv is not None:
            self.setMinimum(minv)

        if maxv is not None:
            self.setMaximum(maxv)


class ButtonMenu(QtWidgets.QPushButton):
    """ 
    Is is Button with drop down menu
    """
    def __init__(self, text, menu_items=None, *, parent=None):
        super().__init__(text, parent)

        self.setStyleSheet("text-align:left; padding: 3px; padding-left: 7px;")
        self.action_menu = QtWidgets.QMenu()
        self.lastSelected = text
        self.item_counter = 0

        if menu_items is None:
            return

        for item in menu_items:
            self.action_menu.addAction(*item)

        self.setMenu(self.action_menu)

    def add_option(self, item, *args):
        func_with_arg = partial(item[1], *args)
        self.action_menu.addAction(item[0], func_with_arg)
        self.setMenu(self.action_menu)

    def set_text(self, text):
        self.lastSelected = self.text()
        self.setText(text)


class DeviceNotConnectedMessage(QtWidgets.QMessageBox):
    """
    Just a message that informs about device not being connected
    """
    def __init__(self):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Critical)
        self.setText("Device not connected!")
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec_()


class DataNotAllowed(QtWidgets.QMessageBox):
    """
    Just a message that informs about data values not being allowed (advanced settings)
    """
    def __init__(self):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setText("Such data values are not allowed!")
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec_()


class SaveProfileMessage(QtWidgets.QMessageBox):
    """
    Just a message that informs about necessity of naming current profile 
    """
    def __init__(self):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setText("Save current profile first!")
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec_()


class TooLongNameMessage(QtWidgets.QMessageBox):
    """
    Just a message that informs about the name being too long while saving
    """
    def __init__(self):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setText("Too long name! (max 50 letters)")
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec_()


class MacroNotFound(QtWidgets.QMessageBox):
    """
    Just a message that informs about the macro not being found
    """
    def __init__(self):
        super().__init__()
        self.setIcon(QtWidgets.QMessageBox.Warning)
        self.setText("Macro not found!")
        self.setStandardButtons(QtWidgets.QMessageBox.Ok)
        self.exec_()
