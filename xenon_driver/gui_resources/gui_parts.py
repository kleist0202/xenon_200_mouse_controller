import os
import glob
from pathlib import Path
from functools import partial

from PyQt5.QtWidgets import (
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QColorDialog,
    QSizePolicy,
    QListWidget,
    QListWidgetItem,
    QLineEdit,
    QCheckBox,
    QSpacerItem,
    QTextEdit,
    QFrame,
)

from PyQt5 import QtGui
from PyQt5 import QtCore

from xenon_driver.configuration import PROFILES_DIR, MACROS_DIR
from xenon_driver.gui_resources import custom_widgets
from xenon_driver.gui_resources import gui_keys
from xenon_driver.options import Options
from xenon_driver.logger import xenon_logger


class TopButtons(QWidget):
    def __init__(self, frame, top_buttons):
        super().__init__()

        buttons_h_layout = QHBoxLayout(frame)

        for (name, function) in top_buttons:
            btn = custom_widgets.Button(name)
            buttons_h_layout.addWidget(btn)

            btn.clicked.connect(function)


class BottomButtons(QWidget):
    def __init__(self, bottom_buttons, current_profile):
        super().__init__()

        bottom_buttons_layout = QHBoxLayout()

        self.profile_label = custom_widgets.Label("Profile: " + current_profile)
        bottom_buttons_layout.addWidget(self.profile_label)
        spacerItem = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        bottom_buttons_layout.addItem(spacerItem)

        for (name, function) in bottom_buttons:
            btn = custom_widgets.Button(name)
            btn.clicked.connect(function)
            bottom_buttons_layout.addWidget(btn)

        self.setLayout(bottom_buttons_layout)

    def set_profile_label_text(self, current_profile):
        self.profile_label.setText("Profile: " + current_profile)


class BindingsButtons(QWidget):
    def __init__(
        self, parent, bindings_frame, bindings_buttons_names, bindings_options, data, dpis_list, multimedia_keys_dict
    ):
        super().__init__()

        self.parent = parent
        self.bindings_v_layout = QVBoxLayout(bindings_frame)
        self.bindings_menus = []
        self.current_set_mode = 1

        self.bindings_buttons_names = bindings_buttons_names
        self.bindings_options = bindings_options
        self.data = data
        self.dpis_list = dpis_list
        self.multimedia_keys_dict = multimedia_keys_dict

        # pop up windows
        self.key_catcher = None
        self.snipe_dpi_selector = None
        self.fire_key_menu = None
        self.multimedia_selector = None

        # create bindings buttons
        bindings_list_layout = QGridLayout()

        for i, name in enumerate(self.bindings_buttons_names):
            start_mode = "mode1"
            buttons_menu = custom_widgets.ButtonMenu(
                self.data.settings_yml["bindings_data"][start_mode][name]["name"]
            )
            for opt in self.bindings_options:
                buttons_menu.add_option((opt, self.on_special_combo_box_item), i, opt)

            label = custom_widgets.Label(str(i + 1) + ".", width=10)
            bindings_list_layout.addWidget(label, i, 0)
            bindings_list_layout.addWidget(buttons_menu, i, 1)
            self.bindings_menus.append(buttons_menu)

        hspacer = QSpacerItem(QSizePolicy.Expanding, QSizePolicy.Minimum)
        bindings_list_layout.addItem(hspacer, 10, 1)

        # create three modes buttons
        modes_layout = QHBoxLayout()

        mode1 = custom_widgets.RadioButton("Mode1", color="#0000ff", bold="bold")
        mode2 = custom_widgets.RadioButton("Mode2", color="#ff0000", bold="bold")
        mode3 = custom_widgets.RadioButton("Mode3", color="#00ff00", bold="bold")

        mode1.clicked.connect(self.on_mode_changed)
        mode2.clicked.connect(self.on_mode_changed)
        mode3.clicked.connect(self.on_mode_changed)

        mode1.mode = 1
        mode2.mode = 2
        mode3.mode = 3

        mode1.setChecked(True)

        modes_layout.addWidget(
            mode1,
        )
        modes_layout.addWidget(mode2, alignment=QtCore.Qt.AlignCenter)
        modes_layout.addWidget(mode3, alignment=QtCore.Qt.AlignRight)

        # add everything to layout
        self.bindings_v_layout.addLayout(modes_layout)
        self.bindings_v_layout.addLayout(bindings_list_layout)

    def on_mode_changed(self):
        radio_button = self.sender()
        current_mode = radio_button.mode
        self.current_set_mode = current_mode
        mode = f"mode{current_mode}"
        for i, name in enumerate(self.bindings_buttons_names):
            self.bindings_menus[i].set_text(
                self.data.settings_yml["bindings_data"][mode][name]["name"]
            )

    def on_special_combo_box_item(self, i, text):
        self.bindings_menus[i].set_text(text)
        last_selected = self.bindings_menus[i].lastSelected

        if text == "Keys combination":
            self.key_catcher = KeyCombinationCatcher(self.parent, i, last_selected)
            self.key_catcher.setWindowModality(QtCore.Qt.ApplicationModal)
            self.key_catcher.ok_pressed.connect(self.on_keys_applied)
            self.key_catcher.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.key_catcher.show()
        elif text == "Snipe button":
            self.snipe_dpi_selector = SnipeDpiSelector(
                self.parent, self.dpis_list, 0, i, last_selected
            )
            self.snipe_dpi_selector.setWindowModality(QtCore.Qt.ApplicationModal)
            self.snipe_dpi_selector.ok_pressed.connect(self.on_snipe_dpi_applied)
            self.snipe_dpi_selector.cancel_pressed.connect(
                self.on_cancel_button_pressed
            )
            self.snipe_dpi_selector.show()
        elif text == "Fire key":
            self.fire_key_menu = FireKeyMenu(self.parent, i, last_selected)
            self.fire_key_menu.setWindowModality(QtCore.Qt.ApplicationModal)
            self.fire_key_menu.ok_pressed.connect(self.on_fire_key_applied)
            self.fire_key_menu.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.fire_key_menu.show()
        elif text == "Multimedia":
            self.multimedia_selector = MultimediaKeysSelector(
                self.parent, 200, 300, self.multimedia_keys_dict, i, last_selected
            )
            self.multimedia_selector.setWindowModality(QtCore.Qt.ApplicationModal)
            self.multimedia_selector.ok_pressed.connect(
                self.on_multimedia_ok_button_pressed
            )
            self.multimedia_selector.cancel_pressed.connect(
                self.on_cancel_button_pressed
            )
            self.multimedia_selector.show()
        elif text == "Macro":
            self.multimedia_selector = MacroSelector(
                self.parent, 200, 300, i, last_selected
            )
            self.multimedia_selector.setWindowModality(QtCore.Qt.ApplicationModal)
            self.multimedia_selector.ok_pressed.connect(self.on_macro_button_pressed)
            self.multimedia_selector.cancel_pressed.connect(
                self.on_cancel_button_pressed
            )
            self.multimedia_selector.show()

    def on_keys_applied(self, keys_catched):
        key_catcher = self.sender()
        self.bindings_menus[key_catcher.key_num].set_text(
            f"Keys combination - {keys_catched}"
        )

    def on_multimedia_ok_button_pressed(self, multimedia_name):
        multimedia_selector = self.sender()
        self.bindings_menus[multimedia_selector.key_num].set_text(
            f"Multimedia - {multimedia_name}"
        )

    def on_cancel_button_pressed(self):
        some_pop_up_window = self.sender()
        self.bindings_menus[some_pop_up_window.key_num].set_text(
            some_pop_up_window.previous
        )

    def on_snipe_dpi_applied(self, dpi_value):
        snipe_button = self.sender()
        self.bindings_menus[snipe_button.key_num].set_text(
            f"Snipe button - {dpi_value}"
        )

    def on_macro_button_pressed(self, file_name):
        some_pop_up_window = self.sender()
        self.bindings_menus[some_pop_up_window.key_num].set_text(f"Macro - {file_name}")

    def on_fire_key_applied(self, key, delay, times):
        fire_key_button = self.sender()
        self.bindings_menus[fire_key_button.key_num].set_text(
            f"Fire key - {key},{delay}ms,{times}"
        )


