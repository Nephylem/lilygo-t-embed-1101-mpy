from machine import Pin

# Button / Encoder pin mapping for LilyGo T-Embed
PIN_CLK = 4   # Encoder A
PIN_DT  = 5   # Encoder B
PIN_SW  = 0   # Encoder push button
PIN_TOP = 6   # Top button above encoder

class Input:
    """
    Input mapping for LilyGo T-Embed CC1101
    - Rotary encoder rotation (GPIO4, GPIO5) = left/right
    - Encoder push (GPIO0) = ok
    - Top button (GPIO6)   = back
    """

    def __init__(self, pin_clk=PIN_CLK, pin_dt=PIN_DT, pin_sw=PIN_SW, pin_top=PIN_TOP):
        self.name = "t-embed"

        # Rotary encoder pins
        self.clk = Pin(pin_clk, Pin.IN, Pin.PULL_UP)
        self.dt  = Pin(pin_dt, Pin.IN, Pin.PULL_UP)

        # Buttons
        self.sw  = Pin(pin_sw, Pin.IN, Pin.PULL_UP)   # encoder push
        self.top = Pin(pin_top, Pin.IN, Pin.PULL_UP)  # top button

        # State tracking
        self.last_clk = self.clk.value()
        self.last_top = self.top.value()

    def get_event(self):
        """
        Poll inputs and return events:
        "left", "right", "ok", "back", or None
        """
        event = None

        # --- Encoder rotation detection (quadrature) ---
        clk_val = self.clk.value()
        dt_val = self.dt.value()

        if clk_val != self.last_clk:  # edge detected
            if dt_val != clk_val:
                event = "right"   # CW
            else:
                event = "left"    # CCW
        self.last_clk = clk_val

        # --- Encoder push (GPIO0) ---
        if self.sw.value() == 0:   # active low
            event = "ok"

        # --- Top button (GPIO6) ---
        if self.top.value() == 0 and self.last_top == 1:
            event = "back"
        self.last_top = self.top.value()

        return event
