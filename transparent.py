import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

def make_color_transparent(image_path, color_to_make_transparent, tolerance):

    image = Image.open(image_path)

    image = image.convert("RGBA")

    data = image.getdata()

    new_data = [
        (255, 255, 255, 0) if (
            abs(item[0] - color_to_make_transparent[0]) <= tolerance and
            abs(item[1] - color_to_make_transparent[1]) <= tolerance and
            abs(item[2] - color_to_make_transparent[2]) <= tolerance
        ) else item for item in data
    ]

    image.putdata(new_data)

    return image

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpeg;*.jpg;*.png")])
    if file_path:
        image_path.set(file_path)
        img = Image.open(file_path)
        img.thumbnail((250, 250))
        img = ImageTk.PhotoImage(img)
        image_label.configure(image=img)
        image_label.image = img
        image_label.bind("<Button-1>", get_color_at_click)
        global original_image
        original_image = Image.open(file_path)

def get_color_at_click(event):
    x = event.x
    y = event.y
    img = original_image.copy()
    img.thumbnail((250, 250))
    color = img.getpixel((x, y))
    selected_color.set('#%02x%02x%02x' % color[:3])
    color_display.config(bg=selected_color.get())
    global color_to_make_transparent
    color_to_make_transparent = color[:3]

def process_image():
    if not image_path.get() or not selected_color.get():
        return
    
    global tolerance
    tolerance += 10  # Each time I click process file the tolerance is increased and removes more.
    color_rgb = tuple(int(selected_color.get()[i:i+2], 16) for i in (1, 3, 5))
    processed_image = make_color_transparent(image_path.get(), color_rgb, tolerance)
    
    output_path = os.path.join(os.path.dirname(image_path.get()), "transparent_image.png")
    processed_image.save(output_path)
    
    processed_image.thumbnail((250, 250))
    processed_img = ImageTk.PhotoImage(processed_image)
    output_image_label.configure(image=processed_img)
    output_image_label.image = processed_img
    
    output_path_var.set(output_path)

def save_file():
    if not output_path_var.get():
        return

    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
    if file_path:
        img = Image.open(output_path_var.get())
        img.save(file_path)

# GUI
root = tk.Tk()
root.title("Image Background Remover")

image_path = tk.StringVar()
output_path_var = tk.StringVar()
selected_color = tk.StringVar()
color_to_make_transparent = None
tolerance = 0
original_image = None

# Input
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

input_button = tk.Button(input_frame, text="Select Image", command=select_file)
input_button.pack(side=tk.LEFT, padx=5)

process_button = tk.Button(input_frame, text="Process Image", command=process_image)
process_button.pack(side=tk.LEFT, padx=5)

color_display = tk.Label(input_frame, text="Selected Color", width=10)
color_display.pack(side=tk.LEFT, padx=5)

image_label = tk.Label(root)
image_label.pack(pady=10)

# Output
output_frame = tk.Frame(root)
output_frame.pack(pady=10)

output_image_label = tk.Label(root)
output_image_label.pack(pady=10)

save_button = tk.Button(output_frame, text="Save Processed Image", command=save_file)
save_button.pack(side=tk.LEFT, padx=5)

root.mainloop()