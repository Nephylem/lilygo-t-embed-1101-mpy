"""
On-screen keyboard for LilyGo T-Embed
Uses tft_buttons.py for navigation
"""

from lib import st7789py as st7789
from lib.fonts import vga1_8x8 as font
from lib.configs.tft_config import tft
import lib.configs.tft_buttons as buttons


class Keyboard:
    def __init__(self):
        # Define keys in a grid
        self.keys = [
            list("ABCDEF"),
            list("GHIJKL"),
            list("MNOPQR"),
            list("STUVWX"),
            list("YZ <- ")
        ]
        self.rows = len(self.keys)
        self.cols = len(self.keys[0])

        # Start position
        self.row = 0
        self.col = 0

        # Selected text buffer
        self.text = ""

        # Colors
        self.bg_color = st7789.BLACK
        self.key_color = st7789.WHITE
        self.highlight_color = st7789.YELLOW
        self.text_color = st7789.GREEN

        # Key dimensions
        self.key_w = 50
        self.key_h = 30
        self.start_x = 10
        self.start_y = 20

        self.draw_keyboard()
        self.draw_text()

        # Register button callbacks
        buttons.on("up", self.move_up)
        buttons.on("down", self.move_down)
        buttons.on("left", self.move_left)
        buttons.on("right", self.move_right)
        buttons.on("ok", self.select_key)

    def draw_keyboard(self):
        tft.fill(self.bg_color)
        for r, row in enumerate(self.keys):
            for c, key in enumerate(row):
                x = self.start_x + c * self.key_w
                y = self.start_y + r * self.key_h

                # Highlight current key
                if r == self.row and c == self.col:
                    tft.fill_rect(x, y, self.key_w, self.key_h, self.highlight_color)
                    color = self.bg_color
                else:
                    tft.fill_rect(x, y, self.key_w, self.key_h, self.key_color)
                    color = self.bg_color

                # Center text
                tx = x + (self.key_w - len(key) * 8) // 2
                ty = y + (self.key_h - 8) // 2
                tft.text(font, key, tx, ty, color)

    def draw_text(self):
        # Draw typed text at bottom
        tft.fill_rect(0, 200, 170, 20, self.bg_color)
        tft.text(font, "Input: " + self.text, 5, 205, self.text_color)

    # Navigation
    def move_up(self):    self.row = (self.row - 1) % self.rows; self.draw_keyboard()
    def move_down(self):  self.row = (self.row + 1) % self.rows; self.draw_keyboard()
    def move_left(self):  self.col = (self.col - 1) % self.cols; self.draw_keyboard()
    def move_right(self): self.col = (self.col + 1) % self.cols; self.draw_keyboard()

    def select_key(self):
        key = self.keys[self.row][self.col]
        if key == "<":  # Backspace
            self.text = self.text[:-1]
        elif key == "-":  # Placeholder (empty slot)
            return
        elif key == " ":  # Space
            self.text += " "
        else:
            self.text += key
        self.draw_text()
        self.draw_keyboard()


# --- Usage ---
def run_keyboard():
    kb = Keyboard()
    print("Keyboard started. Type with buttons.")
    while True:
        buttons.poll()  # poll button events continuously
