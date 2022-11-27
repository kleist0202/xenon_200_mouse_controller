import subprocess
import time


class TestHelper:
    def __init__(self, window):
        self.window = window
        self.data = window.data

        time.sleep(0.25)

    def run_test(self, coords_list, data_to_check, correct_file):
        for coords in coords_list:
            if isinstance(coords, list):
                self.click_on_screen(*coords, 1)
            else:
                self.key_press(coords)

        # return

        errors = []

        correct_bytes = self.data.load_bytes(correct_file)
        for i, (gui_byte, correct_byte) in enumerate(
            zip(data_to_check, correct_bytes), start=1
        ):
            if gui_byte == correct_byte:
                continue
            else:
                errors.append(i)

        print()

        if errors:
            print("\033[91mTEST: correct bytes:\033[0m")
            for i, byte in enumerate(correct_bytes, start=1):
                if i in errors:
                    print(f"\033[91m0x{byte:02x}\033[0m", end=" ")
                else:
                    print(f"0x{byte:02x}", end=" ")
                if i % 16 == 0:
                    print()
            print()
            print()

            print("\033[91mTEST: received bytes:\033[0m")
            for i, byte in enumerate(data_to_check, start=1):
                if i in errors:
                    print(f"\033[91m0x{byte:02x}\033[0m", end=" ")
                else:
                    print(f"0x{byte:02x}", end=" ")
                if i % 16 == 0:
                    print()

            print()
            print()

            print("\033[91m******************************************\033[0m")
            print("\033[91mTEST: data bytes are different!\033[0m")
            print(f"\033[91mTEST: test failed at bytes: {errors}!\033[0m")
            print("\033[91m******************************************\033[0m")
            print()

            self.window.kill_em_all()
        else:
            self.data.print_hex(data_to_check)

            print()
            print()

            print("\033[92m******************************************\033[0m")
            print("\033[92mTEST: test passed successfully!\033[0m")
            print("\033[92m******************************************\033[0m")
            print()

            self.window.kill_em_all()

    def click_on_screen(self, x, y, mouseButton=1):
        time.sleep(0.25)
        subprocess.run(
            ["/usr/bin/xdotool", "mousemove", str(x), str(y), "click", str(mouseButton)]
        )
        time.sleep(0.25)

    def key_press(self, key):
        time.sleep(0.25)
        subprocess.run(["/usr/bin/xdotool", "key", str(key)])
        time.sleep(0.25)

    @staticmethod
    def coords_translation(coords_list, translation):
        for i, coords in enumerate(coords_list):
            if isinstance(coords, list):
                coords_list[i][0] = coords[0] + translation
