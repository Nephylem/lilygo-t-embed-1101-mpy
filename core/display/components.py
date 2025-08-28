import time 
from core.display.base import DisplayManager
class UIComponent:
    """
    Base class for all UI components.
    
    Provides common functionality and interface for UI elements including
    positioning, dimensions, visibility, and basic event handling.
        
    Args:
        display (DisplayManager): Display manager instance
        x (int): X coordinate
        y (int): Y coordinate
        width (int): Component width
        height (int): Component height
    """
    
    # base required parameters
    _required = {
        "display" : DisplayManager,
        "width" : int, 
        "height" : int,
        "x" : int, 
        "y" : int
    }  
    _counter = 0

    # for typing
    display:DisplayManager = None
    height:int = 0
    width:int = 0
    x:int = 0
    y:int = 0

    callback = None

    # colors

    BLACK   = DisplayManager.BLACK
    BLUE    = DisplayManager.BLUE
    RED     = DisplayManager.RED
    GREEN   = DisplayManager.GREEN
    CYAN    = DisplayManager.CYAN
    MAGENTA = DisplayManager.MAGENTA
    YELLOW  = DisplayManager.YELLOW
    WHITE   = DisplayManager.WHITE

    # button
    border_color = MAGENTA
    text_color = WHITE
    bg_color = BLACK
    focus_color = BLUE
    press_color = YELLOW
    
    # list view
    selected_text = WHITE
    selected_bg = BLUE

    # text input
    cursor_color = WHITE
    placeholder_color = CYAN
    focus_border = YELLOW
    placeholder:str = ""

    
    def __init__(self, **kwargs):
        # UID system
        UIComponent._counter += 1 
        self.uid = UIComponent._counter
 
        # check and set required arguments
        for reqr, typr in self._required.items():
            try:
                kval = kwargs[reqr]
            except Exception as e:
                raise ValueError(f"({e}) Missing required parameters: <{reqr}>")            

            if typr == callable:
                if not callable(kval):
                    raise TypeError(f"Parameter <{reqr}> must be callable, got {type(kval)}")
            else:
                if not isinstance(kval, typr):
                    raise TypeError(f"Parameter <{reqr}> has invalid type: {type(kval)}")
      
            setattr(self, reqr, kval)
 
        self.visible = True
        self.dirty = True
        self.focused = True

    def __repr__(self):
        try:
            attrs = self.__dict__
            id = str(self.uid)
            attrs = ", ".join(f"{k}={v!r}" for k, v in attrs.items())
            return f"{self.__class__.__name__}({attrs + ", id=" + id})"
        except Exception as e:
            print(e)
 
    def set_focus(self, focused):
        """Set component focus state."""
        if self.focused != focused:
            self.focused = focused
            self.dirty = True
            self.visible = True
 
    def contains_point(self, x, y):
        """Check if point is within component bounds."""
        return (self.x <= x < self.x + self.width and 
                self.y <= y < self.y + self.height)


    def handle_encoder_rotation(self, direction, steps):
        """Handle encoder rotation. Override in subclasses."""
        pass
    
    def handle_button_press(self, button_name, press_type):
        """Handle button press. Override in subclasses."""
        pass
 
class Button(UIComponent):
    """
    Clickable button UI component.
    
    Provides visual feedback for button states (normal, pressed, focused)
    and handles user interactions through button presses.
 
    Args:
        display (Screen().display): Display manager instance
        x (int): X coordinate
        y (int): Y coordinate
        width (int): Button width
        height (int): Button height
        text (str): Button text
        callback (function - default: None): Function to call when button is pressed
    """
 
    _required = dict(UIComponent._required)
    _required.update({
        "text" : str,
        "callback" : callable
    })

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  
        self.pressed = False
  
    def draw(self):
        """Draw the button with current state."""
        if not self.visible:
            return
        
        # Determine colors based on state
        if self.pressed:
            border = self.press_color
            text_col = self.display.BLACK
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
        self.display.draw_rect(self.x, self.y, self.width, self.height, 
                                  bg, filled=True)
        
        # Draw border
        self.display.draw_rect(self.x, self.y, self.width, self.height, border)
        
        # Center and draw text
        text_width = self.display.get_text_width(self.text)
        text_height = self.display.get_text_height()
        text_x = self.x + (self.width - text_width) // 2
        text_y = self.y + (self.height - text_height) // 2
        
        self.display.draw_text(self.text, text_x, text_y, text_col, bg)
        
        self.dirty = False

    def handle_button_press(self, button_name, press_type):
        """Handle button press events."""
        if button_name == 'encoder' and press_type == 'short':
            self.pressed = True
            self.dirty = True
            self.draw()  # Immediate visual feedback
            
            # Execute callback if
            self.callback()
                        
            # Reset pressed state after short delay
            time.sleep_ms(200)
            self.pressed = False
            self.dirty = True

