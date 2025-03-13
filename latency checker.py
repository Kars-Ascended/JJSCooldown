# I USE THIS TO TIME THE INPUT TO THE ACTUAL COOLDOWN START OF A MOVE (for example todo clap active to todo actually swapping)

from pynput import keyboard
import time

last_press_time = None

def on_press(key):
    global last_press_time
    
    try:
        if key.char == 'r' or key.char == 'R':
            current_time = time.time()
            
            if last_press_time is not None:
                time_diff = current_time - last_press_time
                print(f"Time between R presses: {time_diff:.2f} seconds")
            
            last_press_time = current_time
            
    except AttributeError:
        pass

def on_release(key):
    if key == keyboard.Key.esc:
        return False

# Set up the listener
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    print("Press 'R' to measure time between presses. Press 'ESC' to exit.")
    listener.join()