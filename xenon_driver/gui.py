import sys
import yaml
from functools import partial

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from xenon_driver.data import Data
from xenon_driver.data_handler import DataHandler, MacroTranslator
from xenon_driver.options import Options

from xenon_driver.configuration import DATA_DIR, PROFILES_DIR
from xenon_driver.gui_resources import custom_widgets
from xenon_driver.gui_resources import gui_parts
from xenon_driver.gui_resources import gui_keys
from xenon_driver.logger import xenon_logger


class Window(QtWidgets.QWidget):
    App = QtWidgets.QApplication(sys.argv)

    def __init__(self, driver, dry_run=False, load_default=False, parent=None):
        super().__init__(parent)

        default_file_name = self.read_default()

        if load_default:
            self.data = Data(DATA_DIR + "default_settings.yml")
        else:
            self.data = Data(PROFILES_DIR + default_file_name + ".yml")

        self.current_profile = self.data.file_name

        self.data_handler = DataHandler(self.data)

        self.dry_run = dry_run

        # variables
        self.driver = driver

        self.current_set_rr = self.data.settings_yml["main_data"]["rr"]
        self.current_set_dpis = self.data.settings_yml["main_data"]["dpis"]
        self.current_led_mode = self.data.settings_yml["main_data"]["chosen"]
        self.current_steady_color = self.data.settings_yml["main_data"]["steady"]["color"]
        self.current_breath_color = self.data.settings_yml["main_data"]["breath"]["color"]
        self.current_steady_option = self.data.settings_yml["main_data"]["steady"]["option"]
        self.current_breath_option = self.data.settings_yml["main_data"]["breath"]["option"]
        self.current_neon_option = self.data.settings_yml["main_data"]["neon"]["option"]

        # pop up windows
        self.advanced = None
        self.profiles_manager = None
        self.macro_creator = None

        # macro translator
        self.mt = None

        # -------------------
        self.setStyleSheet("background-color: #444444;")

        self.setFixedSize(680, 580)
        self.setWindowTitle("Driver")

        self.outer_frame_layout = QtWidgets.QVBoxLayout(self)

        # ----- frames ------
        self.outer_frame = custom_widgets.Frame(parent=self, color="gray", style=QtWidgets.QFrame.StyledPanel | QtWidgets.QFrame.Sunken)

        self.top_buttons_frame = custom_widgets.Frame(parent=self, color="gray", style=QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken, height=50)

        self.bindings_frame = custom_widgets.Frame(self, "gray", QtWidgets.QFrame.Box | QtWidgets.QFrame.Sunken)

        self.right_frame = custom_widgets.Frame(self, "gray", QtWidgets.QFrame.Box | QtWidgets.QFrame.Sunken)
        # -------------------

        # button names lists
        self.top_buttons_names = ["Create macro", "Profiles", "Advanced"]

        self.dpis_list = [
            ("500" , Options.SNIPE_DPI500 ),
            ("750" , Options.SNIPE_DPI750 ),
            ("1000", Options.SNIPE_DPI1000),
            ("1250", Options.SNIPE_DPI1250),
            ("1375", Options.SNIPE_DPI1375),
            ("1500", Options.SNIPE_DPI1500),
            ("1750", Options.SNIPE_DPI1750),
            ("2000", Options.SNIPE_DPI2000),
            ("2500", Options.SNIPE_DPI2500),
            ("2750", Options.SNIPE_DPI2750),
            ("3200", Options.SNIPE_DPI3200)
        ]

        # ---- bind buttons ----
        self.bindings_options = [
            "Left button", "Right button", "Middle button",
            "Forward button", "Back button",
            "DPI Loop", "DPI +", "DPI -",
            "Three click", "Multimedia", "Fire key", "Keys combination",
            "Macro", "Mode switch", "Snipe button", "Disable"
        ]

        self.bindings_buttons_names = ["left_button", "right_button", "middle_button", "forward_button", "back_button", "dpi_button", "mode_button", "fire_button"]

        self.bindings_functions = [
            self.data_handler.set_left_button,
            self.data_handler.set_right_button,
            self.data_handler.set_middle_button,
            self.data_handler.set_forward_button,
            self.data_handler.set_back_button,
            self.data_handler.set_dpi_button,
            self.data_handler.set_mode_button,
            self.data_handler.set_fire_button
        ]

        # report rate
        self.rr_buttons_names = [
            ("250",  Options.REPORT_RATE_250MHZ),
            ("500",  Options.REPORT_RATE_500MHZ),
            ("1000", Options.REPORT_RATE_1000MHZ)
        ]
        # led
        self.led_mode_data = {
            "Steady": [
                Options.STEADY,
                "Brightness",
                ["10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%"],
                [0x11, 0x21, 0x31, 0x41, 0x51, 0x61, 0x71, 0x81, 0x91, 0xa1],
                True, True,
                self.current_steady_color,
                self.current_steady_option
            ],
            "Breath": [
                Options.BREATH,
                "Speed",
                ["1s", "4s", "6s", "8s"],
                [0x01, 0x11 ,0x51, 0xa1],
                True, True,
                self.current_breath_color,
                self.current_breath_option
            ],
            "Neon": [
                Options.NEON,
                "Speed",
                ["2s", "4s", "6s"],
                [0x11, 0x51 ,0xa1],
                True, False,
                [0,0,0],
                self.current_neon_option
            ],
            "Off" : [
                Options.OFF,
                "",
                [],
                [],
                False, False,
                [0,0,0],
                0x00
            ]
        }

        # multimedia dict
        self.multimedia_keys_dict = {
            "Media Player" : Options.MEDIAPLAYER,
            "Play/Pause"   : Options.PLAYPAUSE,
            "Next"         : Options.NEXT,
            "Previous"     : Options.PREVIOUS,
            "Stop"         : Options.STOP,
            "Mute"         : Options.MUTE,
            "Volume Up"    : Options.VOLUMEUP,
            "Volume Down"  : Options.VOLUMEDOWN,
            "Calculator"   : Options.CALCULATOR,
            "Home page"    : Options.HOMEPAGE
        }

        restore_func = partial(self.load_profile, "default_settings.yml", True)
        self.bottom_buttons_list = [
            ("Restore default", restore_func),
            ("Apply", self.apply_changes),
            ("Exit", self.kill_em_all)
        ]

        # ---- top buttons ----
        self.top_buttons_list = [
            ("Create macro", self.on_create_macro_clicked),
            ("Profiles", self.on_profile_button_clicked),
            ("Advanced", self.on_advanced_clicked)
        ]

        # top buttons
        self.top_buttons_widget = gui_parts.TopButtons(self.top_buttons_frame, self.top_buttons_list)

        # bindings buttons and modes
        self.bindings_buttons_widget = gui_parts.BindingsButtons(
            self,
            self.bindings_frame,
            self.bindings_buttons_names,
            self.bindings_options,
            self.data
        )

        # report rate buttons
        self.rr_widget = gui_parts.ReportRateButtons(self.rr_buttons_names, self.current_set_rr)

        # led_changer
        self.led_changer = gui_parts.LedChanger(self.led_mode_data, self.current_led_mode)

        # dpi sliders
        self.dpi_sliders_widget = gui_parts.DpiSliders(self.current_set_dpis, self.dpis_list)

        # bottom buttons
        self.bottom_buttons_widget = gui_parts.BottomButtons(self.bottom_buttons_list, self.current_profile)

        # ---- setting frames ----

        self.outer_frame_layout.addWidget(self.outer_frame)

        # right side
        self.right_frame_layout = QtWidgets.QVBoxLayout(self.right_frame)
        self.right_frame_layout.addWidget(self.rr_widget)
        self.right_frame_layout.addWidget(self.led_changer)

        self.main_layout = QtWidgets.QVBoxLayout(self.outer_frame)
        self.main_layout.addWidget(self.top_buttons_frame)

        self.settings_h_layout = QtWidgets.QHBoxLayout()
        self.settings_h_layout.addWidget(self.bindings_frame)
        self.settings_h_layout.addWidget(self.right_frame)

        self.main_layout.addLayout(self.settings_h_layout)
        self.main_layout.addWidget(self.bottom_buttons_widget)

        self.right_frame_layout.addWidget(self.dpi_sliders_widget)

        self.right_frame_layout.addStretch()

        self.assign_data_bytes()
        self.center()

    def center(self):
        qt = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qt.moveCenter(cp)
        self.move(qt.topLeft())

    def assign_data_bytes(self):
        if self.current_profile == "":
            custom_widgets.SaveProfileMessage()
            return

        # led
        for rb, widgets in self.led_changer.mode_widgets.items():
            if rb.isChecked():
                combo_box = widgets[0]
                color_button = widgets[1]
                chosen_color = color_button.get_button_color()
                chosen_option = combo_box.currentData()
                if combo_box.currentData() is None:
                    chosen_option = 0x00
                self.data_handler.set_led(rb.mode, chosen_option, chosen_color[0], chosen_color[1], chosen_color[2])

        # bindings
        for i, bind_menu in enumerate(self.bindings_buttons_widget.bindings_menus):
            self.current_set_mode = self.bindings_buttons_widget.current_set_mode
            bind_text = bind_menu.text()
            if bind_text.startswith("Left button"):
                setter = partial(self.bindings_functions[i], Options.CLICK_MASK, Options.LEFT_BUTTON, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Right button"):
                setter = partial(self.bindings_functions[i], Options.CLICK_MASK, Options.RIGHT_BUTTON, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Middle button"):
                setter = partial(self.bindings_functions[i], Options.CLICK_MASK, Options.MIDDLE_BUTTON, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Forward button"):
                setter = partial(self.bindings_functions[i], Options.CLICK_MASK, Options.FORWARD_BUTTON, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Back button"):
                setter = partial(self.bindings_functions[i], Options.CLICK_MASK, Options.BACK_BUTTON, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("DPI Loop"):
                setter = partial(self.bindings_functions[i], Options.DPI_LOOP_MASK, Options.DPI_LOOP, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("DPI +"):
                setter = partial(self.bindings_functions[i], Options.DPI_LOOP_MASK, Options.DPI_PLUS, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("DPI -"):
                setter = partial(self.bindings_functions[i], Options.DPI_LOOP_MASK, Options.DPI_MINUS, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Three click"):
                setter = partial(self.bindings_functions[i], Options.THREE_CLICK_MASK, Options.THREE_CLICK_ACTION, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Keys combination"):
                key_comb_splited = bind_text.split(" ")
                key_comb_text = key_comb_splited[3]
                keys_list = key_comb_text.split("+")
                xenon_logger.debug(keys_list)

                whole_key_combination_data = [Options.KEY_COMBINATION_MASK, 0x00]
                for key_catched in keys_list:
                    for _, tuple_val in gui_keys.GuiKeys.keys_dict.items():
                        if key_catched in ("Ctrl", "Shift", "Alt", "Super") and key_catched == tuple_val[0]:
                            whole_key_combination_data[1] |= tuple_val[1]
                        elif key_catched == tuple_val[0]:
                            whole_key_combination_data.append(tuple_val[1])

                setter = partial(self.bindings_functions[i], *whole_key_combination_data, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Multimedia"):
                bind_text_splitted = bind_text.split(" ")
                multimedia_name = bind_text_splitted[2]
                multimedia_value = self.multimedia_keys_dict[multimedia_name]
                setter = partial(self.bindings_functions[i], Options.KEY_COMBINATION_MASK, 0x00, multimedia_value, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Fire key"):
                bind_text_splitted = bind_text.split("-")
                fire_data = bind_text_splitted[1][1:]
                splitted_fire_data = fire_data.split(",")

                whole_fire_key = [Options.FIRE_MASK, 0, 0, 0]

                if splitted_fire_data[0] in gui_keys.GuiKeys.MOUSE_KEYS:
                    whole_fire_key[1] = gui_keys.GuiKeys.MOUSE_KEYS[splitted_fire_data[0]]

                for _, tuple_val in gui_keys.GuiKeys.keys_dict.items():
                    if splitted_fire_data[0] == tuple_val[0]:
                        whole_fire_key[1] = tuple_val[1]

                whole_fire_key[2] = int(splitted_fire_data[1][:-2])
                whole_fire_key[3] = int(splitted_fire_data[2])

                setter = partial(self.bindings_functions[i], *whole_fire_key, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Mode switch"):
                setter = partial(self.bindings_functions[i], Options.MODE_MASK, Options.MODE_ACTION, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Snipe button"):
                snipe_dpi_text = bind_text.split(" ")
                current_dpi_text = snipe_dpi_text[3]
                actual_dpi_byte = 0
                for dpi_value in self.dpis_list:
                    if dpi_value[0] == current_dpi_text:
                        actual_dpi_byte = dpi_value[1]
                setter = partial(self.bindings_functions[i], Options.SNIPE_BUTTON_MASK, actual_dpi_byte, mode=self.current_set_mode)
                setter()
            elif bind_text.startswith("Macro"):
                bind_text_splitted = bind_text.split(" ")
                macro_file_name = bind_text_splitted[2]
                self.mt = MacroTranslator(macro_file_name)

                # macro doesn't exist anymore
                if not self.mt.macro_bytes:
                    custom_widgets.MacroNotFound()
                    return

                setter = partial(self.bindings_functions[i], Options.MACRO_MASK, 0x00, mode=self.current_set_mode, macro=self.mt)
                setter()
            elif bind_text.startswith("Disable"):
                setter = partial(self.bindings_functions[i], Options.DISABLE_MASK, Options.DISABLE_ACTION, mode=self.current_set_mode)
                setter()

        # rr
        self.data_handler.set_report_rate(self.rr_widget.current_set_rr)

        # mode
        self.data_handler.set_current_mode(self.current_set_mode)

        # apply dpis
        for i, dpi_slider in enumerate(self.dpi_sliders_widget.dpi_sliders_list):
            if self.dpi_sliders_widget.dpi_check_boxes_list[i].isChecked():
                self.data_handler.set_dpi_values(i + 1, dpi_slider.value())
            else:
                self.data_handler.set_dpi_values(i + 1, dpi_slider.value() | Options.BLOCKED_DPI_LEVEL_MASK)

        dpi_levels = sum([dcb.isChecked() for dcb in self.dpi_sliders_widget.dpi_check_boxes_list])
        self.data_handler.set_dpi_levels(dpi_levels)

    def apply_changes(self):
        self.assign_data_bytes()

        if self.dry_run:
            return

        if self.driver is None:
            custom_widgets.DeviceNotConnectedMessage()
            xenon_logger.error("Device not connected")
            return

        # send and save
        send_result = self.driver.send_data(self.data)
        if send_result is None:
            custom_widgets.DeviceNotConnectedMessage()
            xenon_logger.error("Device not connected")
            return

        # save current profile as default
        self.save_default(self.current_profile)

        self.save_data(self.current_profile)

    def save_data(self, file_name):
        self.current_profile = file_name

        # led
        for rb, widgets in self.led_changer.mode_widgets.items():
            combo_box = widgets[0]
            color_button = widgets[1]
            mode_label_text = widgets[2].text()

            if rb.isChecked():
                self.data.settings_yml["main_data"]["chosen"] = mode_label_text

            self.data.settings_yml["main_data"][mode_label_text.lower()]["color"] = color_button.get_button_color()
            self.data.settings_yml["main_data"][mode_label_text.lower()]["option"] = combo_box.currentData()

        # bindings
        for i, binding_menu in enumerate(self.bindings_buttons_widget.bindings_menus):
            self.data.settings_yml["bindings_data"]["mode" + str(self.bindings_buttons_widget.current_set_mode)][self.bindings_buttons_names[i]]["name"] = binding_menu.text()

        # rr
        self.data.settings_yml["main_data"]["rr"] = int(self.rr_widget.current_set_rr)

        # dpis
        for i, dpi_slider in enumerate(self.dpi_sliders_widget.dpi_sliders_list):
            if self.dpi_sliders_widget.dpi_check_boxes_list[i].isChecked():
                self.data.settings_yml["main_data"]["dpis"][i] = dpi_slider.value()
            else:
                self.data.settings_yml["main_data"]["dpis"][i] = dpi_slider.value() | Options.BLOCKED_DPI_LEVEL_MASK

        # set currrent profile label
        self.bottom_buttons_widget.set_profile_label_text(self.current_profile)

        with open(PROFILES_DIR + file_name + ".yml", "w") as f:
            yaml.dump(self.data.settings_yml, f)

        xenon_logger.info("Data saved")

    def on_profile_button_clicked(self):
        self.profiles_manager = gui_parts.ProfilesManager(self, PROFILES_DIR, self.current_profile)
        self.profiles_manager.setWindowModality(Qt.ApplicationModal)
        self.profiles_manager.load_pressed.connect(self.load_profile)
        self.profiles_manager.save_pressed.connect(self.save_data)
        self.profiles_manager.show()

    def on_create_macro_clicked(self):
        self.macro_creator = gui_parts.MacroCreator(self, 600, 400)
        self.macro_creator.setWindowModality(Qt.ApplicationModal)
        self.macro_creator.show()

    def on_advanced_clicked(self):
        self.advanced = gui_parts.Advanced(self, 450, 400, self.driver, self.data)
        self.advanced.setWindowModality(Qt.ApplicationModal)
        self.advanced.show()

    def kill_em_all(self):
        if self.profiles_manager is not None:
            self.profiles_manager.close()
        if self.advanced is not None:
            self.advanced.close()
        if self.macro_creator is not None:
            self.macro_creator.close()
        if self.bindings_buttons_widget.key_catcher is not None:
            self.bindings_buttons_widget.key_catcher.close()
        if self.bindings_buttons_widget.fire_key_menu is not None:
            self.bindings_buttons_widget.fire_key_menu.close()
        if self.bindings_buttons_widget.snipe_dpi_selector is not None:
            self.bindings_buttons_widget.snipe_dpi_selector.close()
        if self.bindings_buttons_widget.multimedia_selector is not None:
            self.bindings_buttons_widget.multimedia_selector.close()

        self.close()

    def save_default(self, file_name):
        with open(DATA_DIR + ".default", "w") as f:
            f.write(file_name)

        xenon_logger.info(f"saving as {file_name} default")

    def read_default(self):
        current_default = ""
        try:
            with open(DATA_DIR + ".default", "r") as f:
                current_default = f.readline().rstrip()
                xenon_logger.info(f"default file is: {current_default}")
        except FileNotFoundError:
            with open(DATA_DIR + ".default", "w") as f:
                current_default = "profile1"
                f.write(current_default)

        return current_default

    def load_profile(self, file_name, default=False):
        if default:
            path = DATA_DIR + file_name
        else:
            path = PROFILES_DIR + file_name + ".yml"

        xenon_logger.info(f"loading {file_name}")
        self.data.settings_yml = self.data.load_data(path)
        xenon_logger.warning(self.data.settings_yml)

        bindings_data = self.data.settings_yml["bindings_data"]

        # load led settings
        main_data = self.data.settings_yml["main_data"]

        chosen_led_mode = main_data["chosen"]
        steady_option = main_data["steady"]["option"]
        breath_option = main_data["breath"]["option"]
        neon_option = main_data["neon"]["option"]
        off_option = main_data["off"]["option"]

        steady_color = main_data["steady"]["color"]
        breath_color = main_data["breath"]["color"]
        neon_color = main_data["neon"]["color"]
        off_color = main_data["off"]["color"]

        options_list = [steady_option, breath_option, neon_option, off_option]
        colors_list = [steady_color, breath_color, neon_color, off_color]

        self.led_changer.set_mode(chosen_led_mode)
        self.led_changer.set_options(options_list)
        self.led_changer.set_color(colors_list)

        # current mode
        # start_mode = "mode1"
        current_set_mode = "mode" + str(self.bindings_buttons_widget.current_set_mode)

        for i, name in enumerate(self.bindings_buttons_names):
            self.bindings_buttons_widget.bindings_menus[i].set_text(bindings_data[current_set_mode][name]["name"])

        # load report rate
        rr = main_data["rr"]
        self.rr_widget.set_report_rate(rr)

        # load dpis
        starting_values = main_data["dpis"]

        self.dpi_sliders_widget.set_sliders_values(starting_values)

        # dont change label if loaded settings are default
        if not default:
            self.current_profile = file_name

        # set currrent profile label
        self.bottom_buttons_widget.set_profile_label_text(self.current_profile)

        self.assign_data_bytes()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F11:
            self.apply_changes()
        elif event.key() == Qt.Key_Q:
            self.kill_em_all()
        elif event.key() == Qt.Key_F10:
            self.load_profile("default_settings.yml")
