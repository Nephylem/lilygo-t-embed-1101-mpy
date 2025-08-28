from core.display.screen import Screen
from core.display.components import Button, TextInput, VirtualKeyboard, UIComponent, ListView



if __name__ == "__main__":
    screen = Screen()
    component = TextInput(display=screen.display, x=10, y=10, width=300, height=20, placeholder="demo text input")
    keyboard = VirtualKeyboard(screen.display, component)
    screen.add_component([keyboard, component])
    print(screen._components)
    while True:
        screen.update()

     