class LedChanger(QWidget):
    def __init__(self, data, current_led_mode):
        """
        data:
            { "key" : [
                mode,
                label_name,
                [ text, ... ],
                [ data, ... ],
                is_color, is_combobox,
                [ r, g, b ],
                current_option
                ],
                ...
            }
        """
        super().__init__()
        self.data = data
        self.current_led_mode = current_led_mode
        self.mode_widgets = (
            {}
        )  # { radio_button : [combo_box, color_button, led_mode_label, color_label] }

        main_led_layout = QVBoxLayout()
        led_layout = QGridLayout()

        title = custom_widgets.Label("Led modes")
        main_led_layout.addWidget(title)

        for row, (mode_name, data) in enumerate(self.data.items(), start=1):
            led_mode_label = custom_widgets.Label(mode_name, width=40)
            led_preference_label = custom_widgets.Label(data[1], height=20)

            radio_button = custom_widgets.RadioButton("")
            radio_button.setFixedHeight(20)
            radio_button.setFixedWidth(20)
            radio_button.mode = data[0]
            radio_button.clicked.connect(self.on_led_mode_changed)
            self.mode_widgets[radio_button] = []

            led_layout.addWidget(radio_button, row * 2 + 1, 0)
            led_layout.addWidget(led_mode_label, row * 2 + 1, 1)

            is_cb = data[4]
            is_color = data[5]

            combo_box = custom_widgets.ComboBox()
            for text, value in zip(data[2], data[3]):
                combo_box.addItem(str(text), value)

            led_layout.addWidget(combo_box, row * 2 + 1, 2)
            led_layout.addWidget(led_preference_label, row * 2 + 0, 2)
            combo_box.setCurrentIndex(combo_box.findData(data[7]))

            if not is_cb:
                combo_box.hide()

            color_r, color_g, color_b = data[6]
            color_button = custom_widgets.ColorButton(color_r, color_g, color_b)
            color_label = custom_widgets.Label("Color")
            led_layout.addWidget(color_button, row * 2 + 1, 3)
            led_layout.addWidget(
                color_label, row * 2 + 0, 3, alignment=QtCore.Qt.AlignLeft
            )
            color_button.clicked.connect(self.color_picker_pop_up)

            if not is_color:
                color_button.hide()
                color_label.hide()

            led_layout.setVerticalSpacing(0)

            if mode_name == self.current_led_mode:
                radio_button.setChecked(True)

            self.mode_widgets[radio_button].append(combo_box)
            self.mode_widgets[radio_button].append(color_button)
            self.mode_widgets[radio_button].append(led_mode_label)
            self.mode_widgets[radio_button].append(color_label)

        main_led_layout.addLayout(led_layout)

        # set all that are not checked to be disabled
        for rb, widgets in self.mode_widgets.items():
            if not rb.isChecked():
                for widget in widgets:
                    widget.setDisabled(True)

        # set main layout
        self.setLayout(main_led_layout)

    def set_mode(self, mode):
        for rb, widgets in self.mode_widgets.items():
            if widgets[2].text() == mode:
                rb.setChecked(True)
                rb.clicked.emit()

    def set_options(self, options):
        for i, (_, widgets) in enumerate(self.mode_widgets.items()):
            item_index = widgets[0].findData(options[i])
            widgets[0].setCurrentText(widgets[0].itemText(item_index))

    def set_color(self, colors):
        for i, (_, widgets) in enumerate(self.mode_widgets.items()):
            widgets[1].set_button_color(*colors[i])

    def color_picker_pop_up(self):
        steady_color_button = self.sender()
        qcd = QColorDialog()
        qcd.setCurrentColor(
            QtGui.QColor.fromRgb(*steady_color_button.get_button_color())
        )
        qcd.exec_()
        color = qcd.selectedColor()
        if not color.isValid():
            return
        steady_color_button.set_button_color(
            color.toRgb().red(), color.toRgb().green(), color.toRgb().blue()
        )

    def on_led_mode_changed(self):
        current_radio_button = self.sender()

        for rb, widgets in self.mode_widgets.items():
            if rb != current_radio_button:
                for widget in widgets:
                    widget.setDisabled(True)
            else:
                for widgets in widgets:
                    widgets.setDisabled(False)


