import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import colorchooser
from PIL import Image, ImageOps, ImageTk, ImageFilter, ImageDraw, ImageColor, ImageEnhance
from tkinter import ttk
import threading


root = tk.Tk()
root.geometry("1000x600")
root.title("Image Edit Tool")
root.config(bg="white")

file_path = ""
export_format = tk.StringVar(value="png")  # Default export format
current_scale = 1.0  # Default zoom scale

edited_image = None
current_filter = None
origin_image = None

def add_image():
    global file_path, origin_image

    file_path = filedialog.askopenfilename(
        initialdir="D:/Workspace/opencv/python-tkiner-image-editor")
    image = Image.open(file_path)
    origin_image = image.copy()
    width, height = int(image.width), int(image.height)
    image = image.resize((width, height), Image.ANTIALIAS)
    canvas.config(width=image.width, height=image.height)
    image = ImageTk.PhotoImage(image)
    canvas.image = image
    canvas.create_image(0, 0, image=image, anchor="nw")


def export_image_background():
    # Create a new thread for exporting
    export_thread = threading.Thread(target=export_image)
    export_thread.start()


def export_image():
    global file_path, edited_image

    if file_path:
        export_format_str = export_format.get()
        export_path = filedialog.asksaveasfilename(defaultextension="." + export_format_str,
                                                     filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp")])

        if export_path:
            # Apply filters to the edited image if available, else use the original image
            if edited_image is not None:
                exported_image = edited_image.copy()
            else:
                exported_image = Image.open(file_path)

            # Check if the selected export format is JPEG and convert to RGB if necessary
            if export_format_str.lower() in ['jpg', 'jpeg'] and exported_image.mode == 'RGBA':
                exported_image = exported_image.convert('RGB')

            # Save the modified image in the selected format
            exported_image.save(export_path)
            exported_image.close()


def redraw_image(image):
    global edited_image
    global original_image

    if image is None:
        image = Image.open(file_path)

    original_image = image

    width, height = int(image.width * current_scale), int(image.height * current_scale)
    resized_image = image.resize((width, height), Image.ANTIALIAS)
    photo = ImageTk.PhotoImage(resized_image)

    # Update canvas with the new photo
    canvas.config(width=resized_image.width, height=resized_image.height)
    canvas.delete("all")  # Clear the canvas
    canvas.image = photo
    canvas.create_image(0, 0, image=photo, anchor="nw")


def invert_colors():
    global edited_image

    if edited_image is not None:
        inverted_image = ImageOps.invert(edited_image.convert('RGB'))
    else:
        image = Image.open(file_path)
        inverted_image = ImageOps.invert(image.convert('RGB'))

    redraw_image(inverted_image)
    edited_image = inverted_image


def getRed(R): return '#%02x%02x%02x'%(R,0,0)
def getGreen(G): return '#%02x%02x%02x'%(0,G,0)
def getBlue(B):return '#%02x%02x%02x'%(0,0,B)

def show_histogram():
    global edited_image

    if edited_image is not None:
        hst=edited_image.histogram()
    else:
        image = Image.open(file_path)
        hst=image.histogram()
    
    Red=hst[0:256] # indicates Red
    Green=hst[256:512] # indicated Green
    Blue=hst[512:768] # indicates Blue

    plt.figure(0) # plots a figure to display RED Histogram
    for i in range(0, 256):
        plt.bar(i, Red[i], color = getRed(i),alpha=0.3)
        plt.title('Red Histogram Chart')

    plt.figure(1) # plots a figure to display GREEN Histogram
    for i in range(0, 256):
        plt.bar(i, Green[i], color = getGreen(i),alpha=0.3)
        plt.title('Green Histogram Chart')

    plt.figure(2) # plots a figure to display BLUE Histogram
    for i in range(0, 256):
        plt.bar(i, Blue[i], color = getBlue(i),alpha=0.3)
        plt.title('Blue Histogram Chart')

    plt.show()


def adjust_color(factor):
    global edited_image, origin_image

    if origin_image is not None:
        enhancer = ImageEnhance.Color(origin_image)
    
    color_adjusted_image = enhancer.enhance(factor)
    redraw_image(color_adjusted_image)
    edited_image = color_adjusted_image
    

def adjust_contrast(factor):
    global edited_image, origin_image

    if origin_image is not None:
        enhancer = ImageEnhance.Contrast(origin_image)
    
    color_adjusted_image = enhancer.enhance(factor)
    redraw_image(color_adjusted_image)
    edited_image = color_adjusted_image


def equalize_histogram():
    global edited_image, origin_image

    if edited_image is not None:
        equalized_image = ImageOps.equalize(edited_image, mask = None)
    elif origin_image is not None:
        equalized_image = ImageOps.equalize(origin_image, mask = None)

    redraw_image(equalized_image)
    edited_image = equalized_image


def merge_images():
    global origin_image, edited_image

    # Let the user choose an image to merge
    merge_file_path = filedialog.askopenfilename()
    if not merge_file_path:
        return

    merge_image = Image.open(merge_file_path)

    # Resize merge_image to match original_image, if necessary
    if merge_image.size != origin_image.size:
        merge_image = merge_image.resize(origin_image.size)

    # Ensure both images have an alpha channel
    if merge_image.mode != 'RGBA':
        merge_image = merge_image.convert('RGBA')
    if origin_image.mode != 'RGBA':
        original_image_with_alpha = origin_image.convert('RGBA')
    else:
        original_image_with_alpha = origin_image

    # Merge the images using alpha_composite
    if origin_image is not None:
        # Create a copy of the original to preserve it
        edited_image = Image.alpha_composite(original_image_with_alpha, merge_image)
        origin_image = edited_image

        # Redraw the canvas with the new image
        redraw_image(edited_image)

# Callback function for color adjustment slider
def on_color_slider_change(value):
    adjust_color(float(value))

# Callback function for contrast adjustment slider
def on_contrast_slider_change(value):
    adjust_contrast(float(value))


left_frame = tk.Frame(root, width=200, height=600, bg="white")
left_frame.pack(side="left", fill="y")

canvas = tk.Canvas(root, width=750, height=600)
canvas.pack()

image_button = tk.Button(left_frame, text="Add Image",
                         command=add_image, bg="white")
image_button.pack(pady=5)

export_format_label = tk.Label(left_frame, text="Select Export Format", bg="white")
export_format_label.pack()
export_format_combobox = ttk.Combobox(left_frame, textvariable=export_format, values=["png", "jpg", "jpeg", "webp"])
export_format_combobox.pack()

export_button = tk.Button(left_frame, text="Export Image",
                          command=export_image_background, bg="white")
export_button.pack(pady=5)

image_button = tk.Button(left_frame, text="Invert colors",
                         command=invert_colors, bg="white")
image_button.pack(pady=5)

image_button = tk.Button(left_frame, text="Show histogram",
                         command=show_histogram, bg="white")
image_button.pack(pady=5)

image_button = tk.Button(left_frame, text="Equalize histogram",
                         command=equalize_histogram, bg="white")
image_button.pack(pady=5)

# Color Adjustment Slider
color_adjust_label = tk.Label(left_frame, text="Adjust Color", bg="white")
color_adjust_label.pack()

color_slider = tk.Scale(left_frame, from_=0, to=2, resolution=0.1, orient="horizontal", command=on_color_slider_change)
color_slider.set(1)  # Default value
color_slider.pack()

# Contrast Adjustment Slider
contrast_adjust_label = tk.Label(left_frame, text="Adjust Contrast", bg="white")
contrast_adjust_label.pack()

contrast_slider = tk.Scale(left_frame, from_=0, to=2, resolution=0.1, orient="horizontal", command=on_contrast_slider_change)
contrast_slider.set(1)  # Default value
contrast_slider.pack()

merge_images_button = tk.Button(left_frame, text="Merge Images", command=merge_images, bg="white")
merge_images_button.pack(pady=5)

root.mainloop()