"""LilyGo T-embed 170x320
"""

from machine import Pin, SPI
import st7789py as st7789

TFT_CS   = 41
TFT_DC   = 16
TFT_RST  = 40
TFT_BL   = 21   # backlight pin
TFT_PWR  = 15   # board power pin
TFT_SCLK = 11
TFT_MOSI = 9

TFA = 0
BFA = 0
WIDE = 1
TALL = 0
SCROLL = 0      # orientation for scroll.py
FEATHERS = 1    # orientation for feathers.py

POWER = Pin(46, Pin.OUT, value=1)

def config(rotation=0) -> st7789.ST7789:
    """
    Configures and returns an instance of the ST7789 display driver.

    Args:
        rotation (int): The rotation of the display (default: 0).

    Returns:
        ST7789: An instance of the ST7789 display driver.
    """

    custom_rotations = (
        (0x00, 170, 320, 35, 0, False),
        (0x60, 320, 170, 0, 35, False),
        (0xC0, 170, 320, 35, 0, False),
        (0xA0, 320, 170, 0, 35, False),
    )

    return st7789.ST7789(
        SPI(2, baudrate=40000000, sck=Pin(TFT_SCLK), mosi=Pin(TFT_MOSI), miso=None),
        170,
        320,
        cs=Pin(TFT_CS, Pin.OUT),
        dc=Pin(TFT_DC, Pin.OUT),
        reset=Pin(TFT_RST, Pin.OUT),
        backlight=Pin(TFT_BL, Pin.OUT),
        custom_rotations=custom_rotations,
        rotation=rotation,
        color_order=st7789.BGR,
    )

 