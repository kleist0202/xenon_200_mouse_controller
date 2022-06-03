import usb.core
import usb.util

import logging

logger = logging.getLogger(__name__)


class Driver:
    def __init__(self, id_vendor, id_product, *, dry_run=False):
        self.dry_run = dry_run
        self.interface = 1
        logging.info("driver INIT")

        self.dev = usb.core.find(idVendor=id_vendor, idProduct=id_product)

    def __enter__(self):
        logging.info("driver ENTER")
        if self.dev is None:
            return
        self.endpoint = self.dev[0][(self.interface,0)][0]
        return self

    def __exit__(self, type, value, traceback):
        logger.info("driver EXIT")
        if type:
            logger.debug(f"Driver: Logging exception {type, value, traceback}")

    def send_data(self, data):
        if self.dry_run:
            logger.info("Driver (dry run): data has not been sent")
            return

        try:
            self.dev.detach_kernel_driver(self.interface)
        except usb.core.USBError:
            return

        logger.debug("Driver: DETACHING KERNEL DRIVER")
        usb.util.claim_interface(self.dev, self.interface)
        logger.debug("Driver: CLAIMING INTERFACE")

        self.dev.set_interface_altsetting(interface=self.interface, alternate_setting=0)

        self.dev.ctrl_transfer(
                bmRequestType=0x21,
                bRequest=0x09,
                wValue=0x0304,
                wIndex=0x0001,
                data_or_wLength=data.main_data,
                timeout=1000
        )

        self.dev.ctrl_transfer(
                bmRequestType=0x21,
                bRequest=0x09,
                wValue=0x0308,
                wIndex=0x0001,
                data_or_wLength=data.reset_data,
                timeout=1000
        )

        self.dev.ctrl_transfer(
                bmRequestType=0x21,
                bRequest=0x09,
                wValue=0x0306,
                wIndex=0x0001,
                data_or_wLength=data.bindings_data,
                timeout=1000
        )
        
        logger.info("Driver: DATA HAS BEEN SENT")

        usb.util.release_interface(self.dev, 1)
        logger.debug("Driver: RELEASING INTERFACE")
        self.dev.attach_kernel_driver(1)
        logger.debug("Driver: ATTACHING KERNEL DRIVER")

        return 0
