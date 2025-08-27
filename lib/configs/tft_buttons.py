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
ENCODER_A_PIN = 4  # GPIO4 - Phase A output of rotary encoder
ENCODER_B_PIN = 5  # GPIO5 - Phase B output of rotary encoder
ENCODER_BUTTON_PIN = 0  # GPIO0 - Push button integrated with rotary encoder

# Physical Button Pins
USER_BUTTON_PIN = 6  # GPIO6 - General purpose user button
PWR_EN_PIN = 15  # GPIO15 - Power enable/control button


# =============================================================================
# HARDWARE INITIALIZATION
# =============================================================================

# Initialize rotary encoder hardware pins
encoder_a = Pin(ENCODER_A_PIN, Pin.IN, Pin.PULL_UP)  # Encoder phase A input
encoder_b = Pin(ENCODER_B_PIN, Pin.IN, Pin.PULL_UP)  # Encoder phase B input
encoder_button = Pin(ENCODER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)  # Encoder button

# Initialize physical buttons
user_button = Pin(USER_BUTTON_PIN, Pin.IN, Pin.PULL_UP)  # User button input
pwr_button = Pin(PWR_EN_PIN, Pin.IN, Pin.PULL_UP)  # Power button input

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

    def __init__(self):
        """
        Initialize the rotary encoder with specified pins.

        ATTRIBUTES:
            pin_a (Pin): Phase A output pin
            pin_b (Pin): Phase B output pin
            pin_button (Pin): Integrated button pin
        """
        self.pin_a = pin_a = encoder_a
        self.pin_b = pin_b = encoder_b
        self.pin_button = pin_button = encoder_button

        # Initialize state tracking variables
        self.last_a_state = pin_a.value()  # Store initial state of phase A
        self.last_b_state = pin_b.value()  # Store initial state of phase B
        self.last_button_state = pin_button.value()  # Store initial button state
        self.counter = 0  # Tracks net rotation steps
        self.button_pressed = False  # Flag for button press detection
        self.last_interrupt_time = 0  # Timestamp for debouncing

        # Set up interrupt handlers for responsive input
        self.pin_a.irq(
            trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.encoder_handler
        )
        
        self.pin_button.irq(trigger=Pin.IRQ_FALLING, handler=self.button_handler)

    def encoder_handler(self, pin):
        """
        Interrupt handler for encoder rotation detection.

        Uses quadrature encoding logic to determine rotation direction.
        Triggers on both pin A and B changes for better resolution.

        Args:
            pin (Pin): The pin that triggered the interrupt
        """
        current_time = time.ticks_ms()

        # Debounce - prevent false triggers from electrical noise
        if time.ticks_diff(current_time, self.last_interrupt_time) < 2:
            return

        self.last_interrupt_time = current_time

        # Quadrature encoding logic:
        # When A changes from 0->1 (rising edge):
        #   - If B=0, rotation is clockwise
        #   - If B=1, rotation is counter-clockwise
        # When A changes from 1->0 (falling edge):
        #   - If B=1, rotation is clockwise
        #   - If B=0, rotation is counter-clockwise

        # Only handle pin A interrupts for simplicity
        if pin == self.pin_a:
            # Read current states
            a_state = self.pin_a.value()
            b_state = self.pin_b.value()

            # Simple quadrature logic: when A changes, check B state
            if a_state != self.last_a_state:
                if (a_state == 1 and b_state == 0) or (a_state == 0 and b_state == 1):
                    self.counter += 1  # Clockwise
                else:
                    self.counter -= 1  # Counter-clockwise

                self.last_a_state = a_state


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
        Get the accumulated rotation steps since last call
        and reset counter.

        Returns:
            int: Number of steps rotated (positive = clockwise, negative = counter-clockwise)
                 0 if no rotation occurred
        """
        value = self.counter  # Store current counter value
        self.counter = 0  # Reset counter for next reading
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
            "encoder": encoder_button,  # Rotary encoder integrated button
            "user": user_button,  # General purpose user button
            "power": pwr_button,  # Power control button
        }

        self.long_press_time = 2000 # ms
        self.press_events = []  # Stores raw press events for processing
        self.time_counter = 0 # time based counter
                
        # Setup hardware interrupts for all buttons
        for name, button in self.buttons.items():
            # Configure interrupt to trigger on both press and release
            # Pin.IRQ_FALLING: Trigger when button is pressed (HIGH → LOW)
            # Pin.IRQ_RISING: Trigger when button is released (LOW → HIGH)
            button.irq(
                trigger=Pin.IRQ_FALLING | Pin.IRQ_RISING, 
                handler=lambda p, n=name: self._button_handler(p, n)
            )
            
    def _button_handler(self, pin, name):
        """
        Interrupt Service Routine (ISR) - Called automatically on button state changes.
        This function must be fast and non-blocking.
        
        Args:
            pin: The pin object that triggered the interrupt
            name: The name of the button from the buttons dictionary
        """
        current_state = pin.value()
        start_time_ms = time.ticks_ms()
        if current_state == 0:  # Falling edge - button pressed
            # Record press start time with millisecond precision
            if len(self.press_events) >= 5: # check list length
                self.press_events = self.press_events[1:5]
            self.press_events.insert(0, ('press_start', name, start_time_ms))

        else:  # Rising edge - button released
            # Find the matching press_start event for this button
            # Calculate press duration  
            for i, (event_type, btn_name, timestamp) in enumerate(self.press_events):
                if event_type == 'press_start' and btn_name == name:
                    end_time_ms = time.ticks_ms()
                    duration = time.ticks_diff(end_time_ms, timestamp)
                    # Record press end with duration
                    self.press_events.insert(0, ('press_end', name, duration))
                    break  # Only process the most recent press start
        
    def get_events(self):
        """
        Process accumulated button events and return completed press actions.
        This should be called regularly from the main program loop.
        
        Returns:
            list: List of tuples containing completed button events
            Format: [(event_type, button_name, duration_ms), ...]
            Event types: 'short_press' or 'long_press'
        """
        events = []  # Completed events to return
        new_events = []  # Ongoing events to keep for next call
        
        # Process all accumulated events
        for event in self.press_events:
            if event[0] == 'press_end':
                # This is a completed press event
                event_type = 'long_press' if event[2] >= self.long_press_time else 'short_press'
                events.append((event_type, event[1], event[2]))
            else:
                # This is an ongoing press, keep it for future processing
                new_events.append(event)
        
        # Update the events list, keeping only ongoing presses
        self.press_events = new_events
        return events

 
# =============================================================================
# ADVANCED BUTTON MANAGER CLASS
# =============================================================================


class AdvancedButtonManager:
    """
    A unified manager for handling both button presses and rotary encoder events with callback support.

    This class simplifies input handling by providing a clean interface to register callback functions for different types of events from buttons and rotary encoders. It coordinates between lower-level ButtonManager and RotaryEncoder instances to provide a unified event system.

    Attributes:
        button_callbacks (dict): A nested dictionary storing callback functions for button events. Organized by button type ('encoder', 'user', 'power') and press duration('short', 'long').

        encoder_callbacks (dict): Dictionary storing callback functions for encoder rotation events ('clockwise' and 'counterclockwise').

        button (ButtonManager): The underlying button manager instance for handling button inputs. 
        
        encoder (RotaryEncoder): The underlying rotary encoder instance for handling rotation inputs.
    """

    def __init__(self, encoder_manager: RotaryEncoder, button_manager: ButtonManager):
        """Initialize the advanced button manager with callback structures."""

        self.button_callbacks = {
            "encoder": {"short": None, "long": None},  # Encoder button callbacks
            "user": {"short": None, "long": None},  # User button callbacks
            "power": {"short": None, "long": None},  # Power button callbacks
        }

        self.encoder_callbacks = {
            "clockwise": None,  # Clockwise rotation callback
            "counterclockwise": None,  # Counter-clockwise rotation callback
        }

        # Initialize the lower-level managers
        self.button_manager = button_manager
        self.encoder = encoder_manager
        

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
        if press_type not in ["short", "long"]:
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
        if direction not in ["clockwise", "counterclockwise"]:
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
        if rotation > 0 and self.encoder_callbacks["clockwise"]:
            self.encoder_callbacks["clockwise"](rotation)  # Call clockwise callback
        elif rotation < 0 and self.encoder_callbacks["counterclockwise"]:
            self.encoder_callbacks["counterclockwise"](
                abs(rotation)
            )  # Call counter-clockwise callback

        # Handle encoder button
        if self.encoder.get_button():
            if self.button_callbacks["encoder"]["short"]:
                self.button_callbacks["encoder"][
                    "short"
                ]()  # Call encoder button callback
 
        # Handle other buttons
        events = self.button_manager.get_events()
        for event_type, button_name, duration in events: 
            print(f"{event_type:12} on {button_name:8}: {duration:4}ms")
            if event_type == "long_press": 
                long_press_callback = self.button_callbacks[button_name]["long"]
                if long_press_callback: 
                    long_press_callback()
            elif event_type == "short_press":
                short_press_callback = self.button_callbacks[button_name]["short"]
                if short_press_callback: 
                    short_press_callback()
            
             

      
            
