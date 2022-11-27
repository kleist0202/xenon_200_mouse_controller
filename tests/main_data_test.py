import sys
from context import xenon_driver
from test_helper import TestHelper
import threading


def main():

    # left_monitor_size = [1360, 768]

    breath_coords = [930, 508]
    breath_speed = [1050, 508]
    breath_4_seconds = [1050, 490]
    color_picker_open = [1245, 508]
    color_picked = [1092, 364]
    color_picker_ok = [1060, 730]

    report_rate_250 = [1025, 375]

    set_first_dpi = [1050, 655]
    disable_first_dpi = [935, 685]

    apply = [1150, 800]

    coords_list = [
        breath_coords,
        breath_speed,
        breath_4_seconds,
        color_picker_open,
        color_picked,
        color_picker_ok,
        report_rate_250,
        set_first_dpi,
        disable_first_dpi,
        apply,
    ]

    # trnaslate coord when left monitor is on
    # TestHelper.coords_translation(coords_list, left_monitor_size[0])

    with xenon_driver.Driver(0x258A, 0x1007) as driver:
        w = xenon_driver.Window(driver, dry_run=True, load_default=True)

        th = TestHelper(w)
        thr = threading.Thread(
            target=th.run_test, args=(coords_list, w.data.main_data, "./test_main_data")
        )

        w.show()

        thr.start()
        sys.exit(xenon_driver.Window.App.exec_())


if __name__ == "__main__":
    main()
