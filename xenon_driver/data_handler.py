from xenon_driver.configuration import MACROS_DIR
from xenon_driver.gui_resources.gui_keys import GuiKeys
from .options import Options

from xenon_driver.logger import xenon_logger


class DataHandler:
    def __init__(self, data):
        self.handler_data = data
        self.main_data = data.main_data
        self.reset_data = data.reset_data
        self.bindings_data = data.bindings_data
        self.settings_yml = data.settings_yml

        self.basic_clicks = [Options.LEFT_BUTTON, Options.RIGHT_BUTTON, Options.MIDDLE_BUTTON]

        self.multimedia_keys = [
                Options.PLAYPAUSE, Options.NEXT, Options.PREVIOUS, Options.STOP,
                Options.MUTE, Options.VOLUMEUP, Options.VOLUMEDOWN
        ]

        self.dpi_loop_actions = [Options.DPI_LOOP, Options.DPI_PLUS, Options.DPI_MINUS]

    def bindings_checker(func):
        """
        Raise an error if entered arguments when setting bindings are invalid
        """
        def inner(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1):
            if mask is Options.CLICK_MASK:
                speed = 0x00
                times = 0x00
                if action not in self.basic_clicks and action not in [Options.BACK_BUTTON, Options.FORWARD_BUTTON]:
                    raise Exception(f"Wrong action for {mask}")

            elif mask is Options.DPI_LOOP_MASK:
                speed = 0x00
                times = 0x00

                if action not in self.dpi_loop_actions:
                    raise Exception(f"Wrong action for {mask}")

            elif mask is Options.FIRE_MASK:
                if speed < 5 or speed > 255:
                    raise Exception("'speed' allowed values are 5-255")

                if times < 1 or times > 255:
                    raise Exception("'times' allowed values are 1-255")

                if action not in self.basic_clicks:
                    raise Exception(f"Wrong action for {mask}")

            elif mask is Options.MODE_MASK:
                action = Options.MODE_ACTION
                speed = 0x00
                times = 0x00

            elif mask is Options.THREE_CLICK_MASK:
                action = Options.THREE_CLICK_ACTION
                speed = 0x00
                times = 0x00

            elif mask is Options.MULTIMEDIA_MASK:
                speed = 0x00
                times = 0x00

                if action not in self.multimedia_keys:
                    raise Exception(f"Wrong action for {mask}")

            elif mask is Options.DISABLE_MASK:
                action = Options.DISABLE_ACTION
                speed = 0x00
                times = 0x00

            elif mask is Options.KEY_COMBINATION_MASK:
                pass

            else:
                raise Exception(f"This mask is not allowed ({mask})!")

            func(self, mask, action, speed, times, mode)
        return inner

    def macro_number(nth):
        def inner(func):
            def wrapper(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
                if mask == Options.MACRO_MASK:
                    start_byte = 2+nth*128
                    self.bindings_data[start_byte] = macro.cycle_times
                    for i, index in enumerate(range(start_byte, start_byte+125)):
                        if i > 127-3:
                            break
                        self.bindings_data[index+1] = macro.macro_bytes[i]
                    action |= (nth+1 << 4)
                    action += macro.macro_mode

                func(self, mask, action, speed, times, mode, macro)

            return wrapper
        return inner

    def show_bytes(self):
        xenon_logger.info("Showing Main")
        for i, b in enumerate(self.main_data):
            xenon_logger.info(f"{i}, {hex(b)}")

        xenon_logger.info("Showing Reset")
        for i, b in enumerate(self.reset_data):
            xenon_logger.info(f"{i}, {hex(b)}")

        xenon_logger.info("Showing Bindings data")
        for i, b in enumerate(self.bindings_data):
            xenon_logger.info(f"{i}, {hex(b)}")

    def set_led(self, mode, option=0x00, r=0x00, g=0x00, b=0x00):
        """
        mode:
            Options.STEADY
            Options.BREATH
            Options.NEON
            Options.OFF

        option:
            STEADY
            0x11 -> 10%
            0x51 -> 50%
            0xa1 -> 100%
            
            BREATH
            0x01 -> 1s
            0x11 -> 4s
            0x51 -> 6s
            0xa1 -> 8s
            
            NEON
            0x11 -> 2s
            0x51 -> 4s
            0xa1 -> 6s

        r, g, b:
            0x00-0xff -> colors
        """
        self.main_data[93] = mode
        self.main_data[96] = option
        self.main_data[97] = r
        self.main_data[98] = g
        self.main_data[99] = b

    def set_report_rate(self, report_rate):
        """
        report_rate:
            Options.REPORT_RATE_250MHZ or
            Options.REPORT_RATE_500MHZ or
            Options.REPORT_RATE_1000MHZ
        """

        if report_rate not in [Options.REPORT_RATE_250MHZ, Options.REPORT_RATE_500MHZ, Options.REPORT_RATE_1000MHZ]:
            raise Exception("This option is not allowed (report rate)")

        self.main_data[8] = int(report_rate)

    def set_direction(self, direction):
        """
        direction:
            normal/inverse -> directions
        """
        if direction == "normal":
            self.main_data[73] = Options.NORMAL_DIRECTION
        elif direction == "inverse":
            self.main_data[73] = Options.INVERSE_DIRECTION
        else:
            raise Exception("No such option (direction)")

    def set_dpi_values(self, level, value):
        """
        level:
            1,2,3,4 -> dpi levels
        value:
            0x00-0x0b -> dpi value
        """

        if (value < 0x00 or value > 0x0b) and (value < 0x80 or value > 0x8b):
            raise Exception("No such option (dpi value)")

        if level == 1:
            self.main_data[74] = value
        elif level == 2:
            self.main_data[75] = value
        elif level == 3:
            self.main_data[76] = value
        elif level == 4:
            self.main_data[77] = value
        else:
            raise Exception("No such option (dpi level)")

    def set_dpi_levels(self, level):
        """
        level:
            1 or 2 or 3 or 4
        """

        if level < 0x00 or level > 0x04:
            raise Exception("No such option (dpi level)")

        self.main_data[71] = level

    # @bindings_checker
    @macro_number(0)
    def set_left_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for left mouse button

        mask:
            Options.*MASK
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        # 66 67 68 69
        if mode == 1:
            self.bindings_data[1026] = 0x01 | mask
            self.bindings_data[1027] = action
            self.bindings_data[1028] = speed
            self.bindings_data[1029] = times
        elif mode == 2:
            self.bindings_data[1066] = 0x01 | mask
            self.bindings_data[1067] = action
            self.bindings_data[1068] = speed
            self.bindings_data[1069] = times
        elif mode == 3:
            self.bindings_data[1106] = 0x01 | mask
            self.bindings_data[1107] = action
            self.bindings_data[1108] = speed
            self.bindings_data[1109] = times
        else:
            raise Exception("Allowed mode numbers are within range: 1-3")

    # @bindings_checker
    @macro_number(1)
    def set_right_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for right mouse button

        mask:
            Options.*MASK
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1030] = 0x02 | mask
            self.bindings_data[1031] = action
            self.bindings_data[1032] = speed
            self.bindings_data[1033] = times
        elif mode == 2:
            self.bindings_data[1070] = 0x02 | mask
            self.bindings_data[1071] = action
            self.bindings_data[1072] = speed
            self.bindings_data[1073] = times
        elif mode == 3:
            self.bindings_data[1110] = 0x02 | mask
            self.bindings_data[1111] = action
            self.bindings_data[1112] = speed
            self.bindings_data[1113] = times

    # @bindings_checker
    @macro_number(2)
    def set_middle_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for middle mouse button

        mask:
            Options.*MASK -> mask from class Options
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1034] = 0x03 | mask
            self.bindings_data[1035] = action
            self.bindings_data[1036] = speed
            self.bindings_data[1037] = times
        elif mode == 2:
            self.bindings_data[1074] = 0x03 | mask
            self.bindings_data[1075] = action
            self.bindings_data[1076] = speed
            self.bindings_data[1077] = times
        elif mode == 3:
            self.bindings_data[1114] = 0x03 | mask
            self.bindings_data[1115] = action
            self.bindings_data[1116] = speed
            self.bindings_data[1117] = times
    
    # @bindings_checker
    @macro_number(3)
    def set_back_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for back mouse button

        mask:
            Options.*MASK -> mask from class Options
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1038] = 0x04 | mask
            self.bindings_data[1039] = action
            self.bindings_data[1040] = speed
            self.bindings_data[1041] = times
        elif mode == 2:
            self.bindings_data[1078] = 0x04 | mask
            self.bindings_data[1079] = action
            self.bindings_data[1080] = speed
            self.bindings_data[1081] = times
        elif mode == 3:
            self.bindings_data[1118] = 0x04 | mask
            self.bindings_data[1119] = action
            self.bindings_data[1120] = speed
            self.bindings_data[1121] = times

    # @bindings_checker
    @macro_number(4)
    def set_forward_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for forward mouse button

        mask:
            Options.*MASK -> mask from class Options
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1042] = 0x05 | mask
            self.bindings_data[1043] = action
            self.bindings_data[1044] = speed
            self.bindings_data[1045] = times
        elif mode == 2:
            self.bindings_data[1082] = 0x05 | mask 
            self.bindings_data[1083] = action
            self.bindings_data[1084] = speed
            self.bindings_data[1085] = times
        elif mode == 3:
            self.bindings_data[1122] = 0x05 | mask 
            self.bindings_data[1123] = action
            self.bindings_data[1124] = speed
            self.bindings_data[1125] = times

    # @bindings_checker
    @macro_number(5)
    def set_dpi_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for dpi mouse button

        mask:
            Options.*MASK -> mask from class Options
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1046] = 0x06 | mask
            self.bindings_data[1047] = action
            self.bindings_data[1048] = speed
            self.bindings_data[1049] = times
        elif mode == 2:
            self.bindings_data[1086] = 0x06 | mask
            self.bindings_data[1087] = action
            self.bindings_data[1088] = speed
            self.bindings_data[1089] = times
        elif mode == 3:
            self.bindings_data[1126] = 0x06 | mask
            self.bindings_data[1127] = action
            self.bindings_data[1128] = speed
            self.bindings_data[1129] = times
        
    # @bindings_checker
    @macro_number(7)
    def set_fire_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for fire mouse button

        mask:
            Options.*MASK -> mask from class Options
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key 
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1050] = 0x07 | mask
            self.bindings_data[1051] = action
            self.bindings_data[1052] = speed
            self.bindings_data[1053] = times
        elif mode == 2:
            self.bindings_data[1090] = 0x07 | mask
            self.bindings_data[1091] = action
            self.bindings_data[1092] = speed
            self.bindings_data[1093] = times
        elif mode == 3:
            self.bindings_data[1130] = 0x07 | mask
            self.bindings_data[1131] = action
            self.bindings_data[1132] = speed
            self.bindings_data[1133] = times

    # @bindings_checker
    @macro_number(6)
    def set_mode_button(self, mask, action=Options.DEFAULT, speed=0x00, times=0x00, mode=1, macro=None):
        """
        Set action for mode mouse button

        mask:
            Options.*MASK -> mask from class Options
        action:
            Options.* -> some action
            or
            Options.LCTRL/LSHIFT/LALT -> these keys
        speed:
            5-255 -> for fire key
            or
            Options.KEY_*
        times:
            1-255 -> for fire key
            or
            Options.KEY_*
        """

        if mode == 1:
            self.bindings_data[1054] = 0x08 | mask
            self.bindings_data[1055] = action
            self.bindings_data[1056] = speed
            self.bindings_data[1057] = times
        elif mode == 2:
            self.bindings_data[1094] = 0x08 | mask
            self.bindings_data[1095] = action
            self.bindings_data[1096] = speed
            self.bindings_data[1097] = times
        elif mode == 3:
            self.bindings_data[1134] = 0x08 | mask
            self.bindings_data[1135] = action
            self.bindings_data[1136] = speed
            self.bindings_data[1137] = times

    def set_current_mode(self, mode):
        """
        Only for changing blink color when new data is written (probably?)

        mode: int
            1 or 2 or 3
        """
        self.reset_data[1] = mode


