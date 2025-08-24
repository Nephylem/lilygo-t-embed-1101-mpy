"""
rotary.py - Rotary Encoder and Button Management for LilyGo T-Embed

This module provides classes to handle rotary encoder input and button management
for the LilyGo T-Embed development board with MicroPython.

Features:
- Rotary encoder rotation detection with debouncing
- Button press detection with short/long press differentiation
- Callback-based event handling system
- Hardware abstraction for easy integration

Author: Nephy
Date: 2024
Version: 1.0
"""

from machine import Pin, SPI
import time

# =============================================================================
# HARDWARE PIN DEFINITIONS
# =============================================================================

# Rotary Encoder Pins (from official LilyGo T-Embed documentation)
ENCODER_A_PIN = 4    # GPIO4 - Phase A output of rotary encoder
ENCODER_B_PIN = 5    # GPIO5 - Phase B output of rotary encoder  
ENCODER_BUTTON_PIN = 0  # GPIO0 - Push button integrated with rotary encoder

# Physical Button Pins
USER_BUTTON_PIN = 6   # GPIO6 - General purpose user button
PWR_EN_PIN = 15       # GPIO15 - Power enable/control button
 

# =============================================================================
# HARDWARE INITIALIZATION
# =============================================================================

# Initialize rotary encoder hardware pins
encoder_a = Pin(ENCODER_A_PIN, Pin.IN, Pin.PULL_UP)      # Encoder phase A input
encoder_b = Pin(ENCODER_B_PIN, Pin.IN, Pin.PULL_UP)      # Encoder phase B input
encoder_button = Pin(ENCODER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)  # Encoder button

# Initialize physical buttons
user_button = Pin(USER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)  # User button input
pwr_button = Pin(PWR_EN_PIN, Pin.IN, Pin.PULL_UP)        # Power button input
 
# =============================================================================
# ROTARY ENCODER CLASS
# =============================================================================

class RotaryEncoder:
    """
    Handles rotary encoder input including rotation detection and button press.
    
    This class uses interrupt handlers to detect encoder movements and button
    presses without the need for continuous polling, providing responsive
    input handling with built-in debouncing.
    
    Attributes:
        pin_a (Pin): Phase A output pin of the encoder
        pin_b (Pin): Phase B output pin of the encoder  
        pin_button (Pin): Encoder's integrated push button pin
        last_a_state (int): Previous state of phase A for change detection
        counter (int): Accumulated rotation steps (positive = clockwise)
        button_pressed (bool): Flag indicating if button was pressed
        last_interrupt_time (int): Timestamp for debouncing calculations
    """
    
    def __init__(self, pin_a, pin_b, pin_button):
        """
        Initialize the rotary encoder with specified pins.
        
        Args:
            pin_a (Pin): Phase A output pin
            pin_b (Pin): Phase B output pin
            pin_button (Pin): Integrated button pin
        """
        self.pin_a = pin_a
        self.pin_b = pin_b
        self.pin_button = pin_button
        
        # Initialize state tracking variables
        self.last_a_state = pin_a.value()      # Store initial state of phase A
        self.last_button_state = pin_button.value()  # Store initial button state
        self.counter = 0            # Tracks net rotation steps
        self.button_pressed = False # Flag for button press detection
        self.last_interrupt_time = 0 # Timestamp for debouncing
        
        # Set up interrupt handlers for responsive input
        self.pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.encoder_handler)
        self.pin_b.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.encoder_handler)

        self.pin_button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_handler)
    
    def encoder_handler(self, pin):
        """
        Interrupt handler for encoder rotation detection.
        
        Called whenever the phase A pin changes state. Determines rotation
        direction by comparing the states of phase A and phase B pins.
        Includes debouncing to prevent false triggers.
        
        Args:
            pin (Pin): The pin that triggered the interrupt
        """
        current_time = time.ticks_ms()
        
        if time.ticks_diff(current_time, self.last_interrupt_time) < 5:
            return
            
        self.last_interrupt_time = current_time
        
        a_state = self.pin_a.value()
        b_state = self.pin_b.value()
        
        print(f"Interrupt! A: {a_state}, B: {b_state}, Last A: {self.last_a_state}")
        
        # Check which pin changed
        if pin == self.pin_a:
            # A pin changed
            if a_state != self.last_a_state:
                if b_state != a_state:
                    self.counter += 1
                    print("Clockwise rotation detected")
                else:
                    self.counter -= 1
                    print("Counter-clockwise rotation detected")
        else:
            # B pin changed
            if b_state != self.last_b_state:
                if a_state == b_state:
                    self.counter += 1
                    print("Clockwise rotation detected")
                else:
                    self.counter -= 1
                    print("Counter-clockwise rotation detected")
        
        self.last_a_state = a_state
        self.last_b_state = b_state
        print(f"Counter: {self.counter}")
    
    def button_handler(self, pin):
        """
        Interrupt handler for encoder button press detection.
        
        Called when the encoder button is pressed. Includes debouncing
        to prevent multiple triggers from a single press.
        
        Args:
            pin (Pin): The pin that triggered the interrupt
        """
        current_time = time.ticks_ms()
        # 200ms debounce time to prevent multiple detections
        if time.ticks_diff(current_time, self.last_interrupt_time) > 200:
            self.button_pressed = True  # Set button pressed flag
            self.last_interrupt_time = current_time  # Update debounce timer
    
    def get_rotation(self):
        """
        Get the accumulated rotation steps since last call.
        
        Returns:
            int: Number of steps rotated (positive = clockwise, negative = counter-clockwise)
                 0 if no rotation occurred
        """
        value = self.counter  # Store current counter value
        self.counter = 0      # Reset counter for next reading
        return value
    
    def get_button(self):
        """
        Check if the encoder button was pressed since last call.
        
        Returns:
            bool: True if button was pressed, False otherwise
        """
        if self.button_pressed:
            self.button_pressed = False  # Reset flag after reading
            return True
        return False

