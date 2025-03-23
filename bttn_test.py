from pynput import mouse
import time

# This function will be called when a mouse button is pressed
def on_click(x, y, button, pressed):
    if pressed:
        print(f'Button {button} pressed at ({x}, {y})')

# This function will be called when a mouse button is released
def on_release(x, y, button, pressed):
    if not pressed:
        print(f'Button {button} released at ({x}, {y})')

# Set up the listener for mouse events
with mouse.Listener(on_click=on_click, on_release=on_release) as listener:
    print("Press 'esc' to exit the test.")
    try:
        while True:
            time.sleep(0.1)  # Sleep to reduce CPU usage
    except KeyboardInterrupt:
        listener.stop()  # Stop the listener on keyboard interrupt
    except Exception as e:
        print(f"An error occurred: {e}")
        listener.stop()

print("Exiting...")