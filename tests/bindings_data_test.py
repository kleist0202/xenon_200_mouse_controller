import sys
from context import xenon_driver
from test_helper import TestHelper
import threading


def main():

    left_monitor_size = [1360, 768]

    right_button = [750, 460]
    dpi_loop = [750, 600]
    fire_key = [750, 725]
    combination = [750, 975]
    press_a = "a"
    press_b = "b"
    press_shift = "Shift_L"
    combination_ok = [1050, 575]
    apply = [1150, 800]

    coords_list = [
        right_button,
        dpi_loop,
        fire_key,
        combination,
        press_a,
        press_b,
        press_shift,
        combination_ok,
        apply,
    ]

    # trnaslate coord when left monitor is on
    TestHelper.coords_translation(coords_list, left_monitor_size[0])

    with xenon_driver.Driver(0x258A, 0x1007, dry_run=True) as driver:
        w = xenon_driver.Window(driver, dry_run=True, load_default=True)

        th = TestHelper(w)
        thr = threading.Thread(
            target=th.run_test,
            args=(coords_list, w.data.bindings_data, "./test_bindings_data"),
        )

        w.show()

        thr.start()
        sys.exit(xenon_driver.Window.App.exec_())


if __name__ == "__main__":
    main()
