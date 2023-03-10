from context import xenon_driver


def main():
    with xenon_driver.Driver(0x258a, 0x1007) as driver:
        data = xenon_driver.Data()
        data_handler = xenon_driver.DataHandler(data)
        # data_handler.set_left_button(xenon_driver.Options.CLICK_MASK, xenon_driver.Options.LEFT_BUTTON)
        # data_handler.set_led(xenon_driver.Options.STEADY, 0x51, 255, 0, 0)
        # driver.catch_interrupt()
        m = xenon_driver.Macro()
        m.macro_bytes = [
            0x01, 0x04, 0x81, 0x04, 0x01, 0x06, 0x81, 0x06,
        ]
        # data_handler.set_right_button(xenon_driver.Options.MACRO_MASK, xenon_driver.Options.MACRO_ACTION, macro=m)
        # data_handler.set_fire_button(xenon_driver.Options.CLICK_MASK, xenon_driver.Options.LEFT_BUTTON)
        data_handler.set_fire_button(xenon_driver.Options.KEY_COMBINATION_MASK, 0, 0xa0)
        data.print_hex(data.bindings_data)
        driver.send_data(data)


if __name__ == "__main__":
    main()