# =============================================================================
# BUTTON MANAGER CLASS
# =============================================================================

class ButtonManager:
    """
    Manages all physical buttons with debouncing and press duration detection.
    
    This class handles multiple buttons, distinguishing between short
    and long presses, and provides a simple interface to check button states.
    
    Attributes:
        buttons (dict): Mapping of button names to Pin objects
        button_states (dict): Current pressed state for each button
        button_press_times (dict): Timestamp when each button was pressed
        long_press_duration (int): Duration threshold for long press in milliseconds
    """
    
    def __init__(self):
        """Initialize the button manager with all available buttons."""
        # Dictionary mapping button names to their hardware pins
        self.buttons = {
            'encoder': encoder_button,  # Rotary encoder integrated button
            'user': user_button,        # General purpose user button
            'power': pwr_button         # Power control button
        }
        
        # Initialize state tracking dictionaries
        self.button_states = {name: False for name in self.buttons}  # Pressed states
        self.button_press_times = {name: 0 for name in self.buttons}  # Press timestamps
        self.long_press_duration = 1000  # 1 second threshold for long press
        
        # Set up interrupt handlers for all buttons
        for name, button in self.buttons.items():
            button.irq(trigger=Pin.IRQ_FALLING, handler=lambda p, b=name: self._button_handler(b))
    
    def _button_handler(self, button_name):
        """
        Internal interrupt handler for button presses.
        
        Args:
            button_name (str): Name of the button that was pressed
        """
        current_time = time.ticks_ms()
        self.button_states[button_name] = True  # Mark button as pressed
        self.button_press_times[button_name] = current_time  # Record press time
    
    def get_button_press(self, button_name):
        """
        Check if a specific button was pressed and return press type.
        
        Args:
            button_name (str): Name of the button to check
            
        Returns:
            str or None: 'short' for short press, 'long' for long press,
                         None if no press detected
        """
        if self.button_states.get(button_name, False):
            current_time = time.ticks_ms()
            # Calculate how long the button was held down
            press_duration = time.ticks_diff(current_time, self.button_press_times[button_name])
            
            self.button_states[button_name] = False  # Reset button state
            
            # Determine press type based on duration
            if press_duration > self.long_press_duration:
                return 'long'   # Long press
            else:
                return 'short'  # Short press
        return None  # No press detected
    
    def check_all_buttons(self):
        """
        Check all buttons for press events.
        
        Returns:
            dict: Dictionary mapping button names to press types
                  Example: {'encoder': 'short', 'power': 'long'}
        """
        pressed_buttons = {}
        for name in self.buttons:
            press_type = self.get_button_press(name)
            if press_type:
                pressed_buttons[name] = press_type
        return pressed_buttons

