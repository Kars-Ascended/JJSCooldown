import tkinter as tk
from pynput import keyboard
import threading
import time

class CountdownApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Countdown Timer")
        self.root.geometry("800x350")
        self.root.attributes('-topmost', True, '-transparentcolor', '#FFFF00')
        self.root.overrideredirect(True)  # Remove title bar
        self.root.configure(bg='#FFFF00')  # Set window background to yellow for transparency
        
        # Create canvas for progress bar with transparent background
        self.canvas = tk.Canvas(
            self.root, 
            height=24, 
            width=304, 
            highlightthickness=0,
            bg='#FFFF00'  # Set canvas background to yellow for transparency
        )
        # Create border rectangle (adjusted with extra pixel top/left)
        self.border = self.canvas.create_rectangle(1, 1, 303, 23, outline='gray', width=2)
        # Progress bar now fits inside 2px border, with extra pixel top/left
        self.progress_bar = self.canvas.create_rectangle(2, 2, 2, 21, fill='red')
        # Text element adjusted for new center
        self.text_element = self.canvas.create_text(151, 11, text="", fill="black", anchor="center", 
                                                  font=("Times New Roman", 13))
        
        # Create a frame for input elements
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)
        
        # Add description text
        description = tk.Label(
            self.input_frame,
            text="Shenanigans timer by r/Father_Enrico\n"
            "Click a character to start their cooldown timer, pressing 'R' will restart the timer\n"
            "'x bound' refers to if you want to time from when the move ends or starts\n"
            "lower = when R is pressed, upper = when the move ends. im not adding every small bound like hakari doors being hit\n"
            ,
            font=("Arial", 10),
            justify=tk.CENTER
        )
        description.pack(pady=5)

        # Define presets with their times and colors (make the main colour the average of the ult bar colours, and the completed colour the top of the ult bar)
        self.presets = {
            'Gojo': {'time': 15, 'color': '#02acff', 'completed_color': '#2bd5ff', 'text': 'Limitless'},
            'Yuji': {'time': 2, 'color': '#860000', 'completed_color': '#f90000', 'text': 'Combat Instincts'},
            'Hakari': {'time': 12.5, 'color': '#02ac7f', 'completed_color': '#53fd7f', 'text': 'Door Guard'},
            'Megumi (Lower bound)': {'time': 10, 'color': '#011e2d', 'completed_color': '#2c2d2d', 'text': 'Lurking Shadow'},  # color needs redoing
            'Megumi (Upper bound)': {'time': 11.8, 'color': '#011e2d', 'completed_color': '#2c2d2d', 'text': 'Lurking Shadow'},  # color needs redoing
            'Mahito': {'time': 0.2, 'color': '#558dff', 'completed_color': '#a6a9ff', 'text': 'Self Transfiguration'},
            'Choso': {'time': 20, 'color': '#410000', 'completed_color': '#7f0000', 'text': 'Convergence'},
            'Todo (Normal)': {'time': 10.5, 'color': '#80d5ff', 'completed_color': '#f9fdff', 'text': 'Boogie Woogie'},
            'Todo (Perfect / Bluff)': {'time': 2, 'color': '#80d5ff', 'completed_color': '#f9fdff', 'text': 'Boogie Woogie'},
            'Todo (Throwable)': {'time': 5, 'color': '#80d5ff', 'completed_color': '#f9fdff', 'text': 'Boogie Woogie'},
            'Higuruma (NOT ADDED YET)': {'time': 2, 'color': '#795023', 'completed_color': '#b07f3c', 'text': 'NONE'},
            'Locust': {'time': 10, 'color': '#398d00', 'completed_color': '#54a900', 'text': 'Fluttering Pounce'}
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
                command=lambda t=preset_data['time'], c=preset_data['color'], cc=preset_data['completed_color']: 
                    self.start_countdown(t, c, cc, start_immediately=False)
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
        
        # Add Cleave state tracker
        self.is_cleave_mode = False
        
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
    
    def start_countdown(self, seconds, color, completed_color=None, start_immediately=True):
        self.total_seconds = seconds
        self.last_time = seconds
        self.last_color = color
        
        # Handle completed color
        if completed_color:
            self.current_completed_color = completed_color
        else:
            # Find the preset's completed color
            try:
                self.current_completed_color = self.presets[next(
                    key for key, value in self.presets.items() 
                    if value['time'] == seconds and value['color'] == color
                )]['completed_color']
            except StopIteration:
                # Fallback to last known completed color if preset not found
                self.current_completed_color = self.last_color
        
        if start_immediately:
            self.counting = True
            self.start_time = time.time()
            self.elapsed = 0
            self.canvas.itemconfig(self.progress_bar, fill=color, outline=color)
            self.canvas.itemconfig(self.text_element, text="")  # Hide text during countdown
        else:
            self.counting = False
            self.canvas.coords(self.progress_bar, 2, 2, 301, 21)  # Adjusted coordinates
            self.canvas.itemconfig(self.progress_bar, fill=self.current_completed_color, outline=self.current_completed_color)
            # Show ability text
            try:
                text = self.presets[next(
                    key for key, value in self.presets.items() 
                    if value['time'] == seconds and value['color'] == color
                )]['text']
                self.canvas.itemconfig(self.text_element, text=text)
            except StopIteration:
                self.canvas.itemconfig(self.text_element, text="")
            # Hide input frame and show progress bar
            self.input_frame.pack_forget()
            self.label.pack_forget()
            self.canvas.pack(pady=0)
            self.root.geometry("304x24")
            return

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
                self.root.configure(bg='#FFFF00')  # Ensure background stays yellow
                
                # Calculate smooth progress (adjusted for new coordinates)
                progress_width = (self.elapsed / self.total_seconds) * 299 + 2
                self.canvas.coords(self.progress_bar, 2, 2, progress_width, 21)
                self.canvas.itemconfig(self.text_element, text="")  # Hide text during countdown
                
                self.root.after(self.update_interval, self.countdown)
            else:
                # Countdown complete (adjusted for 2px border)
                self.counting = False
                self.canvas.coords(self.progress_bar, 2, 2, 301, 21)
                self.canvas.itemconfig(self.progress_bar, fill=self.current_completed_color, outline=self.current_completed_color)
                # Show ability text based on mode
                if self.is_cleave_mode and self.last_color == '#860000':
                    self.canvas.itemconfig(self.text_element, text="Cleave")
                else:
                    try:
                        text = self.presets[next(
                            key for key, value in self.presets.items() 
                            if value['time'] == self.last_time and value['color'] == self.last_color
                        )]['text']
                        self.canvas.itemconfig(self.text_element, text=text)
                    except StopIteration:
                        self.canvas.itemconfig(self.text_element, text="")

    def reset_ui(self):
        """Reset the UI to show buttons again"""
        self.canvas.pack_forget()
        self.input_frame.pack(pady=10)
        self.label.pack(pady=10)
        self.root.geometry("200x150")

    def on_press(self, key):
        try:
            if key.char == 'r' and not self.counting:
                if self.last_time in [12, 13.5] and self.last_color == '#860000':
                    # Special case for Yuji's extended timer
                    self.start_countdown(self.last_time, '#860000', '#f90000')
                else:
                    self.start_countdown(self.last_time, self.last_color)
            elif key.char == 'g':  # Toggle timer
                if self.last_color == '#860000':  # Check if it's Yuji's color
                    if self.last_time == 2:  # Normal timer -> Special timer
                        self.is_cleave_mode = True
                        if self.counting:
                            remaining_ratio = 1 - (self.elapsed / self.total_seconds)
                            self.elapsed = (1 - remaining_ratio) * 13.5
                            self.total_seconds = 13.5
                            self.start_time = time.time() - self.elapsed
                        else:
                            self.start_countdown(13.5, '#860000', '#f90000', start_immediately=False)
                        self.canvas.itemconfig(self.text_element, text="Cleave")
                    elif self.last_time in [12, 13.5]:  # Special timer -> Normal timer
                        self.is_cleave_mode = False
                        if self.counting:
                            remaining_ratio = 1 - (self.elapsed / self.total_seconds)
                            self.elapsed = (1 - remaining_ratio) * 2
                            self.total_seconds = 2
                            self.start_time = time.time() - self.elapsed
                        else:
                            self.start_countdown(2, '#860000', '#f90000', start_immediately=False)
                        self.canvas.itemconfig(self.text_element, text="Combat Instincts")
                    self.last_time = self.total_seconds
        except AttributeError:
            pass
    
    def on_closing(self):
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = CountdownApp()