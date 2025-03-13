import tkinter as tk
from pynput import keyboard
import threading
import time

class CountdownApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Countdown Timer")
        self.root.geometry("800x350")
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)  # Remove title bar
        
        # Create canvas for progress bar
        self.canvas = tk.Canvas(self.root, height=24, width=304, highlightthickness=0)
        self.progress_bar = self.canvas.create_rectangle(0, 0, 0, 24, fill='red')
        
        # Create a frame for input elements
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)
        
        # Add description text
        description = tk.Label(
            self.input_frame,
            text="Shenanigans timer by r/Father_Enrico\n"
            "Click a character to start their cooldown timer, pressing 'R' will restart the timer\n"
            "'x bound' refers to if you want to time from when the move ends or starts\n"
            "lower = when R is pressed, upper = when the move ends\n"
            ,
            font=("Arial", 10),
            justify=tk.CENTER
        )
        description.pack(pady=5)

        # Define presets with their times and colors
        self.presets = {
            'Gojo': {'time': 15, 'color': '#02acff', 'completed_color': '#2bd5ff'}, #done
            'Yuji': {'time': 2, 'color': '#860000', 'completed_color': '#f90000'},  # color needs fixing
            'Hakari': {'time': 12.5, 'color': '#00FF00', 'completed_color': '#004400'},  # color needs fixing
            'Megumi (Lower bound)': {'time': 10, 'color': '#0000FF', 'completed_color': '#000088'},  # color needs fixing
            'Megumi (Upper bound)': {'time': 11.8, 'color': '#17262d', 'completed_color': '#0b1317'},  # color needs fixing
            'Mahito': {'time': 0.2, 'color': '#FFA500', 'completed_color': '#805200'},  # color needs fixing
            'Choso': {'time': 20, 'color': '#FFA500', 'completed_color': '#805200'},  # color needs fixing
            'Todo (Normal)': {'time': 10, 'color': '#FFA500', 'completed_color': '#805200'},  # color needs fixing
            'Todo (Perfect / Bluff)': {'time': 2, 'color': '#FFA500', 'completed_color': '#805200'},  # color needs fixing
            'Todo (Throwable)': {'time': 5, 'color': '#FFA500', 'completed_color': '#805200'},  # color needs fixing
            'Higuruma (NOT ADDED YET)': {'time': 2, 'color': '#FFA500', 'completed_color': '#805200'},  # color needs fixing
            'Locust': {'time': 10, 'color': '#FFA500', 'completed_color': '#805200'}  # color needs fixing
        }
        
        # Create buttons frame instead of input field
        self.buttons_frame = tk.Frame(self.input_frame)
        self.buttons_frame.pack(pady=5)
        
        # Calculate max width based on longest preset name
        max_width = max(len(name) for name in self.presets.keys())
        
        # Create preset buttons
        for i, (preset_name, preset_data) in enumerate(self.presets.items()):
            row = i // 4  # Integer division to determine row
            col = i % 4   # Modulo to determine column
            btn = tk.Button(
                self.buttons_frame, 
                text=preset_name,
                width=max_width,  # Set fixed width for all buttons
                command=lambda t=preset_data['time'], c=preset_data['color']: self.start_countdown(t, c)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)  # Using grid instead of pack
        
        # Label for countdown with click and drag binding
        self.label = tk.Label(self.root, text="Select preset timer", font=("Arial", 20))
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
        
        # Add variables to store last used settings
        self.last_time = 0
        self.last_color = '#FFffff'
        self.completed_color = '#FF0000'  # Color for completed state
        
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
    
    def start_countdown(self, seconds, color):
        if not self.counting:
            self.total_seconds = seconds
            self.last_time = seconds
            self.last_color = color
            # Store the completed color for the current preset
            self.current_completed_color = self.presets[next(key for key, value in self.presets.items() if value['time'] == seconds and value['color'] == color)]['completed_color']
            self.counting = True
            self.start_time = time.time()
            self.elapsed = 0
            self.canvas.itemconfig(self.progress_bar, fill=color)
            self.countdown()

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
                self.canvas.itemconfig(self.progress_bar, fill=self.current_completed_color)

    def reset_ui(self):
        """Reset the UI to show buttons again"""
        self.canvas.pack_forget()
        self.input_frame.pack(pady=10)
        self.label.pack(pady=10)
        self.root.geometry("200x150")

    def on_press(self, key):
        try:
            if key.char == 'r' and not self.counting:
                self.start_countdown(self.last_time, self.last_color)
        except AttributeError:
            pass
    
    def on_closing(self):
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = CountdownApp()