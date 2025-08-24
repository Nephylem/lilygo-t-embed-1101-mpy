from lib import st7789py as st7789
from lib.configs import tft_config
from lib.fonts import vga1_8x8 as font_128
from lib.fonts import vga2_8x8 as font_256
import time

tft = tft_config.config(rotation=0) 

# --- Splash screen ---
import utime
import random
 


def main():
    """ main """
    tft = tft_config.config(tft_config.SCROLL)
    last_line = tft.height - font_128.HEIGHT
    tfa = tft_config.TFA # top free area when scrolling
    bfa = tft_config.BFA # bottom free area when scrolling
    tft.vscrdef(tfa, 240, bfa)

    tft.fill(st7789.BLUE)
    scroll = 0
    character = 0
    col = tft.width // 2 - 5 * font_128.WIDTH // 2

    while True:
        tft.fill_rect(0, scroll, tft.width, 1, st7789.BLUE)

        if scroll % font_128.HEIGHT == 0:
            tft.text(
                font_128,
                f'x{character:02x} {chr(character)}',
                col,
                (scroll + last_line) % tft.height,
                st7789.WHITE,
                st7789.BLUE)

            character = character + 1 if character < 256 else 0

        tft.vscsad(scroll + tfa)
        scroll += 1

        if scroll == tft.height:
            scroll = 0

        utime.sleep(0.01)


main()