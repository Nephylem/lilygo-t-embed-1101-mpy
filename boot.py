import lib.configs.tft_buttons as tft_buttons
import time

buttons = tft_buttons.Input()

while True:
    ev = buttons.get_event()
        
    if ev:
        try:
            print("Event:", ev) 
            time.sleep(0.01)
        except KeyboardInterrupt:
            break  # prints left, right, ok, back