class ReportRateButtons(QWidget):
    def __init__(self, rr_buttons_names, current_set_rr):
        super().__init__()

        self.rr_buttons = []
        self.current_set_rr = current_set_rr
        self.rr_buttons_names = rr_buttons_names

        rr_layout = QHBoxLayout()

        rr_info_label = custom_widgets.Label("Report rate")
        rr_unit_label = custom_widgets.Label("Hz")

        rr_layout.addWidget(rr_info_label)
        rr_layout.addItem(QSpacerItem(10, 0))

        for (name, _) in self.rr_buttons_names:
            rr_button = custom_widgets.Button(
                name, func=self.report_rate_button_clicked
            )
            rr_layout.addWidget(rr_button)
            self.rr_buttons.append(rr_button)

        for i, (name, val) in enumerate(self.rr_buttons_names):
            if val == self.current_set_rr:
                self.rr_buttons[i].setStyleSheet("background: #333333; color: white;")

        rr_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Minimum))
        rr_layout.addWidget(rr_unit_label)
        rr_layout.setSpacing(0)

        # set main layout
        self.setLayout(rr_layout)

    def report_rate_button_clicked(self):
        rr_button = self.sender()
        for btn in self.rr_buttons:
            if btn != rr_button:
                btn.setStyleSheet("background: #777777; color: black;")
            else:
                btn.setStyleSheet("background: #333333; color: white;")

        for name, val in self.rr_buttons_names:
            if rr_button.text() == name:
                self.current_set_rr = val

    def set_report_rate(self, rr):
        self.current_set_rr = rr

        for btn in self.rr_buttons:
            btn.setStyleSheet("background: #777777; color: black;")

        for i, (_, val) in enumerate(self.rr_buttons_names):
            if val == self.current_set_rr:
                self.rr_buttons[i].setStyleSheet("background: #333333; color: white;")


class DpiSliders(QWidget):
    def __init__(self, starting_values, dpi_values):
        super().__init__()

        self.dpi_labels_list = []
        self.dpi_sliders_list = []
        self.dpi_check_boxes_list = []

        self.dpi_values = dpi_values
        dpi_sliders_layout = QGridLayout()
        dpi_sliders_layout.addWidget(custom_widgets.Label("DPI"), 0, 0)

        for i in range(4):
            dpi_slider = custom_widgets.JumpSlider(QtCore.Qt.Horizontal)
            dpi_slider.setMinimum(1)
            dpi_slider.setMaximum(len(dpi_values))

            low_nibble = starting_values[i] & 0x0F
            high_nibble = starting_values[i] & 0xF0

            dpi_slider.setValue(low_nibble)

            func = partial(self.on_slider_value_changed, i + 1)
            dpi_slider.valueChanged.connect(func)

            dpi_check_box = QCheckBox()

            if high_nibble != Options.BLOCKED_DPI_LEVEL_MASK:
                dpi_check_box.setChecked(True)

            current_dpi_label = custom_widgets.Label(dpi_values[low_nibble - 1][0])

            self.dpi_labels_list.append(current_dpi_label)
            self.dpi_sliders_list.append(dpi_slider)
            self.dpi_check_boxes_list.append(dpi_check_box)

            dpi_sliders_layout.addWidget(dpi_check_box, i + 1, 0)
            dpi_sliders_layout.addWidget(dpi_slider, i + 1, 1)
            dpi_sliders_layout.addWidget(current_dpi_label, i + 1, 2)

        # set main layout
        self.setLayout(dpi_sliders_layout)

    def on_slider_value_changed(self, num):
        current_dpi_slider = self.sender()
        self.dpi_labels_list[num - 1].setText(
            self.dpi_values[current_dpi_slider.value() - 1][0]
        )

    def set_sliders_values(self, starting_values):
        for i in range(4):
            low_nibble = starting_values[i] & 0x0F
            high_nibble = starting_values[i] & 0xF0
            self.dpi_sliders_list[i].setValue(low_nibble)

            if high_nibble != Options.BLOCKED_DPI_LEVEL_MASK:
                self.dpi_check_boxes_list[i].setChecked(True)
            else:
                self.dpi_check_boxes_list[i].setChecked(False)


class KeyCombinationCatcher(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(str)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent, key_num, previous):
        super().__init__(parent, 300, 120)
        self.key_num = key_num
        self.previous = previous

        key_catcher_layout = QVBoxLayout(self.outer_frame)
        buttons_layouts = QHBoxLayout()

        info_label = custom_widgets.Label("Enter keystroke:")

        self.keys_label = custom_widgets.Label("", height=20)
        self.keys_label.setStyleSheet("background: white;")
        self.keys_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.keys_label.setAlignment(QtCore.Qt.AlignCenter)

        ok_button = custom_widgets.Button("Ok", width=75, func=self.save_combination)

        cancel_button = custom_widgets.Button(
            "Cancel", width=75, func=self.cancel_button_pressed
        )

        key_catcher_layout.addWidget(info_label)
        key_catcher_layout.addWidget(self.keys_label)

        buttons_layouts.addWidget(
            cancel_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom
        )
        buttons_layouts.addWidget(ok_button)

        key_catcher_layout.addLayout(buttons_layouts)

        self.pressed_keys_list = []
        self.pressed_modifiers_list = []
        self.keys_dict = gui_keys.GuiKeys.keys_dict

    def keyPressEvent(self, e):
        pressed_key = e.key()
        if pressed_key in [
            QtCore.Qt.Key_Control,
            QtCore.Qt.Key_Alt,
            QtCore.Qt.Key_Shift,
            QtCore.Qt.Key_Super_L,
        ]:
            if pressed_key not in self.pressed_modifiers_list:
                self.pressed_modifiers_list.append(pressed_key)

        # if there are already two keys or key was already pressed
        if not (
            len(self.pressed_keys_list) > 1 or (len(self.pressed_keys_list) == 1 and pressed_key == self.pressed_keys_list[0])
        ):

            if pressed_key not in [
                QtCore.Qt.Key_Control,
                QtCore.Qt.Key_Alt,
                QtCore.Qt.Key_Shift,
                QtCore.Qt.Key_Super_L,
            ]:
                self.pressed_keys_list.append(pressed_key)

        try:
            keys = [self.keys_dict[k][0] for k in self.pressed_keys_list]
        except KeyError:
            self.pressed_keys_list.pop()
            xenon_logger.warning(f"No such key {pressed_key}")
            return

        modifiers_keys = [self.keys_dict[k][0] for k in self.pressed_modifiers_list]
        catcher_text = "+".join(modifiers_keys)
        if len(keys) != 0 and len(modifiers_keys) != 0:
            catcher_text += "+"

        catcher_text += "+".join(keys)
        self.keys_label.setText(catcher_text)

    def save_combination(self):
        if len(self.pressed_keys_list) != 0 or len(self.pressed_modifiers_list) != 0:
            text = self.keys_label.text()
            self.ok_pressed.emit(text)

            self.close()

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()