class ListView(UIComponent):
    """
    Scrollable list UI component.
    
    Displays a list of items with scrolling capability using the rotary encoder.
    Supports item selection and callbacks for selection events.

    Args:
        display (DisplayManager): Display manager instance
        x (int): X coordinate
        y (int): Y coordinate
        width (int): List width
        height (int): List height
        items (list): List of items to display
        callback (function - default: None): Function to call when button is pressed
        
    """
    _required = dict(UIComponent._required)
    _required.update({
        "items" : list,
        "callback" : callable
    })
    def __init__(self, **kwargs):
 
        super().__init__(**kwargs)       
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.item_height = self.display.get_text_height() + 4  # Text height + padding
        self.visible_items = self.height // self.item_height
 
    def set_items(self, items):
        """Set the list items."""
        self.items = items
        self.selected_index = 0
        self.scroll_offset = 0
        self.dirty = True
 
    def draw(self):
        """Draw the list view."""
        if not self.visible:
            return
        
        # Clear background
        self.display.draw_rect(self.x, self.y, self.width, self.height, self.bg_color, filled=True)
        
        # Draw border
        self.display.draw_rect(self.x, self.y, self.width, self.height, self.border_color)
        
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
                self.display.draw_rect(self.x + 1, item_y, 
                                          self.width - 2, self.item_height,
                                          self.selected_bg, filled=True)
                text_color = self.selected_text
                bg_color = self.selected_bg
            else:
                text_color = self.text_color
                bg_color = self.bg_color
            
            # Draw item text
            text_x = self.x + 4
            self.display.draw_text(item_text, text_x, item_y + 2, 
                                     text_color, bg_color)
        
        self.dirty = False
    
    def handle_encoder_rotation(self, direction, steps):
        """Handle encoder rotation for scrolling."""

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
            if self.callback and 0 <= self.selected_index < len(self.items):
                self.callback(self.selected_index, self.items[self.selected_index])
    
    def get_selected_item(self):
        """Get the currently selected item."""
        if 0 <= self.selected_index < len(self.items):
            return self.items[self.selected_index]
        return None

class TextInput(UIComponent):
    """
    Text input UI component with placeholder support.
    
    Provides text input capability with placeholder text display
    and cursor indication for active input state.

    Args:
        display (DisplayManager): Display manager instance
        x (int): X coordinate
        y (int): Y coordinate
        width (int): Input width
        height (int): Input height
        placeholder (str): Placeholder text
    """
    
    _required = dict(UIComponent._required)
    _required.update({
        "placeholder" : str
    })
    
    def __init__(self, **kwargs):
 
        super().__init__(**kwargs)
        self.text = ""
        self.cursor_visible = True
        self.cursor_blink_time = 0
        self.max_chars = (self.width - 8) // self.display.FONT.WIDTH  # Account for padding
 
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
        self.display.draw_rect(self.x, self.y, self.width, self.height,
                                  self.bg_color, filled=True)
        
        # Draw border
        self.display.draw_rect(self.x, self.y, self.width, self.height, border)
        
        # Calculate text position
        text_x = self.x + 4
        text_y = self.y + (self.height - self.display.get_text_height()) // 2
        
        # Draw text or placeholder
        if self.text:
            display_text = self.text
            color = self.text_color
        else:
            display_text = self.placeholder
            color = self.placeholder_color
        
        if display_text:
            self.display.draw_text(display_text, text_x, text_y, color, self.bg_color)
        
        # Draw cursor if focused and text is not empty or no placeholder
        if self.focused and (self.text or not self.placeholder):
            current_time = time.ticks_ms()
            if time.ticks_diff(current_time, self.cursor_blink_time) > 500:
                self.cursor_visible = not self.cursor_visible
                self.cursor_blink_time = current_time
                self.dirty = True
            
            if self.cursor_visible:
                cursor_x = text_x + self.display.get_text_width(self.text)
                self.display.draw_line(cursor_x, text_y, 
                                         cursor_x, text_y + self.display.get_text_height() - 1,
                                         self.cursor_color)
        
        self.dirty = False

