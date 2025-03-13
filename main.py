import tkinter as tk
from pynput import keyboard
import threading
import time

class CountdownApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Countdown Timer")
        self.root.geometry("200x150")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove title bar
        
        # Create canvas for progress bar
        self.canvas = tk.Canvas(self.root, height=24, width=304, highlightthickness=0)
        self.progress_bar = self.canvas.create_rectangle(0, 0, 0, 24, fill='red')
        
        # Create a frame for input elements
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)
        
        # Input field
        self.time_entry = tk.Entry(self.input_frame)
        self.time_entry.pack(pady=10)
        
        # Label for countdown with click and drag binding
        self.label = tk.Label(self.root, text="Enter seconds\nPress 'R' to start", font=("Arial", 20))
        self.label.pack(pady=10)
        self.label.bind('<Button-1>', self.start_drag)
        self.label.bind('<B1-Motion>', self.on_drag)
        
        # Make canvas draggable too
        self.canvas.bind('<Button-1>', self.start_drag)
        self.canvas.bind('<B1-Motion>', self.on_drag)
        
        # Initialize time tracking variables
        self.counting = False
        self.seconds = 0
        self.total_seconds = 0
        self.start_time = 0
        self.elapsed = 0
        
        # Update interval for smoother animation (milliseconds)
        self.update_interval = 16  # ~60fps for smoother animation
        self.progress = 0
        
        # Setup keyboard listener
        self.listener = keyboard.Listener(on_press=self.on_press)
        self.listener.start()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def start_drag(self, event):
        self.x = event.x
        self.y = event.y

    def on_drag(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")
    
    def countdown(self):
        if self.counting:
            self.elapsed = (time.time() - self.start_time)
            remaining = self.total_seconds - self.elapsed
            
            if remaining > 0:
                # Hide input frame and show progress bar
                self.input_frame.pack_forget()
                self.label.pack_forget()
                self.canvas.pack(pady=0)
                self.root.geometry("304x24")
                
                # Calculate smooth progress
                progress_width = (self.elapsed / self.total_seconds) * 304
                self.canvas.coords(self.progress_bar, 0, 0, progress_width, 24)
                
                self.root.after(self.update_interval, self.countdown)
            else:
                # Countdown complete
                self.counting = False
                self.canvas.coords(self.progress_bar, 0, 0, 304, 24)
                self.canvas.itemconfig(self.progress_bar, fill='#00ff00')

    def on_press(self, key):
        try:
            if key.char == 'r' and not self.counting:
                try:
                    seconds = int(self.time_entry.get())
                    if seconds > 0:
                        self.total_seconds = seconds
                        self.counting = True
                        self.start_time = time.time()
                        self.elapsed = 0
                        self.canvas.itemconfig(self.progress_bar, fill='red')
                        self.countdown()
                except ValueError:
                    self.label.config(text="Enter valid number")
        except AttributeError:
            pass
    
    def on_closing(self):
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = CountdownApp()