class SnipeDpiSelector(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(str)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent, dpi_values_dict, starting_value, key_num, previous):
        super().__init__(parent, 300, 120)

        self.dpi_values_dict = dpi_values_dict
        self.key_num = key_num
        self.previous = previous
        self.dpi_label = custom_widgets.Label(self.dpi_values_dict[starting_value][0])

        snipe_dpi_selector_layout = QVBoxLayout(self.outer_frame)

        selector_layout = QHBoxLayout()
        buttons_layout = QHBoxLayout()

        self.snipe_dpi_slider = custom_widgets.JumpSlider(QtCore.Qt.Horizontal)

        self.snipe_dpi_slider.setMinimum(1)
        self.snipe_dpi_slider.setMaximum(len(self.dpi_values_dict))

        self.snipe_dpi_slider.setValue(starting_value + 1)

        self.snipe_dpi_slider.valueChanged.connect(self.on_slider_value_changed)

        selector_layout.addWidget(custom_widgets.Label("DPI"))
        selector_layout.addWidget(self.snipe_dpi_slider)
        selector_layout.addWidget(self.dpi_label)

        ok_button = custom_widgets.Button("Ok")
        cancel_button = custom_widgets.Button("Cancel")

        ok_button.clicked.connect(self.ok_button_preseed)
        cancel_button.clicked.connect(self.cancel_button_pressed)

        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)

        snipe_dpi_selector_layout.addWidget(custom_widgets.Label("Snipe button"))
        snipe_dpi_selector_layout.addLayout(selector_layout)
        snipe_dpi_selector_layout.addLayout(buttons_layout)

    def on_slider_value_changed(self):
        for i, dpi_value in enumerate(self.dpi_values_dict, start=1):
            if i == self.snipe_dpi_slider.value():
                self.dpi_label.setText(dpi_value[0])

    def ok_button_preseed(self):
        self.ok_pressed.emit(self.dpi_label.text())
        self.close()

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()


class KeyCatcher(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(list)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent, 300, 120)

        self.keys_dict = gui_keys.GuiKeys.keys_dict
        self.pressed_key = None

        key_catcher_layout = QVBoxLayout(self.outer_frame)
        buttons_layouts = QHBoxLayout()

        info_label = custom_widgets.Label("Enter keystroke:")

        self.keys_label = custom_widgets.Label("", height=20)
        self.keys_label.setStyleSheet("background: white;")
        self.keys_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.keys_label.setAlignment(QtCore.Qt.AlignCenter)

        ok_button = custom_widgets.Button("Ok", width=75, func=self.save_key)
        cancel_button = custom_widgets.Button(
            "Cancel", width=75, func=self.cancel_button_pressed
        )

        key_catcher_layout.addWidget(info_label)
        key_catcher_layout.addWidget(self.keys_label)

        buttons_layouts.addWidget(
            cancel_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom
        )
        buttons_layouts.addWidget(ok_button)

        key_catcher_layout.addLayout(buttons_layouts)

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()

    def save_key(self):
        if self.pressed_key is None:
            return
        key_text = self.keys_dict[self.pressed_key][0]
        key_drver_value = self.keys_dict[self.pressed_key][1]
        self.ok_pressed.emit([key_text, key_drver_value])
        self.close()

    def keyPressEvent(self, e):
        pressed_key = e.key()
        try:
            key_text = self.keys_dict[pressed_key]
        except KeyError:
            xenon_logger.warning(f"No such key {pressed_key}")
            return
        self.pressed_key = pressed_key
        self.keys_label.setText(key_text[0])


class FireKeyMenu(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(str, int, int)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent, key_num, previous):
        super().__init__(parent, 360, 150)

        self.key_num = key_num
        self.keys_dict = gui_keys.GuiKeys.keys_dict
        self.previous = previous
        self.parent = parent
        self.current_button = gui_keys.GuiKeys.MOUSE_KEYS["Left button"]
        self.current_delay = 30
        self.current_times = 1
        self.fire_key_catcher = None

        fire_key_menu_layout = QVBoxLayout(self.outer_frame)
        actions_layout = QGridLayout()
        buttons_layout = QHBoxLayout()

        action_label = custom_widgets.Label("action", height=20)
        delay_label = custom_widgets.Label(f"delay ({self.current_delay}-255)")
        times_label = custom_widgets.Label(f"times ({self.current_times}-255)")

        menu_items = [
            ("Left button", self.left_button_chosen),
            ("Right button", self.right_button_chosen),
            ("Middle button", self.middle_button_chosen),
            ("Keystroke", self.keystroke_chosen),
        ]

        self.action_menu_button = custom_widgets.ButtonMenu("Left button", menu_items)

        delay_entry = custom_widgets.SpinBox(
            width=90, minv=self.current_delay, maxv=255
        )
        delay_entry.valueChanged.connect(self.on_delay_changed)

        times_entry = custom_widgets.SpinBox(
            width=90, minv=self.current_times, maxv=255
        )
        times_entry.valueChanged.connect(self.on_times_changed)

        ok_button = custom_widgets.Button("Ok")
        cancel_button = custom_widgets.Button("Cancel")

        ok_button.clicked.connect(self.ok_button_preseed)
        cancel_button.clicked.connect(self.cancel_button_pressed)

        actions_layout.addWidget(action_label, 0, 0)
        actions_layout.addWidget(delay_label, 0, 1)
        actions_layout.addWidget(times_label, 0, 2)

        actions_layout.addWidget(self.action_menu_button, 1, 0)
        actions_layout.addWidget(delay_entry, 1, 1)
        actions_layout.addWidget(times_entry, 1, 2)

        buttons_layout.addItem(QSpacerItem(150, 0))
        buttons_layout.addWidget(cancel_button, alignment=QtCore.Qt.AlignBottom)
        buttons_layout.addWidget(ok_button, alignment=QtCore.Qt.AlignBottom)

        actions_layout.setVerticalSpacing(0)

        fire_key_menu_layout.addLayout(actions_layout)
        fire_key_menu_layout.addLayout(buttons_layout)

    def on_delay_changed(self, i):
        self.current_delay = i

    def on_times_changed(self, i):
        self.current_times = i

    def ok_button_preseed(self):
        key_text = self.action_menu_button.text()
        delay = self.current_delay
        times = self.current_times
        self.ok_pressed.emit(key_text, delay, times)
        self.close()

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()

    def fire_catcher_applied(self, text_and_value):
        self.action_menu_button.setText(text_and_value[0])
        self.current_button = text_and_value[1]

    def left_button_chosen(self):
        self.current_button = gui_keys.GuiKeys.MOUSE_KEYS["Left button"]
        self.action_menu_button.setText("Left button")

    def right_button_chosen(self):
        self.current_button = gui_keys.GuiKeys.MOUSE_KEYS["Right button"]
        self.action_menu_button.setText("Right button")

    def middle_button_chosen(self):
        self.current_button = gui_keys.GuiKeys.MOUSE_KEYS["Middle button"]
        self.action_menu_button.setText("Middle button")

    def keystroke_chosen(self):
        self.fire_key_catcher = KeyCatcher(self)
        self.fire_key_catcher.setWindowModality(QtCore.Qt.ApplicationModal)
        self.fire_key_catcher.ok_pressed.connect(self.fire_catcher_applied)
        self.fire_key_catcher.show()


