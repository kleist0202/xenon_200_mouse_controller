import sys
import xenon_driver
import argparse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry_run", "-d", action="store_true")

    args = p.parse_args()

    is_dry_run = vars(args)["dry_run"]

    with xenon_driver.Driver(0x258A, 0x1007) as driver:
        w = xenon_driver.Window(driver, dry_run=is_dry_run)
        w.show()
        sys.exit(xenon_driver.Window.App.exec_())


if __name__ == "__main__":
    main()