# =============================================================================
# ADVANCED BUTTON MANAGER CLASS
# =============================================================================

class AdvancedButtonManager:
    """
    High-level button and encoder manager with callback support.
    
    This class provides a callback-based interface for handling input events.
    It coordinates the RotaryEncoder and ButtonManager classes and allows
    application code to register callback functions for specific events.
    
    Attributes:
        button_callbacks (dict): Nested dictionary storing callback functions
        encoder_callbacks (dict): Callback functions for encoder rotation
        button_manager (ButtonManager): Instance of ButtonManager
        encoder (RotaryEncoder): Instance of RotaryEncoder
    """
    
    def __init__(self):
        """Initialize the advanced button manager with callback structures."""
        # Initialize callback dictionaries with None values
        self.button_callbacks = {
            'encoder': {'short': None, 'long': None},  # Encoder button callbacks
            'user': {'short': None, 'long': None},     # User button callbacks  
            'power': {'short': None, 'long': None}     # Power button callbacks
        }
        
        self.encoder_callbacks = {
            'clockwise': None,        # Clockwise rotation callback
            'counterclockwise': None  # Counter-clockwise rotation callback
        }
        
        # Initialize the lower-level managers
        self.button_manager = ButtonManager()
        self.encoder = RotaryEncoder(encoder_a, encoder_b, encoder_button)
    
    def set_button_callback(self, button_name, press_type, callback):
        """
        Register a callback function for a button event.
        
        Args:
            button_name (str): Name of the button ('encoder', 'user', 'power')
            press_type (str): Type of press ('short' or 'long')
            callback (function): Function to call when event occurs
            
        Raises:
            ValueError: If button_name or press_type is invalid
        """
        if button_name not in self.button_callbacks:
            raise ValueError(f"Invalid button name: {button_name}")
        if press_type not in ['short', 'long']:
            raise ValueError(f"Invalid press type: {press_type}")
        
        self.button_callbacks[button_name][press_type] = callback
    
    def set_encoder_callback(self, direction, callback):
        """
        Register a callback function for encoder rotation.
        
        Args:
            direction (str): Rotation direction ('clockwise' or 'counterclockwise')
            callback (function): Function to call when rotation occurs
            
        Raises:
            ValueError: If direction is invalid
        """
        if direction not in ['clockwise', 'counterclockwise']:
            raise ValueError(f"Invalid direction: {direction}")
        
        self.encoder_callbacks[direction] = callback
    
    def update(self):
        """
        Check for input events and trigger appropriate callbacks.
        
        This method should be called regularly in the main application loop
        to process input events and execute registered callbacks.
        """
        # Handle encoder rotation
        rotation = self.encoder.get_rotation()
        if rotation > 0 and self.encoder_callbacks['clockwise']:
            self.encoder_callbacks['clockwise'](rotation)  # Call clockwise callback
        elif rotation < 0 and self.encoder_callbacks['counterclockwise']:
            self.encoder_callbacks['counterclockwise'](abs(rotation))  # Call counter-clockwise callback
        
        # Handle encoder button
        if self.encoder.get_button():
            if self.button_callbacks['encoder']['short']:
                self.button_callbacks['encoder']['short']()  # Call encoder button callback
        
        # Handle other buttons
        pressed = self.button_manager.check_all_buttons()
        for button, press_type in pressed.items():
            callback = self.button_callbacks.get(button, {}).get(press_type)
            if callback:
                callback()  # Execute the registered callback
 

 