class MultimediaKeysSelector(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(str)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent, size_w, size_h, multimedia_keys_dict, key_num, previous):
        super().__init__(parent, size_w, size_h)

        multimedia_keys_layout = QVBoxLayout(self.outer_frame)
        buttons_layout = QHBoxLayout()

        self.multimedia_keys_dict = multimedia_keys_dict

        self.key_num = key_num
        self.previous = previous

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: white;")

        for key in self.multimedia_keys_dict:
            item = QListWidgetItem(key)
            self.list_widget.addItem(item)

        ok_button = custom_widgets.Button("Ok")
        cancel_button = custom_widgets.Button("Cancel")

        ok_button.clicked.connect(self.ok_button_preseed)
        cancel_button.clicked.connect(self.cancel_button_pressed)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(ok_button)

        multimedia_keys_layout.addWidget(self.list_widget)
        multimedia_keys_layout.addLayout(buttons_layout)

    def ok_button_preseed(self):
        chosen_name = self.list_widget.currentItem().text()
        # chosen_key = self.multimedia_keys_dict[chosen_name]
        self.ok_pressed.emit(chosen_name)
        self.close()

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()


class MacroSelector(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(str)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent, size_w, size_h, key_num, previous):
        super().__init__(parent, size_w, size_h)

        macro_selector_layout = QVBoxLayout(self.outer_frame)
        buttons_layout = QHBoxLayout()

        self.key_num = key_num
        self.previous = previous

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: white;")

        files_paths = glob.glob(MACROS_DIR + "*")
        files = [Path(file).stem for file in files_paths]

        for file in files:
            self.list_widget.addItem(QListWidgetItem(file))

        ok_button = custom_widgets.Button("Ok")
        cancel_button = custom_widgets.Button("Cancel")

        ok_button.clicked.connect(self.ok_button_preseed)
        cancel_button.clicked.connect(self.cancel_button_pressed)

        buttons_layout.addWidget(cancel_button)
        buttons_layout.addWidget(ok_button)

        macro_selector_layout.addWidget(self.list_widget)
        macro_selector_layout.addLayout(buttons_layout)

    def ok_button_preseed(self):
        chosen_name = self.list_widget.currentItem().text()
        self.ok_pressed.emit(chosen_name)
        self.close()

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()


class ProfilesManager(custom_widgets.PopUpWindow):
    load_pressed = QtCore.pyqtSignal(str)
    save_pressed = QtCore.pyqtSignal(str)

    PROFILES_EXTENSION = ".yml"

    def __init__(self, parent, path, starting_profile):
        super().__init__(parent, 300, 400)

        profiles_manager_layout = QHBoxLayout(self.outer_frame)

        self.list_widget = QListWidget()
        self.list_widget.setStyleSheet("background: white;")

        files_paths = glob.glob(path + "*" + ProfilesManager.PROFILES_EXTENSION)
        files = [Path(file).stem for file in files_paths]

        for file in files:
            self.list_widget.addItem(QListWidgetItem(file))

        current_profile_item = self.list_widget.findItems(
            starting_profile, QtCore.Qt.MatchExactly
        )
        if current_profile_item:
            self.list_widget.setCurrentItem(current_profile_item[0])

        save_label = custom_widgets.Label("Enter profile name:", height=20)
        self.entry_widget = QLineEdit()
        self.entry_widget.setStyleSheet("background: white;")

        cancel_button = custom_widgets.Button("Cancel", func=self.close)
        save_button = custom_widgets.Button("Save profile", func=self.save_and_close)
        delete_button = custom_widgets.Button(
            "Delete profile", func=self.delete_profile
        )
        load_button = custom_widgets.Button("Load", func=self.load_and_close)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(save_label)
        buttons_layout.addWidget(self.entry_widget)
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addWidget(load_button, alignment=QtCore.Qt.AlignBottom)
        buttons_layout.addWidget(cancel_button)

        profiles_manager_layout.addWidget(self.list_widget)
        profiles_manager_layout.addLayout(buttons_layout)

    def load_and_close(self):
        loaded_file_name = self.list_widget.currentItem().text()
        self.load_pressed.emit(loaded_file_name)
        self.close()

    def save_and_close(self):
        saved_file_name = self.entry_widget.displayText()
        if len(saved_file_name) > 50:
            custom_widgets.TooLongNameMessage()
            return
        if saved_file_name:
            self.save_pressed.emit(saved_file_name)
            self.close()

    def delete_profile(self):
        # end function instantly if no items exists
        if not self.list_widget.count():
            return

        current_item = self.list_widget.currentItem()
        file_name = current_item.text()

        listItems = self.list_widget.selectedItems()

        if not listItems:
            return

        for item in listItems:
            self.list_widget.takeItem(self.list_widget.row(item))

        os.remove(PROFILES_DIR + file_name + ProfilesManager.PROFILES_EXTENSION)


class EnterDelay(custom_widgets.PopUpWindow):
    ok_pressed = QtCore.pyqtSignal(int)
    cancel_pressed = QtCore.pyqtSignal()

    def __init__(self, parent, max_delay):
        super().__init__(parent, 300, 120)

        self.keys_dict = gui_keys.GuiKeys.keys_dict

        delay_enter_layout = QVBoxLayout(self.outer_frame)
        buttons_layouts = QHBoxLayout()

        info_label = custom_widgets.Label("Enter delay:")

        self.delay_spin_box = custom_widgets.SpinBox(minv=1, maxv=max_delay)

        ok_button = custom_widgets.Button("Ok", width=75, func=self.save_delay)
        cancel_button = custom_widgets.Button(
            "Cancel", width=75, func=self.cancel_button_pressed
        )

        delay_enter_layout.addWidget(info_label)
        delay_enter_layout.addWidget(self.delay_spin_box)

        buttons_layouts.addWidget(
            cancel_button, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom
        )
        buttons_layouts.addWidget(ok_button)

        delay_enter_layout.addLayout(buttons_layouts)

    def cancel_button_pressed(self):
        self.cancel_pressed.emit()
        self.close()

    def save_delay(self):
        delay_value = self.delay_spin_box.value()
        self.ok_pressed.emit(delay_value)
        self.close()