class VirtualKeyboard:

    """
    Virtual keyboard component for text input with full character set support.
    
    Features:
    - Standard QWERTY layout with letters, numbers, and symbols
    - Caps lock functionality with visual indicator
    - Enter and Delete special keys
    - Dynamic minimal design with focused key highlighting
    - Optimized rendering with static layout calculations
    
    Display Layout (320x170):
    - Row 0: Numbers and symbols (1-0, special chars)
    - Row 1: QWERTYUIOP
    - Row 2: ASDFGHJKL
    - Row 3: ZXCVBNM + special keys (Caps, Enter, Del)
    - Row 4: Space bar
    
    Call Stack Flow:
    User Input → handle_encoder_rotation/handle_button_press → 
    _move_selection/_activate_key → _update_target_text → draw
 
    Execution Flow:
    1. Calculate optimal layout based on display dimensions
    2. Initialize state variables
    3. Set up color scheme
    4. Position keyboard optimally on screen
    
    Args:
        display (DisplayManager): Display manager instance
        target_text_input (TextInput): Optional text input to update
 
    """
    
    # Static keyboard layout definition - computed once at class level
    _LAYOUT = [
        # Row 0: Numbers and top symbols
        ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', 'DEL'],
        # Row 1: QWERTY top row  
        ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
        # Row 2: ASDF middle row
        ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'CAPS'],
        # Row 3: ZXCV bottom row + special keys
        ['z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/'],
        # Row 4: Space and Enter
        ['SPACE', 'ENTER']
    ]
    
    # Symbol mappings for shift state (caps lock affects symbols too)
    _SHIFT_MAP = {
        '1': '!', '2': '@', '3': '#', '4': ',', '5': '%',
        '6': '^', '7': '&', '8': '*', '9': '(', '0': ')',
        '-': '_', '=': '+', '[': '{', ']': '}', ';': ':',
        "'": '"', ',': '<', '.': '>', '/': '?'
    }
 
    @classmethod
    def _calculate_layout_metrics(cls, display_width, display_height, font_width, font_height):
        """
        Pre-calculate keyboard layout metrics for optimal performance.
        Called once during initialization to avoid repeated calculations.
        
        Args:
            display_width (int): Display width in pixels
            display_height (int): Display height in pixels  
            font_width (int): Font character width
            font_height (int): Font character height
            
        Returns:
            dict: Layout metrics including key dimensions and positions
        """
        # Reserve space for margins and padding
        margin_x = 4
        margin_y = 4
        key_padding = 2
        
        # Calculate available space
        available_width = display_width - (2 * margin_x)
        available_height = display_height - (2 * margin_y)
        
        # Calculate key dimensions based on longest row (row 0 with 12 keys)
        max_keys_per_row = max(len(row) for row in cls._LAYOUT)
        key_width = (available_width - ((max_keys_per_row + 1) * key_padding)) // max_keys_per_row
        key_height = font_height + 6  # Text height + padding
        
        # Calculate row positioning
        total_rows = len(cls._LAYOUT)
        row_height = key_height + key_padding
        total_keyboard_height = (total_rows * row_height) - key_padding
        
        # Center vertically if space available
        start_y = margin_y + max(0, (available_height - total_keyboard_height) // 2)
        
        return {
            'key_width': key_width,
            'key_height': key_height,
            'key_padding': key_padding,
            'margin_x': margin_x,
            'start_y': start_y,
            'row_height': row_height
        }
    
    def __init__(self, display:DisplayManager, text_input:TextInput):
 
        self.display = display
        self.width = display.width
        self.height = display.height
        
        # Calculate layout metrics once during initialization
        self.metrics = self._calculate_layout_metrics(
            self.width, self.height,
            self.display.FONT.WIDTH, self.display.FONT.HEIGHT
        )

        # Keyboard state
        self.visible  = True
        self.dirty = True
        self.focused = True

        self.selected_row = 0
        self.selected_col = 0
        self.caps_lock = False
        self.target_text_input = text_input
        
        # Color scheme - minimal and clean
        self.bg_color = self.display.BLACK
        self.key_color = self.display.WHITE
        self.key_bg = self.display.BLACK
        self.focused_key_bg = self.display.WHITE
        self.focused_key_text = self.display.BLACK
        self.special_key_color = self.display.CYAN
        self.caps_active_color = self.display.YELLOW
        
        # Pre-calculate all key positions for performance
        self._key_positions = self._calculate_key_positions()
        
 
    def _calculate_key_positions(self):
        """
        Pre-calculate screen positions for all keys to optimize rendering.
        
        Returns:
            list: 2D array of (x, y, width) tuples for each key position
        """
        positions = []
        metrics = self.metrics
        print(metrics)
        for row_idx, row in enumerate(self._LAYOUT):
            row_positions = []
            current_y = metrics['start_y'] + (row_idx * metrics['row_height'])
            
            # Handle special row layouts
            # if row_idx == 4:  # Space/Enter row - wider keys
            #     space_width = self.width // 8 - metrics['key_padding']
            #     enter_width = self.width // 8 - metrics['key_padding']
                
            #     row_positions.append((metrics['margin_x'], current_y, space_width))
            #     row_positions.append((metrics['margin_x'] + space_width + metrics['key_padding'], 
            #                         current_y, enter_width))
            # else:
                # Calculate row width and center it
            row_width = len(row) * metrics['key_width'] + (len(row) - 1) * metrics['key_padding']
            start_x = metrics['margin_x'] + (self.width - 2 * metrics['margin_x'] - row_width) // 2
            
            for col_idx, key in enumerate(row):
                key_x = start_x + col_idx * (metrics['key_width'] + metrics['key_padding'])
                key_width = metrics['key_width']
                
                # Special key width adjustments
                if key in ['CAPS', 'DEL']:
                    key_width = int(metrics['key_width'] * 1.2)
                
                row_positions.append((key_x, current_y, key_width))
            print(row_positions)
            positions.append(row_positions)
        
        return positions
    
    def _get_key_char(self, row, col):
        """
        Get the character for a key at given position, accounting for caps lock.
        
        Args:
            row (int): Row index
            col (int): Column index
            
        Returns:
            str: Character to display/input
        """
        if row >= len(self._LAYOUT) or col >= len(self._LAYOUT[row]):
            return ''
        
        key = self._LAYOUT[row][col]
        
        # Handle special keys
        if key in ['CAPS', 'DEL', 'ENTER', 'SPACE']:
            return key
        
        # Apply caps lock to letters
        if key.isalpha():
            return key.upper() if self.caps_lock else key
        
        # Apply shift to symbols if caps lock is on
        if self.caps_lock and key in self._SHIFT_MAP:
            return self._SHIFT_MAP[key]
        
        return key
    
    def _move_selection(self, direction):
        """
        Move keyboard selection in specified direction with boundary checking.
        
        Call Stack: handle_encoder_rotation → _move_selection → draw
        
        Args:
            direction (str): Movement direction ('up', 'down', 'left', 'right')
        """
        old_row, old_col = self.selected_row, self.selected_col
        
        if direction == 'up':
            self.selected_row = max(0, self.selected_row - 1)
            # Adjust column if new row has fewer keys
            if self.selected_col >= len(self._LAYOUT[self.selected_row]):
                self.selected_col = len(self._LAYOUT[self.selected_row]) - 1
                
        elif direction == 'down':
            self.selected_row = min(len(self._LAYOUT) - 1, self.selected_row + 1)
            # Adjust column if new row has fewer keys
            if self.selected_col >= len(self._LAYOUT[self.selected_row]):
                self.selected_col = len(self._LAYOUT[self.selected_row]) - 1
                
        elif direction == 'left':
            if self.selected_col > 0:
                self.selected_col -= 1
            else:
                # Wrap to end of previous row
                if self.selected_row > 0:
                    self.selected_row -= 1
                    self.selected_col = len(self._LAYOUT[self.selected_row]) - 1
                    
        elif direction == 'right':
            if self.selected_col < len(self._LAYOUT[self.selected_row]) - 1:
                self.selected_col += 1
            else:
                # Wrap to start of next row
                if self.selected_row < len(self._LAYOUT) - 1:
                    self.selected_row += 1
                    self.selected_col = 0
        
        # Mark for redraw if selection changed
        if (old_row, old_col) != (self.selected_row, self.selected_col):
            self.dirty = True
    
    def _activate_key(self):
        """
        Activate the currently selected key.
        
        Call Stack: handle_button_press → _activate_key → _update_target_text
        
        Handles special keys (CAPS, DEL, ENTER, SPACE) and regular character input.
        """
        key = self._get_key_char(self.selected_row, self.selected_col)
        
        if key == 'CAPS':
            self.caps_lock = not self.caps_lock
            self.dirty = True
        elif key == 'DEL':
            self._update_target_text('BACKSPACE')
        elif key == 'ENTER':
            self._update_target_text('ENTER')
        elif key == 'SPACE':
            self._update_target_text(' ')
        elif key and key not in ['CAPS', 'DEL', 'ENTER', 'SPACE']:
            self._update_target_text(key)
    
    def _update_target_text(self, char_or_action):
        """
        Update the target text input with character or action.
        
        Args:
            char_or_action (str): Character to add or action ('BACKSPACE', 'ENTER')
        """
        if not self.target_text_input:
            return
        
        if char_or_action == 'BACKSPACE':
            self.target_text_input.backspace()
        elif char_or_action == 'ENTER':
            # Could trigger submission or newline depending on implementation
            pass
        else:
            self.target_text_input.append_char(char_or_action)
    
    def draw(self):
        """
        Render the virtual keyboard with current state.
        
        Call Stack: Screen.draw → VirtualKeyboard.draw
        
        Optimization: Only redraws when dirty flag is set.
        """
        if not self.visible or not self.dirty:
            return
        
        # Clear background
        self.display.clear(self.bg_color)
        
        # Draw all keys
        for row_idx, row in enumerate(self._LAYOUT):
            for col_idx, key in enumerate(row):
                self._draw_key(row_idx, col_idx)
        
        self.dirty = False
    
    def _draw_key(self, row, col):
        """
        Draw individual key with appropriate styling.
        
        Args:
            row (int): Key row index
            col (int): Key column index
        """
        if row >= len(self._key_positions) or col >= len(self._key_positions[row]):
            return
        
        key_x, key_y, key_width = self._key_positions[row][col]
        key_height = self.metrics['key_height']
        key_char = self._get_key_char(row, col)
        
        # Determine key styling
        is_selected = (row == self.selected_row and col == self.selected_col)
        is_caps = (key_char == 'CAPS')
        is_special = key_char in ['DEL', 'ENTER', 'SPACE']
        
        # Key colors
        if is_selected:
            bg_color = self.focused_key_bg
            text_color = self.focused_key_text
            border_color = self.focused_key_bg
        elif is_caps and self.caps_lock:
            bg_color = self.key_bg
            text_color = self.caps_active_color
            border_color = self.caps_active_color
        elif is_special:
            bg_color = self.key_bg
            text_color = self.special_key_color
            border_color = self.special_key_color
        else:
            bg_color = self.key_bg
            text_color = self.key_color
            border_color = self.key_color
        
        # Draw key background
        self.display.draw_rect(key_x, key_y, key_width, key_height, 
                                  bg_color, filled=True)
        
        # Draw key border
        self.display.draw_rect(key_x, key_y, key_width, key_height, border_color)
        
        # Draw key text - handle special key labels
        display_text = self._get_display_text(key_char)
        text_width = self.display.get_text_width(display_text)
        text_height = self.display.get_text_height()
        
        text_x = key_x + (key_width - text_width) // 2
        text_y = key_y + (key_height - text_height) // 2
        
        self.display.draw_text(display_text, text_x, text_y, text_color, bg_color)
    
    def _get_display_text(self, key_char):
        """
        Get display text for key labels.
        
        Args:
            key_char (str): Key character
            
        Returns:
            str: Text to display on key
        """
        if key_char == 'SPACE':
            return 'SPC'
        elif key_char == 'ENTER':
            return 'ENT'
        elif key_char == 'DEL':
            return 'DEL'
        elif key_char == 'CAPS':
            return 'CAP'
        else:
            return key_char
    
    def handle_encoder_rotation(self, direction, steps):
        """
        Handle encoder rotation for keyboard navigation.
        
        Call Stack: Screen input handler → handle_encoder_rotation → _move_selection
        
        Args:
            direction (str): Rotation direction ('clockwise' or 'counterclockwise')
            steps (int): Number of steps rotated
        """
        # Map rotation to movement - treat each step as one movement
        for _ in range(steps):
            if direction == 'clockwise':
                self._move_selection('right')
            else:
                self._move_selection('left')
    
    def handle_button_press(self, button_name, press_type):
        """
        Handle button presses for key activation and navigation.
        
        Call Stack: Screen input handler → handle_button_press → _activate_key
        
        Args:
            button_name (str): Name of pressed button
            press_type (str): Type of press ('short' or 'long')
        """
        if button_name == 'encoder' and press_type == 'short':
            self._activate_key()
        elif button_name == 'user' and press_type == 'short':
            # User button for vertical navigation
            self._move_selection('down')
    
    def set_target_text_input(self, text_input):
        """
        Set the target text input component.
        
        Args:
            text_input (TextInput): Text input component to update
        """
        self.target_text_input = text_input

    def set_focus(self, focused):
        """Set component focus state."""
        if self.focused != focused:
            self.focused = focused
            self.dirty = True
            self.visible = True