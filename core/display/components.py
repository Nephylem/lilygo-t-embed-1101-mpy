"""
ST7789 UI Framework for MicroPython
Provides comprehensive UI components for TFT display applications

Dependencies:
- st7789py.py (ST7789 display driver)
- vga1_8x8.py (Default font)
- tft_config.py (Display configuration)
- tft_buttons.py (Button and encoder handling)
"""

from lib import st7789py as st7789
from lib.fonts import vga1_8x8
from lib.configs import tft_config
from lib.configs.tft_buttons import AdvancedButtonManager, ButtonManager, RotaryEncoder
import time

# =============================================================================
# DISPLAY MANAGER CLASS
# =============================================================================

class DisplayManager:
    """
    Manages the TFT display and provides drawing utilities.
    
    This class serves as the main interface to the ST7789 display driver,
    providing convenient methods for drawing shapes, text, and managing
    display operations.
    """
    
    def __init__(self, rotation=0):
        """
        Initialize the display manager.
        
        Args:
            rotation (int): Display rotation (0-3)
        """
        self.display = tft_config.config(rotation)
        self.width = self.display.width
        self.height = self.display.height
        self.font = vga1_8x8
        
        # Color constants from st7789py
        self.BLACK = st7789.BLACK
        self.BLUE = st7789.BLUE
        self.RED = st7789.RED
        self.GREEN = st7789.GREEN
        self.CYAN = st7789.CYAN
        self.MAGENTA = st7789.MAGENTA
        self.YELLOW = st7789.YELLOW
        self.WHITE = st7789.WHITE
        
        # Clear display on initialization
        self.clear()
    
    def clear(self, color=None):
        """Clear the display with specified color."""
        fill_color = color if color is not None else self.BLACK
        self.display.fill(fill_color)
    
    def draw_text(self, text, x, y, color=None, bg_color=None):
        """
        Draw text at specified position.
        
        Args:
            text (str): Text to draw
            x (int): X coordinate
            y (int): Y coordinate
            color (int): Text color (default: WHITE)
            bg_color (int): Background color (default: BLACK)
        """
        text_color = color if color is not None else self.WHITE
        background = bg_color if bg_color is not None else self.BLACK
        self.display.text(self.font, text, x, y, text_color, background)
    
    def draw_rect(self, x, y, width, height, color, filled=False):
        """
        Draw a rectangle.
        
        Args:
            x (int): X coordinate
            y (int): Y coordinate
            width (int): Rectangle width
            height (int): Rectangle height
            color (int): Rectangle color
            filled (bool): Whether to fill the rectangle
        """
        if filled:
            self.display.fill_rect(x, y, width, height, color)
        else:
            self.display.rect(x, y, width, height, color)
    
    def draw_line(self, x0, y0, x1, y1, color):
        """Draw a line between two points."""
        self.display.line(x0, y0, x1, y1, color)
    
    def draw_pixel(self, x, y, color):
        """Draw a single pixel."""
        self.display.pixel(x, y, color)
    
    def get_text_width(self, text):
        """Calculate the width of text in pixels."""
        return len(text) * self.font.WIDTH
    
    def get_text_height(self):
        """Get the height of text in pixels."""
        return self.font.HEIGHT

# =============================================================================
# BASE UI COMPONENT CLASS
# =============================================================================

