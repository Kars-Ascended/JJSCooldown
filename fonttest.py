import tkinter as tk
from tkinter import font
import os
from ctypes import windll

root = tk.Tk()

# Get absolute path to font file
font_path = os.path.abspath("fonts/FingerPaint.ttf")
print(f"Loading font from: {font_path}")

try:
    # Register font with Windows
    result = windll.gdi32.AddFontResourceW(font_path)
    print(f"Font registration result: {result}")  # 1 means success
    
    # Load and register with tkinter
    root.tk.call('font', 'create', 'FingerPaint')
    custom_font = font.Font(family="Finger Paint", size=20)
    
    # Print available fonts for debugging
    print("Available fonts:", [f for f in font.families() if 'finger' in f.lower()])
    
    # Apply to test label
    label = tk.Label(root, text="Hello, Custom Font!", font=custom_font)
    label.pack(pady=20)
    
except Exception as e:
    print(f"Error loading font: {e}")
    # Fallback to system font
    label = tk.Label(root, text="Hello, Fallback Font!", font=("Arial", 20))
    label.pack(pady=20)

root.mainloop()
