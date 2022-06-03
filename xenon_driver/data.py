from xenon_driver.configuration import DATA_DIR
from .options import Options
import yaml
from pathlib import Path


class Data:
    def __init__(self, file_path=None):
        yaml.add_representer(int, self.hexint_presenter)

        self.settings_yml = None
        self.file_name = file_path
        self.main_data = self.load_bytes(DATA_DIR+"main_data")
        self.reset_data = self.load_bytes(DATA_DIR+"reset_data")
        self.bindings_data = self.load_bytes(DATA_DIR+"bindings_data")

        if self.file_name is not None:
            self.settings_yml = self.load_data(file_path)
            self.assign_bytes(self.settings_yml, self.main_data, self.reset_data, self.bindings_data)

    @staticmethod
    def load_bytes(data_file_name):
        bytes_list = []
        with open(data_file_name, "r") as file:
            lines = file.readlines()
            for line in lines:
                bytes_line = line.rstrip().split(" ")
                for byte in bytes_line:
                    bytes_list.append(int(byte, 16))

        return bytes_list

    @staticmethod
    def assign_bytes(settings_yml, main_data, reset_data, bindings_data):
        chosen = settings_yml["main_data"]["chosen"].lower()
        led = settings_yml["main_data"][chosen]["value"]
        br = settings_yml["main_data"][chosen]["option"]
        c = settings_yml["main_data"][chosen]["color"]
        dirn = settings_yml["main_data"]["dirn"]
        rr = settings_yml["main_data"]["rr"]
        d = settings_yml["main_data"]["dpis"]

        mode1 = settings_yml["bindings_data"]["mode1"]
        mode2 = settings_yml["bindings_data"]["mode2"]
        mode3 = settings_yml["bindings_data"]["mode3"]

        dpis = 0x04

        main_data[8] = rr

        main_data[71] = dpis

        main_data[73] = dirn

        main_data[74] = d[0]
        main_data[75] = d[1]
        main_data[76] = d[2]
        main_data[77] = d[3]

        main_data[93] = led

        main_data[96] = br
        main_data[97] = c[0]
        main_data[98] = c[1]
        main_data[99] = c[2]

        mode = Options.MODE1
        
        reset_data[1] = mode

        # mifj -> m - mode, i - mode number (1-3), f - flag (class Options), j - button number (1-8)  
        # miaj -> m - mode, i - mode number (1-3), a - action (class Options), j - button number (1-8)  
        m1f1 = mode1['left_button']['data'][0];    m1a1 = mode1['left_button']['data'][1];    m1s1 = mode1['left_button']['data'][2];    m1t1 = mode1['left_button']['data'][3]
        m1f2 = mode1['right_button']['data'][0];   m1a2 = mode1['right_button']['data'][1];   m1s2 = mode1['right_button']['data'][2];   m1t2 = mode1['right_button']['data'][3]
        m1f3 = mode1['middle_button']['data'][0];  m1a3 = mode1['middle_button']['data'][1];  m1s3 = mode1['middle_button']['data'][2];  m1t3 = mode1['middle_button']['data'][3]
        m1f4 = mode1['back_button']['data'][0];    m1a4 = mode1['back_button']['data'][1];    m1s4 = mode1['back_button']['data'][2];    m1t4 = mode1['back_button']['data'][3]
        m1f5 = mode1['forward_button']['data'][0]; m1a5 = mode1['forward_button']['data'][1]; m1s5 = mode1['forward_button']['data'][2]; m1t5 = mode1['forward_button']['data'][3]
        m1f6 = mode1['dpi_button']['data'][0];     m1a6 = mode1['dpi_button']['data'][1];     m1s6 = mode1['dpi_button']['data'][2];     m1t6 = mode1['dpi_button']['data'][3]
        m1f7 = mode1['fire_button']['data'][0];    m1a7 = mode1['fire_button']['data'][1];    m1s7 = mode1['fire_button']['data'][2];    m1t7 = mode1['fire_button']['data'][3]
        m1f8 = mode1['mode_button']['data'][0];    m1a8 = mode1['mode_button']['data'][1];    m1s8 = mode1['mode_button']['data'][2];    m1t8 = mode1['mode_button']['data'][3]

        m2f1 = mode2['left_button']['data'][0];    m2a1 = mode2['left_button']['data'][1];    m2s1 = mode2['left_button']['data'][2];    m2t1 = mode2['left_button']['data'][3]
        m2f2 = mode2['right_button']['data'][0];   m2a2 = mode2['right_button']['data'][1];   m2s2 = mode2['right_button']['data'][2];   m2t2 = mode2['right_button']['data'][3]
        m2f3 = mode2['middle_button']['data'][0];  m2a3 = mode2['middle_button']['data'][1];  m2s3 = mode2['middle_button']['data'][2];  m2t3 = mode2['middle_button']['data'][3]
        m2f4 = mode2['back_button']['data'][0];    m2a4 = mode2['back_button']['data'][1];    m2s4 = mode2['back_button']['data'][2];    m2t4 = mode2['back_button']['data'][3]
        m2f5 = mode2['forward_button']['data'][0]; m2a5 = mode2['forward_button']['data'][1]; m2s5 = mode2['forward_button']['data'][2]; m2t5 = mode2['forward_button']['data'][3]
        m2f6 = mode2['dpi_button']['data'][0];     m2a6 = mode2['dpi_button']['data'][1];     m2s6 = mode2['dpi_button']['data'][2];     m2t6 = mode2['dpi_button']['data'][3]
        m2f7 = mode2['fire_button']['data'][0];    m2a7 = mode2['fire_button']['data'][1];    m2s7 = mode2['fire_button']['data'][2];    m2t7 = mode2['fire_button']['data'][3]
        m2f8 = mode2['mode_button']['data'][0];    m2a8 = mode2['mode_button']['data'][1];    m2s8 = mode2['mode_button']['data'][2];    m2t8 = mode2['mode_button']['data'][3]

        m3f1 = mode3['left_button']['data'][0];    m3a1 = mode3['left_button']['data'][1];    m3s1 = mode3['left_button']['data'][2];    m3t1 = mode3['left_button']['data'][3]
        m3f2 = mode3['right_button']['data'][0];   m3a2 = mode3['right_button']['data'][1];   m3s2 = mode3['right_button']['data'][2];   m3t2 = mode3['right_button']['data'][3]
        m3f3 = mode3['middle_button']['data'][0];  m3a3 = mode3['middle_button']['data'][1];  m3s3 = mode3['middle_button']['data'][2];  m3t3 = mode3['middle_button']['data'][3]
        m3f4 = mode3['back_button']['data'][0];    m3a4 = mode3['back_button']['data'][1];    m3s4 = mode3['back_button']['data'][2];    m3t4 = mode3['back_button']['data'][3]
        m3f5 = mode3['forward_button']['data'][0]; m3a5 = mode3['forward_button']['data'][1]; m3s5 = mode3['forward_button']['data'][2]; m3t5 = mode3['forward_button']['data'][3]
        m3f6 = mode3['dpi_button']['data'][0];     m3a6 = mode3['dpi_button']['data'][1];     m3s6 = mode3['dpi_button']['data'][2];     m3t6 = mode3['dpi_button']['data'][3]
        m3f7 = mode3['fire_button']['data'][0];    m3a7 = mode3['fire_button']['data'][1];    m3s7 = mode3['fire_button']['data'][2];    m3t7 = mode3['fire_button']['data'][3]
        m3f8 = mode3['mode_button']['data'][0];    m3a8 = mode3['mode_button']['data'][1];    m3s8 = mode3['mode_button']['data'][2];    m3t8 = mode3['mode_button']['data'][3]

        bindings_data[1026] = m1f1; bindings_data[1027] = m1a1; bindings_data[1028] = m1s1; bindings_data[1029] = m1t1
        bindings_data[1030] = m1f2; bindings_data[1031] = m1a2; bindings_data[1032] = m1s2; bindings_data[1033] = m1t2
        bindings_data[1034] = m1f3; bindings_data[1035] = m1a3; bindings_data[1036] = m1s3; bindings_data[1037] = m1t3
        bindings_data[1038] = m1f4; bindings_data[1039] = m1a4; bindings_data[1040] = m1s4; bindings_data[1041] = m1t4
        bindings_data[1042] = m1f5; bindings_data[1043] = m1a5; bindings_data[1044] = m1s5; bindings_data[1045] = m1t5
        bindings_data[1046] = m1f6; bindings_data[1047] = m1a6; bindings_data[1048] = m1s6; bindings_data[1049] = m1t6
        bindings_data[1050] = m1f7; bindings_data[1051] = m1a7; bindings_data[1052] = m1s7; bindings_data[1053] = m1t7
        bindings_data[1054] = m1f8; bindings_data[1055] = m1a8; bindings_data[1056] = m1s8; bindings_data[1057] = m1t8

        bindings_data[1066] = m2f1; bindings_data[1067] = m2a1; bindings_data[1068] = m2s1; bindings_data[1069] = m2t1
        bindings_data[1070] = m2f2; bindings_data[1071] = m2a2; bindings_data[1072] = m2s2; bindings_data[1073] = m2t2
        bindings_data[1074] = m2f3; bindings_data[1075] = m2a3; bindings_data[1076] = m2s3; bindings_data[1077] = m2t3
        bindings_data[1078] = m2f4; bindings_data[1079] = m2a4; bindings_data[1080] = m2s4; bindings_data[1081] = m2t4
        bindings_data[1082] = m2f5; bindings_data[1083] = m2a5; bindings_data[1084] = m2s5; bindings_data[1085] = m2t5
        bindings_data[1086] = m2f6; bindings_data[1087] = m2a6; bindings_data[1088] = m2s6; bindings_data[1089] = m2t6
        bindings_data[1090] = m2f7; bindings_data[1091] = m2a7; bindings_data[1092] = m2s7; bindings_data[1093] = m2t7
        bindings_data[1094] = m2f8; bindings_data[1095] = m2a8; bindings_data[1096] = m2s8; bindings_data[1097] = m2t8

        bindings_data[1106] = m3f1; bindings_data[1107] = m3a1; bindings_data[1108] = m3s1; bindings_data[1109] = m3t1
        bindings_data[1110] = m3f2; bindings_data[1111] = m3a2; bindings_data[1112] = m3s2; bindings_data[1113] = m3t2
        bindings_data[1114] = m3f3; bindings_data[1115] = m3a3; bindings_data[1116] = m3s3; bindings_data[1117] = m3t3
        bindings_data[1118] = m3f4; bindings_data[1119] = m3a4; bindings_data[1120] = m3s4; bindings_data[1121] = m3t4
        bindings_data[1122] = m3f5; bindings_data[1123] = m3a5; bindings_data[1124] = m3s5; bindings_data[1125] = m3t5
        bindings_data[1126] = m3f6; bindings_data[1127] = m3a6; bindings_data[1128] = m3s6; bindings_data[1129] = m3t6
        bindings_data[1130] = m3f7; bindings_data[1131] = m3a7; bindings_data[1132] = m3s7; bindings_data[1133] = m3t7
        bindings_data[1134] = m3f8; bindings_data[1135] = m3a8; bindings_data[1136] = m3s8; bindings_data[1137] = m3t8

    def load_data(self, file_path):
        print(file_path)
        try:
            with open(file_path, "r") as file:
                default_settings = yaml.safe_load(file)

            file_name = Path(file_path).stem
            self.file_name = file_name
            print(f"Data: name of current settings file: {file_name}")

        except FileNotFoundError:
            print("Data: settings file not found: opening default settings")
            with open(DATA_DIR+"default_settings.yml", "r") as file:
                default_settings = yaml.safe_load(file)
            self.file_name = ""

        return default_settings

    def print_hex(self, data):
        for i, byte in enumerate(data, start=1):
            print(f"0x{byte:02x}", end=" ")
            if i % 16 == 0:
                print()
        print()

    def hexint_presenter(self, dumper, data):
        return dumper.represent_int(hex(data))