class MacroCreator(custom_widgets.PopUpWindow):
    MAX_DELAY = 25627

    def __init__(self, parent, size_w, size_h):
        super().__init__(parent, size_w, size_h)

        widgets_layout = QVBoxLayout(self.outer_frame)

        widgets_frame = custom_widgets.Frame(self, "gray", QFrame.Box | QFrame.Sunken)
        macro_creator_layout = QHBoxLayout(widgets_frame)

        macro_list_layout = QVBoxLayout()
        key_list_layout = QVBoxLayout()
        options_layout = QVBoxLayout()
        bottom_buttons_layout = QHBoxLayout()

        self.macro_list_widget = QListWidget()
        self.macro_list_widget.setFixedWidth(180)
        self.macro_list_widget.setStyleSheet("background: white;")
        self.macro_list_widget.itemClicked.connect(self.change_selected_macro)

        # set first item as selected
        current_macro_item = self.macro_list_widget.itemAt(0, 0)
        if current_macro_item:
            self.macro_list_widget.setCurrentItem(current_macro_item[0])

        self.key_list_widget = QListWidget()
        self.key_list_widget.setFixedWidth(140)
        self.key_list_widget.setStyleSheet("background: white;")

        self.until_key_released = custom_widgets.RadioButton(
            "Cycle until the key released"
        )
        self.until_key_pressed = custom_widgets.RadioButton(
            "Cycle until any key pressed"
        )
        self.cycle_times = custom_widgets.RadioButton("Specified cycle times")
        self.cycle_times.setChecked(True)

        self.until_key_pressed.clicked.connect(self.on_radio_button_checked)
        self.until_key_released.clicked.connect(self.on_radio_button_checked)
        self.cycle_times.clicked.connect(self.on_radio_button_checked)

        self.cycle_entry = custom_widgets.SpinBox(width=90, minv=1, maxv=65535)

        insert_event_label = custom_widgets.Label("Insert event")

        list_of_events = [
            ("Key down", self.key_down_event),
            ("Key up", self.key_up_event),
            ("Delay", self.delay_event),
            ("Left button", self.left_button_event),
            ("Right button", self.right_button_event),
            ("Middle button", self.middle_button_event),
        ]
        self.events_menu = custom_widgets.ButtonMenu("Choose event", list_of_events)
        self.events_menu.setFixedWidth(150)

        self.macro_name_line_edit = QLineEdit()
        self.macro_name_line_edit.setFixedWidth(180)
        self.macro_name_line_edit.setStyleSheet("background: white")

        vspacer = QSpacerItem(10, 100)
        vspacer2 = QSpacerItem(10, 250)

        macro_list_save_button = custom_widgets.Button("Save", func=self.save_macro)
        macro_list_delete_button = custom_widgets.Button(
            "Delete", func=self.delete_macro
        )

        key_list_modify_button = custom_widgets.Button(
            "Modify", width=70, func=self.modify_item
        )
        key_list_delete_button = custom_widgets.Button(
            "Delete", width=70, func=self.delete_item
        )

        cancel_button = custom_widgets.Button("Cancel", func=self.close)
        hspacer = QSpacerItem(100, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

        options_layout.addItem(vspacer)
        options_layout.addWidget(self.until_key_released)
        options_layout.addWidget(self.until_key_pressed)
        options_layout.addWidget(self.cycle_times)
        options_layout.addWidget(self.cycle_entry)
        options_layout.addWidget(insert_event_label)
        options_layout.addWidget(self.events_menu)
        options_layout.addItem(vspacer2)

        macro_list_layout.addWidget(self.macro_list_widget)
        macro_list_layout.addWidget(self.macro_name_line_edit)
        key_list_layout.addWidget(self.key_list_widget)

        macro_list_buttons_layout = QHBoxLayout()
        macro_list_buttons_layout.setSpacing(0)
        macro_list_buttons_layout.addWidget(macro_list_save_button)
        macro_list_buttons_layout.addWidget(macro_list_delete_button)

        key_list_buttons_layout = QHBoxLayout()
        key_list_buttons_layout.setSpacing(0)
        key_list_buttons_layout.addWidget(key_list_modify_button)
        key_list_buttons_layout.addWidget(key_list_delete_button)

        macro_list_layout.addLayout(macro_list_buttons_layout)
        key_list_layout.addLayout(key_list_buttons_layout)

        bottom_buttons_layout.addItem(hspacer)
        bottom_buttons_layout.addWidget(cancel_button)

        macro_creator_layout.addLayout(macro_list_layout)
        macro_creator_layout.addLayout(key_list_layout)
        macro_creator_layout.addLayout(options_layout)
        widgets_layout.addWidget(widgets_frame)
        widgets_layout.addLayout(bottom_buttons_layout)

        self.update_macros()

    def save_macro(self):
        saved_file_name = self.macro_name_line_edit.displayText()
        if len(saved_file_name) > 50:
            custom_widgets.TooLongNameMessage()
            return
        if saved_file_name:
            whole_delay = 0
            start_stalking = False
            delay_items = 0
            current_index = 0
            is_first_item_delay = True

            # merge delays
            while current_index < self.key_list_widget.count():
                item = self.key_list_widget.item(current_index).text()

                if item.startswith("Delay"):
                    if is_first_item_delay:
                        self.key_list_widget.takeItem(current_index)
                        continue
                    delay_items += 1
                    start_stalking = True
                    whole_delay += int(
                        item.split("-")[1].replace(" ", "").replace("ms", "")
                    )
                else:
                    is_first_item_delay = False
                    if start_stalking:

                        # check limit
                        if whole_delay > MacroCreator.MAX_DELAY:
                            whole_delay = MacroCreator.MAX_DELAY

                        full_text = f"Delay - {whole_delay} ms"
                        for j in range(delay_items):
                            self.key_list_widget.takeItem(current_index - j - 1)

                        self.key_list_widget.insertItem(
                            current_index - delay_items, full_text
                        )

                        current_index -= delay_items - 1
                        start_stalking = False
                        whole_delay = 0
                        delay_items = 0
                        continue
                current_index += 1

            # if there is a few delays at the end of list proceed one more time(ugly af)
            if start_stalking:
                start_stalking = False

                # check limit
                if whole_delay > MacroCreator.MAX_DELAY:
                    whole_delay = MacroCreator.MAX_DELAY

                full_text = f"Delay - {whole_delay} ms"
                for j in range(delay_items):
                    self.key_list_widget.takeItem(current_index - j - 1)

                self.key_list_widget.insertItem(current_index - delay_items, full_text)
                whole_delay = 0
                delay_items = 0

            with open(MACROS_DIR + saved_file_name, "w") as file:
                if self.cycle_times.isChecked():
                    file.write(f"1,{self.cycle_entry.value()}:")
                elif self.until_key_pressed.isChecked():
                    file.write("2,1:")
                elif self.until_key_released.isChecked():
                    file.write("4,1:")

                for i in range(self.key_list_widget.count()):
                    file.write(self.key_list_widget.item(i).text())
                    if i != self.key_list_widget.count() - 1:
                        file.write(",")

        self.update_macros()

    def update_macros(self):
        files_paths = glob.glob(MACROS_DIR + "*")
        files = [Path(file).stem for file in files_paths]
        self.macro_list_widget.clear()

        for file in files:
            self.macro_list_widget.addItem(QListWidgetItem(file))

    def delete_macro(self):
        # end function instantly if no items exists
        if not self.macro_list_widget.count():
            return

        current_item = self.macro_list_widget.currentItem()
        if current_item is None:
            return

        self.macro_list_widget.takeItem(self.macro_list_widget.row(current_item))

        file_name = current_item.text()
        os.remove(MACROS_DIR + file_name)

        self.change_selected_macro()

    def left_button_event(self):
        self.events_menu.setText("Left button")
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            index = 0
            self.key_list_widget.insertItem(index + 1, "Left button - Down")
            self.key_list_widget.insertItem(index + 2, "Left button - Up")
            self.key_list_widget.setCurrentRow(index + 1)
        else:
            index = self.key_list_widget.row(current_item)
            self.key_list_widget.insertItem(index + 1, "Left button - Down")
            self.key_list_widget.insertItem(index + 2, "Left button - Up")
            self.key_list_widget.setCurrentRow(index + 2)

    def right_button_event(self):
        self.events_menu.setText("Right button")
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            index = 0
            self.key_list_widget.insertItem(index + 1, "Right button - Down")
            self.key_list_widget.insertItem(index + 2, "Right button - Up")
            self.key_list_widget.setCurrentRow(index + 1)
        else:
            index = self.key_list_widget.row(current_item)
            self.key_list_widget.insertItem(index + 1, "Right button - Down")
            self.key_list_widget.insertItem(index + 2, "Right button - Up")
            self.key_list_widget.setCurrentRow(index + 2)

    def middle_button_event(self):
        self.events_menu.setText("Middle button")
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            index = 0
            self.key_list_widget.insertItem(index + 1, "Middle button - Down")
            self.key_list_widget.insertItem(index + 2, "Middle button - Up")
            self.key_list_widget.setCurrentRow(index + 1)
        else:
            index = self.key_list_widget.row(current_item)
            self.key_list_widget.insertItem(index + 1, "Middle button - Down")
            self.key_list_widget.insertItem(index + 2, "Middle button - Up")
            self.key_list_widget.setCurrentRow(index + 2)

    def key_down_apply(self, text_and_value):
        full_text = f"Key {text_and_value[0]} - Down"
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            index = 0
            self.key_list_widget.insertItem(index + 1, full_text)
            self.key_list_widget.setCurrentRow(index)
        else:
            index = self.key_list_widget.row(current_item)
            self.key_list_widget.insertItem(index + 1, full_text)
            self.key_list_widget.setCurrentRow(index + 1)

    def key_up_apply(self, text_and_value):
        full_text = f"Key {text_and_value[0]} - Up"
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            index = 0
            self.key_list_widget.insertItem(index + 1, full_text)
            self.key_list_widget.setCurrentRow(index)
        else:
            index = self.key_list_widget.row(current_item)
            self.key_list_widget.insertItem(index + 1, full_text)
            self.key_list_widget.setCurrentRow(index + 1)

    def delay_apply(self, delay):
        full_text = f"Delay - {delay} ms"
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            index = 0
            self.key_list_widget.insertItem(index + 1, full_text)
            self.key_list_widget.setCurrentRow(index)
        else:
            index = self.key_list_widget.row(current_item)
            self.key_list_widget.insertItem(index + 1, full_text)
            self.key_list_widget.setCurrentRow(index + 1)

    def delay_event(self):
        self.events_menu.setText("Delay")
        self.delay_enter = EnterDelay(self, MacroCreator.MAX_DELAY)
        self.delay_enter.setWindowModality(QtCore.Qt.ApplicationModal)
        self.delay_enter.ok_pressed.connect(self.delay_apply)
        self.delay_enter.show()

    def key_up_event(self):
        self.events_menu.setText("Key up")
        self.key_catcher_up = KeyCatcher(self)
        self.key_catcher_up.setWindowModality(QtCore.Qt.ApplicationModal)
        self.key_catcher_up.ok_pressed.connect(self.key_up_apply)
        self.key_catcher_up.show()

    def key_down_event(self):
        self.events_menu.setText("Key down")
        self.key_catcher_down = KeyCatcher(self)
        self.key_catcher_down.setWindowModality(QtCore.Qt.ApplicationModal)
        self.key_catcher_down.ok_pressed.connect(self.key_down_apply)
        self.key_catcher_down.show()

    def modify_item(self):
        current_item = self.key_list_widget.currentItem()
        if current_item is None:
            return

        if current_item.text().endswith("Down"):
            self.key_catcher_down = KeyCatcher(self)
            self.key_catcher_down.setWindowModality(QtCore.Qt.ApplicationModal)
            self.key_catcher_down.ok_pressed.connect(self.modify_key_down)
            self.key_catcher_down.show()
        elif current_item.text().endswith("Up"):
            self.key_catcher_down = KeyCatcher(self)
            self.key_catcher_down.setWindowModality(QtCore.Qt.ApplicationModal)
            self.key_catcher_down.ok_pressed.connect(self.modify_key_up)
            self.key_catcher_down.show()
        elif current_item.text().endswith("ms"):
            self.delay_enter = EnterDelay(self, MacroCreator.MAX_DELAY)
            self.delay_enter.setWindowModality(QtCore.Qt.ApplicationModal)
            self.delay_enter.ok_pressed.connect(self.modify_delay)
            self.delay_enter.show()

    def modify_key_down(self, text_and_value):
        current_item = self.key_list_widget.currentItem()
        full_text = f"Key {text_and_value[0]} - Down"
        current_item.setText(full_text)

    def modify_key_up(self, text_and_value):
        current_item = self.key_list_widget.currentItem()
        full_text = f"Key {text_and_value[0]} - Up"
        current_item.setText(full_text)

    def modify_delay(self, delay):
        current_item = self.key_list_widget.currentItem()
        full_text = f"Delay - {delay} ms"
        current_item.setText(full_text)

    def delete_item(self):
        current_item = self.key_list_widget.currentItem()
        self.key_list_widget.takeItem(self.key_list_widget.row(current_item))

    def on_radio_button_checked(self):
        radio_button = self.sender()

        if radio_button == self.cycle_times:
            self.cycle_entry.setDisabled(False)
        else:
            self.cycle_entry.setDisabled(True)

    def change_selected_macro(self):
        current_item = self.macro_list_widget.currentItem()
        if current_item is None:
            self.key_list_widget.clear()
            return

        selected_macro_name = current_item.text()
        self.macro_name_line_edit.setText(selected_macro_name)

        with open(MACROS_DIR + selected_macro_name, "r") as file:
            macro_text = file.readline()

        # clear whole list
        self.key_list_widget.clear()

        # if macro is empty, end this function
        if macro_text == "":
            return

        macro_full = macro_text.split(":")
        macro_text_list = macro_full[1].split(",")
        begin_macro = macro_full[0].split(",")

        if begin_macro[0] == "1":
            self.cycle_times.setChecked(True)
        elif begin_macro[0] == "2":
            self.until_key_pressed.setChecked(True)
        elif begin_macro[0] == "4":
            self.until_key_released.setChecked(True)
        else:
            xenon_logger.warning("No such value for macro cycle option")

        for key in macro_text_list:
            self.key_list_widget.addItem(key)

        self.key_list_widget.setCurrentRow(self.key_list_widget.count() - 1)


class Advanced(custom_widgets.PopUpWindow):
    def __init__(self, parent, size_w, size_h, driver, data):
        super().__init__(parent, size_w, size_h)

        self.data = data
        self.driver = driver
        self.last_selected = "Main data"

        self.main_data_len = len(self.data.main_data)
        self.reset_data_len = len(self.data.reset_data)
        self.bindings_data_len = len(self.data.bindings_data)

        advanced_layout = QVBoxLayout(self.outer_frame)

        data_buttons_layouts = QHBoxLayout()
        main_data_button = custom_widgets.Button("Main data")
        reset_data_button = custom_widgets.Button("Reset data")
        bindings_data_button = custom_widgets.Button("Bindings data")

        data_buttons_layouts.addWidget(main_data_button)
        data_buttons_layouts.addWidget(reset_data_button)
        data_buttons_layouts.addWidget(bindings_data_button)

        bottom_buttons_layout = QHBoxLayout()
        apply_button = custom_widgets.Button("Apply data")
        close_button = custom_widgets.Button("Close")

        bottom_buttons_layout.addWidget(apply_button)
        bottom_buttons_layout.addWidget(close_button)

        self.main_data_string = self.data_to_string(self.data.main_data)
        self.reset_data_string = self.data_to_string(self.data.reset_data)
        self.bindings_data_string = self.data_to_string(self.data.bindings_data)

        self.te = QTextEdit()
        font = QtGui.QFont("monospace")
        self.te.setFont(font)
        self.te.setStyleSheet("background: white")
        self.te.setText(self.main_data_string)

        main_data_button.clicked.connect(self.set_current_data)
        reset_data_button.clicked.connect(self.set_current_data)
        bindings_data_button.clicked.connect(self.set_current_data)

        close_button.clicked.connect(self.close)
        apply_button.clicked.connect(self.apply_data)

        advanced_layout.addLayout(data_buttons_layouts)
        advanced_layout.addWidget(self.te)
        advanced_layout.addLayout(bottom_buttons_layout)

    def set_current_data(self):
        button = self.sender()
        if button.text() == "Main data":
            if self.last_selected == "Reset data":
                self.reset_data_string = self.te.toPlainText()
            elif self.last_selected == "Bindings data":
                self.bindings_data_string = self.te.toPlainText()

            self.last_selected = button.text()
            self.te.setText(self.main_data_string)
        elif button.text() == "Reset data":
            if self.last_selected == "Main data":
                self.main_data_string = self.te.toPlainText()
            elif self.last_selected == "Bindings data":
                self.bindings_data_string = self.te.toPlainText()

            self.last_selected = button.text()
            self.te.setText(self.reset_data_string)
        elif button.text() == "Bindings data":
            if self.last_selected == "Main data":
                self.main_data_string = self.te.toPlainText()
            elif self.last_selected == "Reset data":
                self.reset_data_string = self.te.toPlainText()

            self.last_selected = button.text()
            self.te.setText(self.bindings_data_string)
        else:
            raise Exception("Advanced: WHOOPS! Wrong data!")

    def apply_data(self):
        if self.last_selected == "Main data":
            self.main_data_string = self.te.toPlainText()
        elif self.last_selected == "Reset data":
            self.reset_data_string = self.te.toPlainText()
        elif self.last_selected == "Bindings data":
            self.bindings_data_string = self.te.toPlainText()

        main_check = self.string_to_data(self.main_data_string)
        reset_check = self.string_to_data(self.reset_data_string)
        bindings_check = self.string_to_data(self.bindings_data_string)

        if (
            len(main_check) != self.main_data_len or len(reset_check) != self.reset_data_len or len(bindings_check) != self.bindings_data_len
        ):
            custom_widgets.DataNotAllowed()
            return

        self.data.main_data = main_check
        self.data.reset_data = reset_check
        self.data.bindings_data = bindings_check

        if self.driver.send_data(self.data) is None:
            custom_widgets.DeviceNotConnectedMessage()
            return

    def data_to_string(self, data):
        data_string = ""
        for i, byte in enumerate(data):
            if i % 16 == 0 and i != 0:
                data_string += "\n"
            data_string += f"{byte:02x}"
            if i != len(data) - 1:
                data_string += " "
        return data_string

    def string_to_data(self, data_string):
        no_newline_string = data_string.replace("\n", "")
        splitted = no_newline_string.split(" ")
        try:
            for byte in splitted:
                if int(byte, 16) > 255 or int(byte, 16) < 0:
                    return []
            data = list(map(lambda x: int(x, 16), splitted))
        except ValueError:
            return []
        return data
