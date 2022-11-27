import yaml
from pathlib import Path

from xenon_driver.configuration import DATA_DIR
from xenon_driver.logger import xenon_logger


class Data:
    def __init__(self, file_path=None):
        yaml.add_representer(int, self.hexint_presenter)

        self.settings_yml = None
        self.file_name = file_path
        self.main_data = self.load_bytes(DATA_DIR + "main_data")
        self.reset_data = self.load_bytes(DATA_DIR + "reset_data")
        self.bindings_data = self.load_bytes(DATA_DIR + "bindings_data")

        if self.file_name is not None:
            self.settings_yml = self.load_data(file_path)

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

    def load_data(self, file_path):
        try:
            with open(file_path, "r") as file:
                default_settings = yaml.safe_load(file)

            file_name = Path(file_path).stem
            self.file_name = file_name
            xenon_logger.info(f"Data: name of current settings file: {file_name}")

        except FileNotFoundError:
            xenon_logger.info("Data: settings file not found: opening default settings")
            with open(DATA_DIR + "default_settings.yml", "r") as file:
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
