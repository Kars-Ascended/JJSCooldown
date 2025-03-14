import tkinter as tk
from pynput import keyboard
import threading
import time
import tkinter.font as tkfont
import os
from ctypes import windll

# Get the path to your font file (assuming it's in the same directory as main.py)
current_dir = os.path.dirname(os.path.abspath(__file__))
font_path = os.path.join(current_dir, "FingerPaint.ttf")  # Replace with your font filename



class CountdownApp:
    def __init__(self):
        self.root = tk.Tk()
        
        # Register font with Windows and tkinter
        font_path = os.path.join(os.path.dirname(__file__), 'fonts', 'FingerPaint.ttf')
        try:
            # Register font with Windows
            result = windll.gdi32.AddFontResourceW(font_path)
            print(f"Font registration result: {result}")  # 1 means success
            
            # Load and register with tkinter
            self.root.tk.call('font', 'create', 'FingerPaint')
            self.custom_font = tkfont.Font(family="Finger Paint", size=13)
            
            # Print available fonts for debugging
            print("Available fonts:", [f for f in tkfont.families() if 'finger' in f.lower()])
            
            self.font_loaded = True
        except Exception as e:
            print(f"Error loading font: {e}")
            self.custom_font = ("Arial", 13)
            self.font_loaded = False

        self.root.title("Countdown Timer")
        self.root.geometry("1200x350")
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
        
        # Create outline effect with multiple black text objects
        offset = 1  # Adjust this value to change outline thickness
        self.text_outline = []
        for x_offset in [-offset, offset]:
            for y_offset in [-offset, offset]:
                outline = self.canvas.create_text(
                    151 + x_offset, 
                    11 + y_offset, 
                    text="",
                    fill="black",
                    anchor="center",
                    font=self.custom_font
                )
                self.text_outline.append(outline)
        
        # Create the main white text on top
        self.text_element = self.canvas.create_text(
            151, 11,
            text="",
            fill="white",
            anchor="center",
            font=self.custom_font
        )
        
        # Create a frame for input elements
        self.input_frame = tk.Frame(self.root)
        self.input_frame.pack(pady=10)
        
        # Add description text
        description = tk.Label(
            self.input_frame,
            text="Shenanigans timer by r/Father_Enrico\n"
            "Click a character to start their cooldown timer, pressing 'R' will restart the timer\n"
            "Certain characters like megumi have their cooldowns adjusted as moves only go on cooldown when the move ends\nso if the timings feel off its for this reason \n"
            "Upper bound = adjusted for when the move ends (so if you cancel it sooner it will display slightly off)\n",
            font=self.custom_font,
            justify=tk.CENTER
        )
        description.pack(pady=5)

        # Define presets with their times and colors (make the main colour the average of the ult bar colours, and the completed colour the top of the ult bar)
        self.presets = {
            'Gojo': {'time': 15.6, 'color': '#02acff', 'completed_color': '#2bd5ff', 'text': 'Limitless'},
            'Yuji': {'time': 2, 'color': '#860000', 'completed_color': '#f90000', 'text': 'Combat Instincts'},
            'Hakari': {'time': 12.6, 'color': '#02ac7f', 'completed_color': '#53fd7f', 'text': 'Door Guard'},
            'Megumi (Upper bound)': {'time': 11.8, 'color': '#011e2d', 'completed_color': '#2c2d2d', 'text': 'Lurking Shadow'},  # color needs redoing
            'Mahito': {'time': 0.2, 'color': '#558dff', 'completed_color': '#a6a9ff', 'text': 'Self Transfiguration'},
            'Choso': {'time': 20.5, 'color': '#410000', 'completed_color': '#7f0000', 'text': 'Convergence'},
            'Todo (Normal)': {'time': 10.5, 'color': '#80d5ff', 'completed_color': '#f9fdff', 'text': 'Boogie Woogie'},
            'Todo (Perfect / Bluff)': {'time': 2, 'color': '#80d5ff', 'completed_color': '#f9fdff', 'text': 'Boogie Woogie'},
            'Todo (Throwable)': {'time': 5, 'color': '#80d5ff', 'completed_color': '#f9fdff', 'text': 'Boogie Woogie'},
            'Higuruma (NOT ADDED YET)': {'time': 2, 'color': '#795023', 'completed_color': '#b07f3c', 'text': 'NONE'},
            'Locust': {'time': 10.4, 'color': '#398d00', 'completed_color': '#54a900', 'text': 'Fluttering Pounce'}
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
        self.label = tk.Label(self.root, text="Drag Me", 
            font=self.custom_font)
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
        
        # Cache for preset lookups
        self.preset_cache = {}
        # Cache for commonly used values
        self.canvas_width = 304
        self.progress_start = 2
        self.progress_end = 301
        self.progress_height = 21
        
        # Yuji's specific values
        self.yuji_config = {
            'normal': {'time': 2, 'text': 'Combat Instincts'},
            'cleave': {'time': 13.5, 'text': 'Cleave'},
            'color': '#860000',
            'completed_color': '#f90000'
        }
        
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
        # Cache preset lookup result
        cache_key = f"{seconds}_{color}"
        if (cache_key not in self.preset_cache):
            try:
                preset = next(
                    value for value in self.presets.values()
                    if value['time'] == seconds and value['color'] == color
                )
                self.preset_cache[cache_key] = preset
            except StopIteration:
                self.preset_cache[cache_key] = None

        preset = self.preset_cache[cache_key]
        
        self.total_seconds = seconds
        self.last_time = seconds
        self.last_color = color
        
        # Simplified color handling
        self.current_completed_color = completed_color or (preset['completed_color'] if preset else self.last_color)
        
        if start_immediately:
            self.counting = True
            self.start_time = time.time()
            self.elapsed = 0
            self.canvas.itemconfig(self.progress_bar, fill=color, outline=color)
            # Clear both outline and main text
            for outline in self.text_outline:
                self.canvas.itemconfig(outline, text="")
            self.canvas.itemconfig(self.text_element, text="")
        else:
            self.counting = False
            self.canvas.coords(self.progress_bar, self.progress_start, self.progress_start, 
                             self.progress_end, self.progress_height)
            self.canvas.itemconfig(self.progress_bar, 
                                 fill=self.current_completed_color, 
                                 outline=self.current_completed_color)
            # Update both outline and main text with preset text
            text = preset['text'] if preset else ""
            for outline in self.text_outline:
                self.canvas.itemconfig(outline, text=text)
            self.canvas.itemconfig(self.text_element, text=text)
            
            self.input_frame.pack_forget()
            self.label.pack_forget()
            self.canvas.pack(pady=0)
            self.root.geometry(f"{self.canvas_width}x24")
            return

        self.countdown()

    def countdown(self):
        if self.counting:
            self.elapsed = time.time() - self.start_time
            remaining = self.total_seconds - self.elapsed
            
            if remaining > 0:
                # Hide input frame and show progress bar
                self.input_frame.pack_forget()
                self.label.pack_forget()
                self.canvas.pack(pady=0)
                self.root.geometry("304x24")
                self.root.configure(bg='#FFFF00')  
                
                # Optimized progress calculation
                progress_width = self.progress_start + (self.elapsed / self.total_seconds) * 299
                self.canvas.coords(self.progress_bar, self.progress_start, self.progress_start,
                                 progress_width, self.progress_height)
                
                # Clear both outline and main text during countdown
                for outline in self.text_outline:
                    self.canvas.itemconfig(outline, text="")
                self.canvas.itemconfig(self.text_element, text="")
                
                self.root.after(self.update_interval, self.countdown)
            else:
                # Countdown complete
                self.counting = False
                self.canvas.coords(self.progress_bar, self.progress_start, self.progress_start,
                                 self.progress_end, self.progress_height)
                self.canvas.itemconfig(self.progress_bar, 
                                     fill=self.current_completed_color,
                                     outline=self.current_completed_color)
                
                # Get the appropriate text to display
                if self.is_cleave_mode and self.last_color == self.yuji_config['color']:
                    display_text = self.yuji_config['cleave']['text']
                else:
                    cache_key = f"{self.last_time}_{self.last_color}"
                    preset = self.preset_cache.get(cache_key)
                    display_text = preset['text'] if preset else ""
                
                # Update both outline and main text
                for outline in self.text_outline:
                    self.canvas.itemconfig(outline, text=display_text)
                self.canvas.itemconfig(self.text_element, text=display_text)

    def reset_ui(self):
        """Reset the UI to show buttons again"""
        self.canvas.pack_forget()
        self.input_frame.pack(pady=10)
        self.label.pack(pady=10)
        self.root.geometry("200x150")

    def on_press(self, key):
        try:
            if key.char == 'r' and not self.counting:
                if self.last_time in [self.yuji_config['cleave']['time']] and self.last_color == self.yuji_config['color']:
                    self.start_countdown(self.last_time, self.yuji_config['color'], self.yuji_config['completed_color'])
                else:
                    self.start_countdown(self.last_time, self.last_color)
            elif key.char == 'g' and self.last_color == self.yuji_config['color']:
                self._toggle_yuji_mode()
        except AttributeError:
            pass

    def _toggle_yuji_mode(self):
        """Helper method for Yuji's mode toggle logic"""
        if self.last_time == self.yuji_config['normal']['time']:
            self.is_cleave_mode = True
            new_time = self.yuji_config['cleave']['time']
            text = self.yuji_config['cleave']['text']
        else:
            self.is_cleave_mode = False
            new_time = self.yuji_config['normal']['time']
            text = self.yuji_config['normal']['text']

        if self.counting:
            remaining_ratio = 1 - (self.elapsed / self.total_seconds)
            self.elapsed = (1 - remaining_ratio) * new_time
            self.total_seconds = new_time
            self.start_time = time.time() - self.elapsed
        else:
            self.start_countdown(new_time, self.yuji_config['color'], 
                               self.yuji_config['completed_color'], start_immediately=False)
        
        # Update both outline and main text
        for outline in self.text_outline:
            self.canvas.itemconfig(outline, text=text)
        self.canvas.itemconfig(self.text_element, text=text)
        
        self.last_time = new_time
    
    def on_closing(self):
        self.listener.stop()
        self.root.destroy()

if __name__ == "__main__":
    app = CountdownApp()