class UIComponent:
    """
    Base class for all UI components.
    
    Provides common functionality and interface for UI elements including
    positioning, dimensions, visibility, and basic event handling.
    """
    
    def __init__(self, display_mgr, x, y, width, height):
        """
        Initialize base UI component.
        
        Args:
            display_mgr (DisplayManager): Display manager instance
            x (int): X coordinate
            y (int): Y coordinate
            width (int): Component width
            height (int): Component height
        """
        self.display_mgr = display_mgr
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = True
        self.focused = False
        self.dirty = True  # Needs redraw
    
    def draw(self):
        """Draw the component. Override in subclasses."""
        if not self.visible:
            return
        # Base implementation - draw border
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height, 
                                  self.display_mgr.WHITE)
    
    def contains_point(self, x, y):
        """Check if point is within component bounds."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)
    
    def set_focus(self, focused):
        """Set component focus state."""
        if self.focused != focused:
            self.focused = focused
            self.dirty = True
    
    def set_visible(self, visible):
        """Set component visibility."""
        if self.visible != visible:
            self.visible = visible
            self.dirty = True
    
    def handle_encoder_rotation(self, direction, steps):
        """Handle encoder rotation. Override in subclasses."""
        pass
    
    def handle_button_press(self, button_name, press_type):
        """Handle button press. Override in subclasses."""
        pass

# =============================================================================
# BUTTON COMPONENT CLASS
# =============================================================================

class Button(UIComponent):
    """
    Clickable button UI component.
    
    Provides visual feedback for button states (normal, pressed, focused)
    and handles user interactions through button presses.
    """
    
    def __init__(self, display_mgr, x, y, width, height, text, callback=None):
        """
        Initialize button component.
        
        Args:
            display_mgr (DisplayManager): Display manager instance
            x (int): X coordinate
            y (int): Y coordinate
            width (int): Button width
            height (int): Button height
            text (str): Button text
            callback (function): Function to call when button is pressed
        """
        super().__init__(display_mgr, x, y, width, height)
        self.text = text
        self.callback = callback
        self.pressed = False
        self.border_color = display_mgr.WHITE
        self.text_color = display_mgr.WHITE
        self.bg_color = display_mgr.BLACK
        self.focus_color = display_mgr.CYAN
        self.press_color = display_mgr.YELLOW
    
    def draw(self):
        """Draw the button with current state."""
        if not self.visible:
            return
        
        # Determine colors based on state
        if self.pressed:
            border = self.press_color
            text_col = self.display_mgr.BLACK
            bg = self.press_color
        elif self.focused:
            border = self.focus_color
            text_col = self.focus_color
            bg = self.bg_color
        else:
            border = self.border_color
            text_col = self.text_color
            bg = self.bg_color
        
        # Draw button background
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height, 
                                  bg, filled=True)
        
        # Draw border
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height, border)
        
        # Center and draw text
        text_width = self.display_mgr.get_text_width(self.text)
        text_height = self.display_mgr.get_text_height()
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - text_height) // 2
        
        self.display_mgr.draw_text(self.text, text_x, text_y, text_col, bg)
        
        self.dirty = False
    
    def handle_button_press(self, button_name, press_type):
        """Handle button press events."""
        if button_name == 'encoder' and press_type == 'short':
            self.pressed = True
            self.dirty = True
            self.draw()  # Immediate visual feedback
            
            # Execute callback if provided
            if self.callback:
                self.callback()
            
            # Reset pressed state after short delay
            time.sleep_ms(100)
            self.pressed = False
            self.dirty = True

# =============================================================================
# LIST VIEW COMPONENT CLASS
# =============================================================================

class ListView(UIComponent):
    """
    Scrollable list UI component.
    
    Displays a list of items with scrolling capability using the rotary encoder.
    Supports item selection and callbacks for selection events.
    """
    
    def __init__(self, display_mgr, x, y, width, height, items=None):
        """
        Initialize list view component.
        
        Args:
            display_mgr (DisplayManager): Display manager instance
            x (int): X coordinate
            y (int): Y coordinate
            width (int): List width
            height (int): List height
            items (list): List of items to display
        """
        super().__init__(display_mgr, x, y, width, height)
        self.items = items or []
        self.selected_index = 0
        self.scroll_offset = 0
        self.item_height = display_mgr.get_text_height() + 4  # Text height + padding
        self.visible_items = height // self.item_height
        self.selection_callback = None
        
        # Colors
        self.bg_color = display_mgr.BLACK
        self.text_color = display_mgr.WHITE
        self.selected_bg = display_mgr.BLUE
        self.selected_text = display_mgr.WHITE
        self.border_color = display_mgr.WHITE
    
    def set_items(self, items):
        """Set the list items."""
        self.items = items
        self.selected_index = 0
        self.scroll_offset = 0
        self.dirty = True
    
    def set_selection_callback(self, callback):
        """Set callback for item selection."""
        self.selection_callback = callback
    
    def draw(self):
        """Draw the list view."""
        if not self.visible:
            return
        
        # Clear background
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height,
                                  self.bg_color, filled=True)
        
        # Draw border
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height,
                                  self.border_color)
        
        # Draw items
        for i in range(self.visible_items):
            item_index = self.scroll_offset + i
            if item_index >= len(self.items):
                break
            
            item_y = self.y + 2 + (i * self.item_height)
            item_text = self.items[item_index]
            
            # Check if this item is selected
            if item_index == self.selected_index:
                # Draw selection background
                self.display_mgr.draw_rect(self.x + 1, item_y, 
                                          self.width - 2, self.item_height,
                                          self.selected_bg, filled=True)
                text_color = self.selected_text
                bg_color = self.selected_bg
            else:
                text_color = self.text_color
                bg_color = self.bg_color
            
            # Draw item text
            text_x = self.x + 4
            self.display_mgr.draw_text(item_text, text_x, item_y + 2, 
                                     text_color, bg_color)
        
        self.dirty = False
    
    def handle_encoder_rotation(self, direction, steps):
        """Handle encoder rotation for scrolling."""
        print(f"ListView got rotation: {direction}, steps: {steps}")
        print(f"Current selected_index: {self.selected_index}")
        if not self.items:
            return
        
        old_selected = self.selected_index
        
        if direction == 'clockwise':
            self.selected_index = min(self.selected_index + steps, len(self.items) - 1)
        else:  # counterclockwise
            self.selected_index = max(self.selected_index - steps, 0)
        
        # Adjust scroll offset if needed
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + self.visible_items:
            self.scroll_offset = self.selected_index - self.visible_items + 1
        
        if old_selected != self.selected_index:
            self.dirty = True
    
    def handle_button_press(self, button_name, press_type):
        """Handle button press for item selection."""
        if button_name == 'encoder' and press_type == 'short':
            if self.selection_callback and 0 <= self.selected_index < len(self.items):
                self.selection_callback(self.selected_index, self.items[self.selected_index])
    
    def get_selected_item(self):
        """Get the currently selected item."""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

# =============================================================================
# TEXT INPUT COMPONENT CLASS
# =============================================================================

class TextInput(UIComponent):
    """
    Text input UI component with placeholder support.
    
    Provides text input capability with placeholder text display
    and cursor indication for active input state.
    """
    
    def __init__(self, display_mgr, x, y, width, height, placeholder=""):
        """
        Initialize text input component.
        
        Args:
            display_mgr (DisplayManager): Display manager instance
            x (int): X coordinate
            y (int): Y coordinate
            width (int): Input width
            height (int): Input height
            placeholder (str): Placeholder text
        """
        super().__init__(display_mgr, x, y, width, height)
        self.text = ""
        self.placeholder = placeholder
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.max_chars = (width - 8) // display_mgr.font.WIDTH  # Account for padding
        
        # Colors
        self.bg_color = display_mgr.BLACK
        self.text_color = display_mgr.WHITE
        self.placeholder_color = display_mgr.CYAN
        self.border_color = display_mgr.WHITE
        self.focus_border = display_mgr.YELLOW
        self.cursor_color = display_mgr.WHITE
    
    def set_text(self, text):
        """Set the input text."""
        self.text = text[:self.max_chars]
        self.dirty = True
    
    def get_text(self):
        """Get the current text."""
        return self.text
    
    def append_char(self, char):
        """Append a character to the text."""
        if len(self.text) < self.max_chars:
            self.text += char
            self.dirty = True
    
    def backspace(self):
        """Remove the last character."""
        if self.text:
            self.text = self.text[:-1]
            self.dirty = True
    
    def draw(self):
        """Draw the text input."""
        if not self.visible:
            return
        
        # Determine border color
        border = self.focus_border if self.focused else self.border_color
        
        # Clear background
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height,
                                  self.bg_color, filled=True)
        
        # Draw border
        self.display_mgr.draw_rect(self.x, self.y, self.width, self.height, border)
        
        # Calculate text position
        text_x = self.x + 4
        text_y = self.y + (self.height - self.display_mgr.get_text_height()) // 2
        
        # Draw text or placeholder
        if self.text:
            display_text = self.text
            color = self.text_color
        else:
            display_text = self.placeholder
            color = self.placeholder_color
        
        if display_text:
            self.display_mgr.draw_text(display_text, text_x, text_y, color, self.bg_color)
        
        # Draw cursor if focused and text is not empty or no placeholder
        if self.focused and (self.text or not self.placeholder):
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.cursor_blink_time) > 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink_time = current_time
                self.dirty = True
            
            if self.cursor_visible:
                cursor_x = text_x + self.display_mgr.get_text_width(self.text)
                self.display_mgr.draw_line(cursor_x, text_y, 
                                         cursor_x, text_y + self.display_mgr.get_text_height() - 1,
                                         self.cursor_color)
        
        self.dirty = False

# =============================================================================
# BASE SCREEN CLASS
# =============================================================================

class Screen:
    """
    Base class for application screens.
    
    Manages a collection of UI components and handles their rendering
    and interaction through a unified interface.
    """
    
    def __init__(self, display_mgr:DisplayManager, button_mgr:AdvancedButtonManager):
        """
        Initialize base screen.
        
        Args:
            display_mgr (DisplayManager): Display manager instance
            button_manager (AdvancedButtonManager) : Advanced button manager instance

        """
        self.button_manager = button_mgr
        self.display_mgr = display_mgr
        self.components = []
        self.focused_component = None
        self.setup_input_handlers()
        self.visible = True
        self.title = ""
        print("screen instance initiated")
    
    def setup_input_handlers(self):
        """Setup input event handlers."""
        self.button_manager.set_encoder_callback('clockwise', self.handle_encoder_clockwise)
        self.button_manager.set_encoder_callback('counterclockwise', self.handle_encoder_counterclockwise)
        self.button_manager.set_button_callback('encoder', 'short', self.handle_encoder_button)
        self.button_manager.set_button_callback('user', 'short', self.handle_user_button)
        self.button_manager.set_button_callback('power', 'short', self.handle_power_button)
    
    def add_component(self, component):
        """Add a UI component to the screen."""
        self.components.append(component)
        if self.focused_component is None:
            self.set_focus(component)
    
    def set_focus(self, component):
        """Set focus to a specific component."""
        if self.focused_component:
            self.focused_component.set_focus(False)
        
        self.focused_component = component
        if component:
            component.set_focus(True)
    
    def draw(self):
        """Draw the screen and all components."""
        if not self.visible:
            return
        
        # Clear screen
        self.display_mgr.clear()
        
        # Draw title if present
        if self.title:
            title_x = (self.display_mgr.width - self.display_mgr.get_text_width(self.title)) // 2
            self.display_mgr.draw_text(self.title, title_x, 5, 
                                     self.display_mgr.WHITE, self.display_mgr.BLACK)
        
        # Draw all components
        for component in self.components:
            if component.dirty or component.focused:
                component.draw()
    
    def update(self):
        """Update screen and handle input."""
        self.button_manager.update()
        
        # Check if any components need redrawing
        needs_redraw = any(component.dirty for component in self.components)
        if needs_redraw:
            self.draw()
    
    def handle_encoder_clockwise(self, steps):
        """Handle clockwise encoder rotation."""
        if self.focused_component:
            self.focused_component.handle_encoder_rotation('clockwise', steps)
    
    def handle_encoder_counterclockwise(self, steps):
        """Handle counter-clockwise encoder rotation."""
        if self.focused_component:
            self.focused_component.handle_encoder_rotation('counterclockwise', steps)
    
    def handle_encoder_button(self):
        """Handle encoder button press."""
        if self.focused_component:
            self.focused_component.handle_button_press('encoder', 'short')
    
    def handle_user_button(self):
        """Handle user button press. Override in subclasses."""
        pass
    
    def handle_power_button(self):
        """Handle power button press. Override in subclasses."""
        pass

# =============================================================================
# MESSAGE SCREEN CLASS
# =============================================================================

class MessageScreen(Screen):
    """
    Screen for displaying message dialogs.
    
    Shows centered messages with different background colors based on message type:
    - Info: Blue background
    - Warning: Red background  
    - Success: Green background
    """
    
    def __init__(self, display_mgr, message, msg_type="info", auto_dismiss=True):
        """
        Initialize message screen.
        
        Args:
            display_mgr (DisplayManager): Display manager instance
            message (str): Message to display
            msg_type (str): Message type ('info', 'warning', 'success')
            auto_dismiss (bool): Whether to auto-dismiss on button press
        """
        super().__init__(display_mgr)
        self.message = message
        self.msg_type = msg_type.lower()
        self.auto_dismiss = auto_dismiss
        self.dismiss_callback = None
        
        # Calculate message box dimensions
        self.padding = 16
        max_text_width = display_mgr.width - (self.padding * 2)
        
        # Word wrap the message
        self.lines = self.wrap_text(message, max_text_width // display_mgr.font.WIDTH)
        
        # Calculate box dimensions
        text_height = len(self.lines) * display_mgr.get_text_height()
        self.box_width = min(max([display_mgr.get_text_width(line) for line in self.lines]) + 32,
                            display_mgr.width - 32)
        self.box_height = text_height + 32
        
        # Center the box
        self.box_x = (display_mgr.width - self.box_width) // 2
        self.box_y = (display_mgr.height - self.box_height) // 2
        
        # Get colors based on message type
        self.bg_color, self.text_color = self.get_type_colors()
    
    def wrap_text(self, text, max_chars):
        """Wrap text to fit within specified character width."""
        if len(text) <= max_chars:
            return [text]
        
        lines = []
        words = text.split(' ')
        current_line = ''
        
        for word in words:
            if len(current_line + word + ' ') <= max_chars:
                current_line += word + ' '
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + ' '
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def get_type_colors(self):
        """Get colors based on message type."""
        if self.msg_type == 'warning':
            return self.display_mgr.RED, self.display_mgr.WHITE
        elif self.msg_type == 'success':
            return self.display_mgr.GREEN, self.display_mgr.WHITE
        else:  # info or default
            return self.display_mgr.BLUE, self.display_mgr.WHITE
    
    def set_dismiss_callback(self, callback):
        """Set callback for when message is dismissed."""
        self.dismiss_callback = callback
    
    def draw(self):
        """Draw the message screen."""
        if not self.visible:
            return
        
        # Clear screen with black
        self.display_mgr.clear(self.display_mgr.BLACK)
        
        # Draw message box background
        self.display_mgr.draw_rect(self.box_x, self.box_y, 
                                  self.box_width, self.box_height,
                                  self.bg_color, filled=True)
        
        # Draw border
        self.display_mgr.draw_rect(self.box_x, self.box_y, 
                                  self.box_width, self.box_height,
                                  self.display_mgr.WHITE)
        
        # Draw text lines
        text_start_y = self.box_y + 16
        line_height = self.display_mgr.get_text_height()
        
        for i, line in enumerate(self.lines):
            text_x = self.box_x + (self.box_width - self.display_mgr.get_text_width(line)) // 2
            text_y = text_start_y + (i * line_height)
            self.display_mgr.draw_text(line, text_x, text_y, 
                                     self.text_color, self.bg_color)
    
    def handle_encoder_button(self):
        """Handle encoder button press to dismiss."""
        if self.auto_dismiss:
            self.dismiss()
    
    def handle_user_button(self):
        """Handle user button press to dismiss."""
        if self.auto_dismiss:
            self.dismiss()
    
    def dismiss(self):
        """Dismiss the message screen."""
        self.visible = False
        if self.dismiss_callback:
            self.dismiss_callback()

# =============================================================================
# USAGE EXAMPLE
# =============================================================================

def example_usage():
    """Example of how to use the UI framework."""
    # Initialize display manager
    display = DisplayManager(rotation=3)  # Landscape mode
    
    # Initialize Button and Rotary encoder
    button_manager = ButtonManager()
    encoder = RotaryEncoder()
    advanced_button_manager = AdvancedButtonManager(button_manager=button_manager, encoder_manager=encoder)

    # Create a main screen
    main_screen = Screen(display, advanced_button_manager)
    main_screen.title = "UI Framework Demo"
    
    # Add a button
    def button_clicked():
        print("Button clicked!")
    
    btn = Button(display, 50, 50, 100, 30, "Click Me", button_clicked)
    main_screen.add_component(btn)
    
    # Add a list view
    items = ["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"]
    listview = ListView(display, 50, 90, 150, 60, items)
    
    def item_selected(index, item):
        print(f"Selected: {item}")
    
    listview.set_selection_callback(item_selected)

    main_screen.add_component(listview)
    # main_screen.set_focus(listview) 
    print(f"Focused component: {main_screen.focused_component}")

    
    # Show a message
    # msg_screen = MessageScreen(display, "Welcome to the UI Framework!", "info")
    
    # call button and rotary manager
 

    # Main loop would be:
    try:
        while True:
            main_screen.update()
            time.sleep_ms(50)
        
        # return main_screen, msg_screen
    except KeyboardInterrupt: 
        display.display.reset_write_address()

# Initialize framework
if __name__ == "__main__":
    example_usage()