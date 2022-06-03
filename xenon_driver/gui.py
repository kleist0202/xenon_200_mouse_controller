import sys
import yaml
from functools import partial
import logging
from logging.config import dictConfig

from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets

from xenon_driver.data import Data
from xenon_driver.data_handler import DataHandler, MacroTranslator
from xenon_driver.options import Options

from xenon_driver.configuration import DATA_DIR, PROFILES_DIR
from xenon_driver.gui_resources import custom_widgets 
from xenon_driver.gui_resources import gui_parts
from xenon_driver.gui_resources import gui_keys


dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s', 
            'datefmt': '%Y-%m-%d %H:%M:%S',
        }
    },
   'handlers' : {
        'default': {
            'level': 'DEBUG', 
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        }
   }, 
   'loggers': {
        '__main__': { 
            'handlers' : ['default'], 
            'level': 'DEBUG', 
            'propagate': False,
        },
   },
   'root': {
        'level': 'DEBUG',
        'handlers': ['default']
   },
})

logger = logging.getLogger(__name__)


class Window(QtWidgets.QWidget):
    App = QtWidgets.QApplication(sys.argv)

    def __init__(self, driver, dry_run=False, load_default=False, parent=None):
        super().__init__(parent)

        default_file_name = self.read_default()

        if load_default:
            self.data = Data(DATA_DIR+"default_settings.yml")
        else:
            self.data = Data(PROFILES_DIR+default_file_name+".yml")

        self.current_profile = self.data.file_name

        self.data_handler = DataHandler(self.data)

        self.dry_run = dry_run

        # variables
        self.driver = driver

        self.current_set_mode = 1
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
        self.key_catcher = None
        self.snipe_dpi_selector = None
        self.fire_key_menu = None
        self.multimedia_selector = None
        self.mt = None

        # -------------------
        self.setStyleSheet("background-color: #444444;")

        self.setFixedSize(680, 560)
        self.setWindowTitle("Driver")

        self.outer_frame_layout = QtWidgets.QVBoxLayout(self)

        # ----- frames ------
        self.outer_frame = custom_widgets.Frame(parent=self, color="gray", style=QtWidgets.QFrame.StyledPanel|QtWidgets.QFrame.Sunken)

        self.buttons_frame = custom_widgets.Frame(parent=self, color="gray", style=QtWidgets.QFrame.Panel | QtWidgets.QFrame.Sunken, height=50)

        self.bindings_frame = custom_widgets.Frame(self, "gray", QtWidgets.QFrame.Box | QtWidgets.QFrame.Sunken)

        self.right_frame = custom_widgets.Frame(self, "gray", QtWidgets.QFrame.Box | QtWidgets.QFrame.Sunken)
        # -------------------

        self.outer_frame_layout.addWidget(self.outer_frame)

        # button names lists
        self.top_buttons_names = ["Create macro", "Profiles", "Advanced"]
        self.bindings_buttons_names = ["left_button", "right_button", "middle_button", "forward_button", "back_button", "dpi_button", "mode_button", "fire_button"]

        # self.snipe_dpis_dict = { 
        #         1  : ["500", Options.SNIPE_DPI500],
        #         2  : ["750", Options.SNIPE_DPI750],
        #         3  : ["1000", Options.SNIPE_DPI1000],
        #         4  : ["1250", Options.SNIPE_DPI1250],
        #         5  : ["1375", Options.SNIPE_DPI1375],
        #         6  : ["1500", Options.SNIPE_DPI1500],
        #         7  : ["1750", Options.SNIPE_DPI1750],
        #         8  : ["2000", Options.SNIPE_DPI2000],
        #         9  : ["2500", Options.SNIPE_DPI2500],
        #         10 : ["2750", Options.SNIPE_DPI2750],
        #         11 : ["3200", Options.SNIPE_DPI3200]
        # }
        self.snipe_dpis_dict = [ 
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

        # ---- modes radio buttons ----
        self.modes_layout = self.create_modes_buttons()

        # ---- top buttons ----
        self.top_buttons_h_layout = self.create_top_buttons(self.buttons_frame, self.top_buttons_names)
    
        # ---- bind buttons ----
        self.bindings_options = ["Left button", "Right button", "Middle button", "Forward button", "Back button", "DPI Loop", "DPI +", "DPI -", "Three click", "Multimedia", "Fire key", "Keys combination", "Macro", "Mode switch", "Snipe button", "Disable"]

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
        # self.cb_bindings_list = []
        self.bindings_menus = []
        self.bindings_list_layout = self.create_bindings_buttons()

        # add bind layouts
        self.bindings_v_layout = QtWidgets.QVBoxLayout(self.bindings_frame)
        self.bindings_v_layout.addLayout(self.modes_layout)
        self.bindings_v_layout.addLayout(self.bindings_list_layout)

        # ---- right side ----
        self.right_frame_layout = QtWidgets.QVBoxLayout(self.right_frame)

        self.rr_buttons_names = [
                ("250",  Options.REPORT_RATE_250MHZ),
                ("500",  Options.REPORT_RATE_500MHZ),
                ("1000", Options.REPORT_RATE_1000MHZ)
        ]

        self.rr_widget = gui_parts.ReportRateButtons(self.rr_buttons_names, self.current_set_rr)

        # led
        self.led_mode_data = {
            "Steady": [
                Options.STEADY,
                "Brightness",
                [ "10%", "20%", "30%", "40%", "50%", "60%", "70%", "80%", "90%", "100%" ],
                [ 0x11, 0x21, 0x31, 0x41, 0x51, 0x61, 0x71, 0x81, 0x91, 0xa1 ],
                True, True,
                self.current_steady_color,
                self.current_steady_option
            ],
            "Breath": [
                Options.BREATH,
                "Speed",
                [ "1s", "4s", "6s", "8s" ],
                [ 0x01, 0x11 ,0x51, 0xa1 ],
                True, True,
                self.current_breath_color,
                self.current_breath_option
            ],
            "Neon": [
                Options.NEON,
                "Speed",
                [ "2s", "4s", "6s" ],
                [ 0x11, 0x51 ,0xa1 ],
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

        self.multimedia_keys_dict = {
            "Media Player" : Options.MEDIAPLAYER,
            "Play/Pause"   : Options.PLAYPAUSE,
            "Next"         : Options.NEXT,
            "Previous"     : Options.PREVIOUS,
            "Stop"         : Options.STOP,
            "Mute"         : Options.MUTE,
            "Volume Up"    : Options.VOLUMEUP,
            "Volume Down"  : Options.VOLUMEDOWN,
            # "Email"        : Options.EMAIL,
            "Calculator"   : Options.CALCULATOR,
            # "Explorer"     : Options.EXPLORER,
            "Home page"    : Options.HOMEPAGE
        }

        self.led_changer = gui_parts.LedChanger(self.led_mode_data, self.current_led_mode)

        # self.right_frame_layout.addLayout(self.rr_layout)
        self.right_frame_layout.addWidget(self.rr_widget)

        self.right_frame_layout.addWidget(self.led_changer)

        # ----  bottom buttons ----
        self.bottom_buttons_layout = self.create_bottom_buttons()

        # ---- setting frames ----
        self.main_layout = QtWidgets.QVBoxLayout(self.outer_frame)
        self.main_layout.addWidget(self.buttons_frame)

        self.settings_h_layout = QtWidgets.QHBoxLayout()
        self.settings_h_layout.addWidget(self.bindings_frame)
        self.settings_h_layout.addWidget(self.right_frame)

        self.main_layout.addLayout(self.settings_h_layout)
        self.main_layout.addLayout(self.bottom_buttons_layout)

        self.dpi_values = ["500", "750", "1000", "1250", "1375", "1500", "1750", "2000", "2500", "2750", "3200"]

        self.dpi_sliders_widget = gui_parts.DpiSliders(self.current_set_dpis, self.dpi_values)

        self.right_frame_layout.addWidget(self.dpi_sliders_widget)

        self.right_frame_layout.addStretch()

        self.center()

    def center(self):
        qt = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qt.moveCenter(cp)
        self.move(qt.topLeft())

    def create_top_buttons(self, frame, names_list):
        buttons_h_layout = QtWidgets.QHBoxLayout(frame)

        for name in names_list:
            btn = QtWidgets.QPushButton(name)
            buttons_h_layout.addWidget(btn)
            if name == "Profiles":
                btn.clicked.connect(self.on_profile_button_clicked)
            elif name == "Create macro":
                btn.clicked.connect(self.on_create_macro_clicked)
            elif name == "Advanced":
                btn.clicked.connect(self.on_advanced_clicked)

        return buttons_h_layout

    def create_bindings_buttons(self):
        bindings_list_layout = QtWidgets.QGridLayout()

        bindings_options = [
                ("Left button", self.on_special_combo_box_item),
                ("Right button", self.on_special_combo_box_item),
                ("Middle button", self.on_special_combo_box_item),
                ("Forward button", self.on_special_combo_box_item),
                ("Back button", self.on_special_combo_box_item),
                ("DPI Loop", self.on_special_combo_box_item),
                ("DPI +", self.on_special_combo_box_item),
                ("DPI -", self.on_special_combo_box_item),
                ("Three click", self.on_special_combo_box_item),
                ("Multimedia", self.on_special_combo_box_item),
                ("Fire key", self.on_special_combo_box_item),
                ("Keys combination", self.on_special_combo_box_item),
                ("Macro", self.on_special_combo_box_item), 
                ("Mode switch", self.on_special_combo_box_item), 
                ("Snipe button", self.on_special_combo_box_item),
                ("Disable", self.on_special_combo_box_item)
        ]

        for i, name in enumerate(self.bindings_buttons_names):
            start_mode = "mode1"
            buttons_menu = custom_widgets.ButtonMenu(self.data.settings_yml["bindings_data"][start_mode][name]["name"])
            for opt in bindings_options:
                buttons_menu.add_option(opt, i, opt[0])

            label = custom_widgets.Label(str(i+1)+".", width=10)
            bindings_list_layout.addWidget(label, i, 0)
            bindings_list_layout.addWidget(buttons_menu, i, 1)
            self.bindings_menus.append(buttons_menu)

        hspacer = QtWidgets.QSpacerItem(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        bindings_list_layout.addItem(hspacer, 10, 1)

        return bindings_list_layout

    def create_bottom_buttons(self):
        bottom_buttons_layout = QtWidgets.QHBoxLayout()

        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.clicked.connect(self.apply_changes)

        exit_button = QtWidgets.QPushButton("Exit")
        exit_button.clicked.connect(self.kill_em_all)

        restore_button = QtWidgets.QPushButton("Restore default")
        restore_func = partial(self.load_profile, "default_settings.yml", True)
        restore_button.clicked.connect(restore_func)

        self.profile_label = QtWidgets.QLabel("Profile: " + self.current_profile)
        bottom_buttons_layout.addWidget(self.profile_label)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        bottom_buttons_layout.addItem(spacerItem)
        bottom_buttons_layout.addWidget(restore_button, alignment=Qt.AlignBottom)
        bottom_buttons_layout.addWidget(apply_button, alignment=Qt.AlignBottom)
        bottom_buttons_layout.addWidget(exit_button, alignment=Qt.AlignBottom)

        return bottom_buttons_layout

    def create_modes_buttons(self):
        modes_layout = QtWidgets.QHBoxLayout()

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

        modes_layout.addWidget(mode1, )
        modes_layout.addWidget(mode2, alignment=Qt.AlignCenter)
        modes_layout.addWidget(mode3, alignment=Qt.AlignRight)

        return modes_layout

    def on_mode_changed(self):
        radio_button = self.sender()
        current_mode = radio_button.mode
        self.current_set_mode = current_mode
        mode = f"mode{current_mode}"
        for i, name in enumerate(self.bindings_buttons_names):
            self.bindings_menus[i].set_text(self.data.settings_yml["bindings_data"][mode][name]["name"])

    def apply_changes(self):
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
        for i, bind_menu in enumerate(self.bindings_menus):
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
                logger.debug(keys_list)

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
                for dpi_value in self.snipe_dpis_dict:
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
                self.data_handler.set_dpi_values(i+1, dpi_slider.value())
            else:
                self.data_handler.set_dpi_values(i+1, dpi_slider.value() | Options.BLOCKED_DPI_LEVEL_MASK)

        dpi_levels = sum([dcb.isChecked() for dcb in self.dpi_sliders_widget.dpi_check_boxes_list])
        self.data_handler.set_dpi_levels(dpi_levels)

        if self.dry_run:
            return

        if self.driver is None:
            custom_widgets.DeviceNotConnectedMessage()
            logging.error("Device not connected")
            return

        # send and save
        send_result = self.driver.send_data(self.data)
        if send_result is None:
            custom_widgets.DeviceNotConnectedMessage()
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
        for i, binding_menu in enumerate(self.bindings_menus):
            self.data.settings_yml["bindings_data"]["mode"+str(self.current_set_mode)][self.bindings_buttons_names[i]]["name"] = binding_menu.text() 

        # rr
        self.data.settings_yml["main_data"]["rr"] = int(self.rr_widget.current_set_rr)

        # dpis
        for i, dpi_slider in enumerate(self.dpi_sliders_widget.dpi_sliders_list):
            if self.dpi_sliders_widget.dpi_check_boxes_list[i].isChecked():
                self.data.settings_yml["main_data"]["dpis"][i] = dpi_slider.value()
            else:
                self.data.settings_yml["main_data"]["dpis"][i] = dpi_slider.value() | Options.BLOCKED_DPI_LEVEL_MASK

        # set currrent profile label
        self.profile_label.setText("Profile: " + self.current_profile)

        with open(PROFILES_DIR+file_name+".yml", "w") as f:
            yaml.dump(self.data.settings_yml, f)

        logging.info("Data saved")

    def on_special_combo_box_item(self, i, text):
        self.bindings_menus[i].set_text(text)
        last_selected =self.bindings_menus[i].lastSelected

        if text == "Keys combination":
            self.key_catcher = gui_parts.KeyCombinationCatcher(self, i, last_selected)
            self.key_catcher.setWindowModality(Qt.ApplicationModal)
            self.key_catcher.ok_pressed.connect(self.on_keys_applied)
            self.key_catcher.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.key_catcher.show()
        elif text == "Snipe button":
            self.snipe_dpi_selector = gui_parts.SnipeDpiSelector(self, self.snipe_dpis_dict, 0, i, last_selected) 
            self.snipe_dpi_selector.setWindowModality(Qt.ApplicationModal)
            self.snipe_dpi_selector.ok_pressed.connect(self.on_snipe_dpi_applied)
            self.snipe_dpi_selector.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.snipe_dpi_selector.show()
        elif text == "Fire key":
            self.fire_key_menu = gui_parts.FireKeyMenu(self, i, last_selected) 
            self.fire_key_menu.setWindowModality(Qt.ApplicationModal)
            self.fire_key_menu.ok_pressed.connect(self.on_fire_key_applied)
            self.fire_key_menu.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.fire_key_menu.show()
        elif text == "Multimedia":
            self.multimedia_selector = gui_parts.MultimediaKeysSelector(self, 200, 300, self.multimedia_keys_dict, i, last_selected) 
            self.multimedia_selector.setWindowModality(Qt.ApplicationModal)
            self.multimedia_selector.ok_pressed.connect(self.on_multimedia_ok_button_pressed)
            self.multimedia_selector.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.multimedia_selector.show()
        elif text == "Macro":
            self.multimedia_selector = gui_parts.MacroSelector(self, 200, 300, i, last_selected) 
            self.multimedia_selector.setWindowModality(Qt.ApplicationModal)
            self.multimedia_selector.ok_pressed.connect(self.on_macro_button_pressed)
            self.multimedia_selector.cancel_pressed.connect(self.on_cancel_button_pressed)
            self.multimedia_selector.show()

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

    def on_keys_applied(self, keys_catched):
        key_catcher = self.sender()
        self.bindings_menus[key_catcher.key_num].set_text(f"Keys combination - {keys_catched}")

    def on_multimedia_ok_button_pressed(self, multimedia_name):
        multimedia_selector = self.sender()
        self.bindings_menus[multimedia_selector.key_num].set_text(f"Multimedia - {multimedia_name}")

    def on_cancel_button_pressed(self):
        some_pop_up_window = self.sender()
        self.bindings_menus[some_pop_up_window.key_num].set_text(some_pop_up_window.previous)

    def on_snipe_dpi_applied(self, dpi_value):
        snipe_button = self.sender()
        self.bindings_menus[snipe_button.key_num].set_text(f"Snipe button - {dpi_value}")

    def on_macro_button_pressed(self, file_name):
        some_pop_up_window = self.sender()
        self.bindings_menus[some_pop_up_window.key_num].set_text(f"Macro - {file_name}")

    def on_fire_key_applied(self, key, delay, times):
        fire_key_button = self.sender()
        self.bindings_menus[fire_key_button.key_num].set_text(f"Fire key - {key},{delay}ms,{times}")

    def kill_em_all(self):
        if self.key_catcher is not None:
            self.key_catcher.close()
        if self.profiles_manager is not None:
            self.profiles_manager.close()
        if self.advanced is not None:
            self.advanced.close()
        if self.fire_key_menu is not None:
            self.fire_key_menu.close()
        if self.snipe_dpi_selector is not None:
            self.snipe_dpi_selector.close()
        if self.multimedia_selector is not None:
            self.multimedia_selector.close()

        self.close()

    def save_default(self, file_name):
        with open(DATA_DIR+".default","w") as f:
            f.write(file_name)

        logging.info(f"saving as {file_name} default")

    def read_default(self):
        with open(DATA_DIR+".default", "r") as f:
            current_default = f.readline().rstrip()
            logging.info(f"default file is: {current_default}")

        return current_default

    def load_profile(self, file_name, default=False):
        if default:
            path = DATA_DIR+file_name
        else:
            path = PROFILES_DIR+file_name+".yml"

        logging.info(f"loading {file_name}")
        self.data.settings_yml = self.data.load_data(path)

        bindings_data = self.data.settings_yml["bindings_data"]

        # load led settings
        main_data = self.data.settings_yml["main_data"]

        chosen_led_mode = main_data["chosen"]
        steady_option = main_data["steady"]["option"]
        breath_option = main_data["breath"]["option"]
        neon_option = main_data["neon"]["option"]
        off_option = main_data["off"]["option"]

        steady_color = main_data["steady"]["color"]
        breath_color= main_data["breath"]["color"]
        neon_color = main_data["neon"]["color"]
        off_color = main_data["off"]["color"]
        
        options_list = [steady_option, breath_option, neon_option, off_option]
        colors_list = [steady_color, breath_color, neon_color, off_color]

        self.led_changer.set_mode(chosen_led_mode)
        self.led_changer.set_options(options_list)
        self.led_changer.set_color(colors_list)

        # current mode
        start_mode = "mode1"

        for i, name in enumerate(self.bindings_buttons_names):
            self.bindings_menus[i].set_text(bindings_data[start_mode][name]["name"])

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
        self.profile_label.setText("Profile: " + self.current_profile)

