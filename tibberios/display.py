# Initial version of this functionality modified from:
# https://github.com/waveshare/e-Paper/blob/master/RaspberryPi_JetsonNano/python/examples/epd_7in5_V2_test.py

import logging
import time

from PIL import Image

from .e_Paper.RaspberryPi_JetsonNano.python.lib.waveshare_epd import epd7in5_V2

logging.basicConfig(level=logging.DEBUG)


def update(image_path: str) -> None:
    try:
        logging.info("Loading epd7in5_V2")
        epd = epd7in5_V2.EPD()
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        logging.info("read bmp file")
        Himage = Image.open(image_path)
        epd.display(epd.getbuffer(Himage))
        time.sleep(2)

        logging.info("Goto Sleep...")
        epd.sleep()

    except IOError as e:
        logging.info(f"IOError: {e}")
        epd7in5_V2.epdconfig.module_exit()


def clear() -> None:
    epd = epd7in5_V2.EPD()
    logging.info("Clear...")
    epd.init()
    epd.Clear()
