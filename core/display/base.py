from lib import st7789py as st7789
from lib.fonts import vga1_8x8
from lib.configs import tft_config
import time

class DisplayManager:
    """
    Manages the TFT display and provides drawing utilities.
    
    This class serves as the main interface to the ST7789 display driver,
    providing convenient methods for drawing shapes, text, and managing
    display operations.
    """
    
    # fonts
    FONT = vga1_8x8

    # Color constants from st7789py
    BLACK   = st7789.BLACK
    BLUE    = st7789.BLUE
    RED     = st7789.RED
    GREEN   = st7789.GREEN
    CYAN    = st7789.CYAN
    MAGENTA = st7789.MAGENTA
    YELLOW  = st7789.YELLOW
    WHITE   = st7789.WHITE
   

    def __init__(self, rotation=0):
        """
        Initialize the display manager.

        Args:
            rotation (int): Display rotation (0-3)
        """
        DisplayManager.display:st7789.ST7789 = tft_config.config(rotation=rotation)
        self.rotation = rotation
        self.width = self.display.width
        self.height = self.display.height

        # Clear display on initialization
        self.display.reset_write_address()
    
    def __repr__(self): 
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
 
    @classmethod
    def clear(cls, color=None):
        """Clear the display with specified color."""
        fill_color = color if color is not None else cls.BLACK
        cls.display.fill(fill_color)

    @classmethod
    def draw_text(cls, text, x, y, color=None, bg_color=None):
        """Draw text at specified position."""
        text_color = color if color is not None else cls.WHITE
        background = bg_color if bg_color is not None else cls.BLACK
        cls.display.text(cls.FONT, text, x, y, text_color, background)

    @classmethod
    def draw_rect(cls, x, y, width, height, color, filled=False):
        """Draw a rectangle."""
        if filled:
            cls.display.fill_rect(x, y, width, height, color)
        else:
            cls.display.rect(x, y, width, height, color)

    @classmethod
    def draw_line(cls, x0, y0, x1, y1, color):
        """Draw a line between two points."""
        cls.display.line(x0, y0, x1, y1, color)

    @classmethod
    def draw_pixel(cls, x, y, color):
        """Draw a single pixel."""
        cls.display.pixel(x, y, color)

    @classmethod
    def get_text_width(cls, text):
        """Calculate the width of text in pixels."""
        return len(text) * cls.FONT.WIDTH
    
    @classmethod
    def get_text_height(cls):
        """Get the height of text in pixels."""
        return cls.FONT.HEIGHT