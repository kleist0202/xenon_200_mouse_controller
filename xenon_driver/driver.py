import usb.core
import usb.util

from xenon_driver.logger import xenon_logger


class Driver:
    def __init__(self, id_vendor, id_product, *, dry_run=False):
        xenon_logger.info("driver INIT")

        self.id_vendor = id_vendor
        self.id_product = id_product
        self.dry_run = dry_run
        self.interface = 1

    def __enter__(self):
        xenon_logger.info("driver ENTER")
        # self.dev = usb.core.find(idVendor=self.id_vendor, idProduct=self.id_product)
        # if self.dev is None:
        #     return
        # self.endpoint = self.dev[0][(self.interface, 0)][0]
        return self

    def __exit__(self, type, value, traceback):
        xenon_logger.info("driver EXIT")
        if type:
            xenon_logger.debug(
                f"Driver: xenon_logger exception {type, value, traceback}"
            )

    def connect(self):
        self.dev = usb.core.find(idVendor=self.id_vendor, idProduct=self.id_product)
        xenon_logger.info("trying to reconnect...")
        if self.dev is None:
            return
        self.endpoint = self.dev[0][(self.interface, 0)][0]

    def send_data(self, data):
        self.connect()

        if self.dry_run:
            xenon_logger.info("Driver (dry run): data has not been sent")
            return

        try:
            self.dev.detach_kernel_driver(self.interface)
        except (usb.core.USBError, AttributeError):
            return

        xenon_logger.debug("Driver: DETACHING KERNEL DRIVER")
        usb.util.claim_interface(self.dev, self.interface)
        xenon_logger.debug("Driver: CLAIMING INTERFACE")

        # self.dev.set_interface_altsetting(interface=self.interface, alternate_setting=0)

        self.dev.ctrl_transfer(
            bmRequestType=0x21,
            bRequest=0x09,
            wValue=0x0304,
            wIndex=0x0001,
            data_or_wLength=data.main_data,
            timeout=1000,
        )

        self.dev.ctrl_transfer(
            bmRequestType=0x21,
            bRequest=0x09,
            wValue=0x0308,
            wIndex=0x0001,
            data_or_wLength=data.reset_data,
            timeout=1000,
        )

        self.dev.ctrl_transfer(
            bmRequestType=0x21,
            bRequest=0x09,
            wValue=0x0306,
            wIndex=0x0001,
            data_or_wLength=data.bindings_data,
            timeout=1000,
        )

        xenon_logger.info("Driver: DATA HAS BEEN SENT")

        usb.util.release_interface(self.dev, 1)
        xenon_logger.debug("Driver: RELEASING INTERFACE")
        self.dev.attach_kernel_driver(1)
        xenon_logger.debug("Driver: ATTACHING KERNEL DRIVER")

        return 0
