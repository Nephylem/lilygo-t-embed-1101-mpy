from lib.configs.tft_buttons import ButtonManager, RotaryEncoder, AdvancedButtonManager
from core.display.base import DisplayManager


class Screen:

    _components:list = [] 

    button = ButtonManager()
    encoder = RotaryEncoder()
    button_manager = AdvancedButtonManager(button_manager=button, encoder_manager=encoder)
    
    rotation = 3
    title = ""
    display = DisplayManager(rotation=rotation)
    focus_counter = 1
    def __init__(self):
        self.focused_component = None
        self.setup_input_handlers()

    def __repr__(self):
        attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
    
    @classmethod
    def focus_cycle(cls, max):
        counter = cls.focus_counter
        if counter >= max: 
            cls.focus_counter = 0
        cls.focus_counter += 1

    @classmethod
    def get_focused_component(cls) -> any | None:
        """Checks UI component attached to the screen."""
        for component in cls._components:
            if component.focused:
                return component
        return None
 
    @classmethod
    def draw(cls, clear=False):
        """Draw the screen and all components."""

        if clear:
            cls.display.clear()

        # Draw title if present
        if cls.title:
            title_x = (cls.display.width - cls.display.get_text_width(cls.title)) // 2
            cls.display.draw_text(cls.title, title_x, 5, 
                                     cls.display.WHITE, cls.display.BLACK)
        # Draw all components
        for component in cls._components:
            if component.dirty or component.focused:
                component.draw()

    @classmethod
    def update(cls):
        """Update screen and handle input."""
        cls.button_manager.update()
        
        # Check if any components need redrawing
        needs_redraw = any(component.dirty for component in cls._components)
        if needs_redraw:
            cls.draw()

    @classmethod
    def set_title(cls, text): 
        cls.title = text

    def add_component(self, component):
        """Add a UI component to the screen."""
        if isinstance(component, list): 
            self._components.extend(component)
            if self.focused_component is None: 
                self.set_focus(component[0])
                return
            
        self._components.append(component)
        if self.focused_component is None:
            self.set_focus(component)

    def setup_input_handlers(self):
        """Setup input event handlers in a concise, extensible way."""
        
        # Encoder events
        encoder_callbacks = {
            'clockwise': self.handle_encoder_clockwise,
            'counterclockwise': self.handle_encoder_counterclockwise,
        }
        for direction, handler in encoder_callbacks.items():
            self.button_manager.set_encoder_callback(direction, handler)

        # Button events
        button_callbacks = {
            ('encoder', 'short'): self.handle_encoder_button,
            ('encoder', 'long'): self.handle_encoder_button_long,
            ('user', 'short'): self.handle_user_button,
            ('user', 'long'): self.handle_user_button_long,
            ('power', 'short'): self.handle_power_button,
        }
        for (btn, press), handler in button_callbacks.items():
            self.button_manager.set_button_callback(btn, press, handler)

    def set_focus(self, component:any):
        if self.focused_component:
            self.focused_component.set_focus(False)
        
        self.focused_component = component
        if component: 
            component.set_focus(True)

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
    
    def handle_encoder_button_long(self):
        """Handle encoder button press."""
        if self.focused_component:
            self.focused_component.handle_button_press('encoder', 'long')
    
    def handle_user_button(self):
        """Handle user button press. Override in subclasses."""
        try:
            focused_component = self.get_focused_component()
            threshold = max([comp.uid for comp in self._components])
            self.focus_cycle(max=threshold)
            next_component = [comp for comp in self._components if comp.uid == self.focus_counter]
            next_comp = next_component.pop()
            if next_comp != focused_component:
                focused_component.set_focus(False)
                self.set_focus(next_comp)
                
        except Exception as e:
            print(e)
    
    def handle_user_button_long(self):
        """Handle user button press. Override in subclasses."""
        pass

        
    def handle_power_button(self):
        """Handle power button press. Override in subclasses."""
        pass