class MacroTranslator:
    def __init__(self, macro_file_name):

        self.macro_bytes = []

        try:
            with open(MACROS_DIR+macro_file_name, 'r') as file:
                macro_text = file.readline()
        except FileNotFoundError:
            return

        macro_full = macro_text.split(":")
        macro_prefix = macro_full[0]
        macro_text_list = macro_full[1].split(",")

        self.macro_mode = int(macro_prefix.split(",")[0])
        self.cycle_times = int(macro_prefix.split(",")[1])

        real_index = 0
        for _, key in enumerate(macro_text_list):
            elems = key.split(" ")
            if elems[0] == '':
                xenon_logger.warning("No data in macro")

                while len(self.macro_bytes) < 125:
                    self.macro_bytes.append(0x00)
                    xenon_logger.debug(f"macro_bytes length: {len(self.macro_bytes)}")
                return

            xenon_logger.debug(f"Elements: {elems}, Index:{real_index}")

            if elems[0] == "Key":
                if elems[3] == "Down":
                    self.macro_bytes.append(0x01)
                    for key, value in GuiKeys.keys_dict.items():
                        if value[0] == elems[1]:
                            self.macro_bytes.append(value[1])
                elif elems[3] == "Up":
                    self.macro_bytes.append(0x81)
                    for key, value in GuiKeys.keys_dict.items():
                        if value[0] == elems[1]:
                            self.macro_bytes.append(value[1])
                real_index += 2
            elif elems[1] == "button":
                if elems[3] == "Down":
                    self.macro_bytes.append(0x01)
                    mouse_button = GuiKeys.MOUSE_KEYS[elems[0]+" "+elems[1]]
                    self.macro_bytes.append(mouse_button)
                if elems[3] == "Up":
                    self.macro_bytes.append(0x81)
                    mouse_button = GuiKeys.MOUSE_KEYS[elems[0]+" "+elems[1]]
                    self.macro_bytes.append(mouse_button)
                real_index += 2
            elif elems[0] == "Delay":
                delay_value = int(elems[2])
                if delay_value < 128:
                    self.macro_bytes[real_index-2] += delay_value-1
                else:
                    hundreds = int(delay_value / 100)
                    rest = delay_value - hundreds*100
                    if rest == 0:
                        rest = 1
                    self.macro_bytes[real_index-2] += rest-1
                    if hundreds == 256:
                        hundreds = 0
                    self.macro_bytes.append(hundreds)
                    self.macro_bytes.append(0x03)
                    real_index += 2


        while len(self.macro_bytes) < 125:
            self.macro_bytes.append(0x00)

        xenon_logger.debug(f"{[hex(x) for x in self.macro_bytes]}")
        xenon_logger.debug(f"macro_bytes length: {len(self.macro_bytes)}")
