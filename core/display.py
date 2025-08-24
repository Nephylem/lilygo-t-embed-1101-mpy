from lib import st7789py as st7789
from lib.configs import tft_config
from lib.fonts import vga1_8x8 as font_128
from lib.fonts import vga2_8x8 as font_256
import time
 
tft = tft_config.config(rotation=3) 

def panelSleep(sleep:bool): 

    if sleep:
 
        tft._write(command=b'\x10') # sleep in
        print('panel sleep in')
        time.sleep(3); 
    else: 
        tft._write(command=b'\x11') # sleep out
        print('panel sleep out')
        time.sleep(3)

def displayMessage(): 
   # Clear screen
    tft.fill(st7789.BLACK)

    # Draw rectangle (x, y, width, height, color)
    x, y = tft.width // 2, 50
    w, h = 130, 40
    tft.rect(x, y, w, h, st7789.RED)   # red border

    # Fill inside rectangle
    tft.fill_rect(x+1, y+1, w-2, h-2, st7789.YELLOW)

    # Draw warning text centered inside
    msg = "WARNING!"
    text_x = x + (w - len(msg) * 8) // 2   # each char is 8px wide in vga1_8x8
    text_y = y + (h - 8) // 2              # font height is 8px
    tft.text(font_128, msg, text_x, text_y, st7789.BLACK, st7789.YELLOW)

if __name__ == "__main__": 
     displayMessage()
