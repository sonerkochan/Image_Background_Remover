import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageChops
import os

def make_color_transparent(image, color_to_make_transparent, tolerance):
    
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
        global processed_image
        processed_image = original_image.copy()
        global undo_stack
        undo_stack = [original_image.copy()] 

def get_color_at_click(event):
    x = event.x
    y = event.y
    img = processed_image.copy()
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
    global processed_image
    tolerance += 10 # Tolerance
    color_rgb = tuple(int(selected_color.get()[i:i+2], 16) for i in (1, 3, 5))
    processed_image = make_color_transparent(processed_image, color_rgb, tolerance)
    
    output_path = os.path.join(os.path.dirname(image_path.get()), "transparent_image.png")
    processed_image.save(output_path)
    
    processed_image.thumbnail((250, 250))
    processed_img = ImageTk.PhotoImage(processed_image)
    image_label.configure(image=processed_img)
    image_label.image = processed_img
    
    output_path_var.set(output_path)
    
    undo_stack.append(processed_image.copy())

def undo():
    if len(undo_stack) > 1:

        current_image = undo_stack.pop()
        previous_image = undo_stack[-1]
        
        original_width, original_height = original_image.size
        previous_image_resized = previous_image.resize((original_width, original_height))
        
        processed_image = previous_image_resized.copy()
        
        processed_image.thumbnail((250, 250))
        processed_img = ImageTk.PhotoImage(processed_image)
        image_label.configure(image=processed_img)
        image_label.image = processed_img

def save_current_image():
    if not processed_image:
        return
    
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
    if file_path:
        processed_image.save(file_path)

# GUI
root = tk.Tk()
root.title("Image Background Remover")

image_path = tk.StringVar()
output_path_var = tk.StringVar()
selected_color = tk.StringVar()
color_to_make_transparent = None
tolerance = 0
original_image = None
processed_image = None
undo_stack = []

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

undo_button = tk.Button(root, text="Undo", command=undo)
undo_button.pack(pady=5)

save_button = tk.Button(root, text="Save Image", command=save_current_image)
save_button.pack(pady=5)

root.mainloop()