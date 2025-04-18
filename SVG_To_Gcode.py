import tkinter as tk
from tkinter import filedialog, Button
import os

from svg_to_gcode.svg_parser import parse_file
from svg_to_gcode.compiler import Compiler, interfaces

svg_file_path = ""

def browse_file():
    global svg_file_path
    svg_file_path = filedialog.askopenfilename(filetypes=[("SVG", "*.svg")])
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, svg_file_path)

def convert_file():
    convert_button.config(text="Converting...", state='disabled')
    window.update_idletasks()

    print("Converting:", svg_file_path)
    folder_path = os.path.dirname(svg_file_path)

    # Get desired output name or default to 'Untitled.gcode'
    output_filename = gcode_name_entry.get().strip() or "Untitled"
    if not output_filename.endswith(".gcode"):
        output_filename += ".gcode"

    temp_path = os.path.join(folder_path, "temp_file.gcode")
    output_path = os.path.join(folder_path, output_filename)

    # Generate temp GCode
    gcode_compiler = Compiler(interfaces.Gcode, movement_speed=1000, cutting_speed=300, pass_depth=2)
    curves = parse_file(svg_file_path)
    gcode_compiler.append_curves(curves)
    gcode_compiler.compile_to_file(temp_path, passes=1)

    # Modify and save final GCode
    with open(temp_path, "r") as f:
        gcode = f.readlines()

    with open(output_path, "w") as f_new:
        m5_detected = 0
        for line in gcode:
            if "M5" in line:
                f_new.write(line)
                f_new.write("G1 Z2.000000\n")
                m5_detected = 1
            else:
                f_new.write(line)
                if m5_detected == 1:
                    f_new.write("G1 Z-2.000000\n")
                    m5_detected = 0

    # Clean up temp file
    if os.path.exists(temp_path):
        os.remove(temp_path)

    print("Conversion complete. Output saved to:", output_path)
    convert_button.config(text="Convert", state='normal')

# GUI setup
window = tk.Tk()
window.title("SVG to GCode Tool")
window.geometry("500x200")

file_frame = tk.Frame(window)
file_frame.pack(pady=10, anchor='w')

# SVG File Label
label = tk.Label(file_frame, text="SVG file:")
label.grid(row=0, column=0, padx=5)

text_box = tk.Text(file_frame, height=1, width=45)
text_box.grid(row=0, column=1, padx=5)

browse_button = Button(file_frame, text="Choose file", command=browse_file)
browse_button.grid(row=0, column=2, padx=5)

# GCode Filename Field
gcode_name_label = tk.Label(file_frame, text="GCode file name:")
gcode_name_label.grid(row=1, column=0, padx=5, pady=5)

gcode_name_entry = tk.Entry(file_frame, width=47)
gcode_name_entry.grid(row=1, column=1, columnspan=2, padx=5, sticky='w')

# Convert Button
convert_button = Button(window, text="Convert", command=convert_file)
convert_button.pack(pady=10, padx=20, anchor='w')

window.mainloop()
