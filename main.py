import tkinter as tk
import matplotlib.pyplot as plt
from tkinter import filedialog
from tkinter import colorchooser
from PIL import Image, ImageOps, ImageTk, ImageFilter, ImageDraw, ImageColor, ImageEnhance
from tkinter import ttk
import threading


root = tk.Tk()
root.geometry("1280x750")
root.title("Image Edit Tool")
root.config(bg="white")

pen_color = "black"
pen_size = 5
file_path = ""
export_format = tk.StringVar(value="png")  # Default export format
current_scale = 1.0  # Default zoom scale

edited_image = None
unfiltered_image = None
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

def change_color():
    global pen_color
    pen_color = colorchooser.askcolor(title="Select Pen Color")[1]


def change_size(size):
    global pen_size
    pen_size = size


def draw(event):
    x1, y1 = (event.x - pen_size), (event.y - pen_size)
    x2, y2 = (event.x + pen_size), (event.y + pen_size)
    canvas.create_oval(x1, y1, x2, y2, fill=pen_color, outline='')


def clear_canvas():
    canvas.delete("all")
    canvas.create_image(0, 0, image=canvas.image, anchor="nw")


def apply_filter(filter):
    global edited_image

    image = Image.open(file_path)

    # Update the canvas with the filtered image
    redraw_image(image, filter)


def export_image_background():
    # Create a new thread for exporting
    export_thread = threading.Thread(target=export_image)
    export_thread.start()


def export_image():
    global file_path

    if file_path:
        export_path = filedialog.asksaveasfilename(defaultextension="." + export_format.get(),
                                                     filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.webp")])

        if export_path:
            # Apply filters to the original image
            if edited_image is not None:
                original_image = edited_image.copy()
            else:
                original_image = Image.open(file_path)

            # Create a new image with the same size
            exported_image = Image.new("RGBA", original_image.size, (255, 255, 255, 0))

            # Paste the original image onto the new image
            exported_image.paste(original_image, (0, 0))

            # Create an ImageDraw object to draw on the new image
            draw = ImageDraw.Draw(exported_image)

            # Iterate over canvas items
            for item in canvas.find_all():
                item_type = canvas.type(item)
                if item_type == "oval":
                    coords = canvas.coords(item)
                    fill_color = canvas.itemcget(item, "fill")
                    outline_color = canvas.itemcget(item, "outline")
                    
                    # Handle empty fill color
                    if fill_color == "":
                        fill_color = None

                    # Convert Tkinter color to PIL color
                    fill_color = ImageColor.getrgb(fill_color) if fill_color else None
                    outline_color = ImageColor.getrgb(outline_color) if outline_color else None

                    # Adjust coordinates based on scaling factor and canvas size
                    coords = [coord / current_scale for coord in coords]
                    coords[0] *= original_image.width * current_scale / canvas.winfo_reqwidth()
                    coords[1] *= original_image.height * current_scale / canvas.winfo_reqheight()
                    coords[2] *= original_image.width * current_scale / canvas.winfo_reqwidth()
                    coords[3] *= original_image.height * current_scale / canvas.winfo_reqheight()

                    # Draw the oval directly onto the exported image
                    draw.ellipse(coords, fill=fill_color, outline=outline_color)

            # Save the modified image in the selected format
            exported_image.save(export_path)
            exported_image.close()


def zoom_in():
    global current_scale
    current_scale *= 1.2
    redraw_image(unfiltered_image, current_filter)

def zoom_out():
    global current_scale
    current_scale /= 1.2
    redraw_image(unfiltered_image, current_filter)

def redraw_image(image, filter=None):
    global edited_image
    global unfiltered_image
    global current_filter

    if image is None:
        image = Image.open(file_path)

    original_image = image

    if filter is not None:
        current_filter = filter
        if filter == "Black and White":
                filtered_image = ImageOps.grayscale(image)
        elif filter == "Blur":
                filtered_image = image.filter(ImageFilter.BLUR)
        elif filter == "Sharpen":
                filtered_image = image.filter(ImageFilter.SHARPEN)
        elif filter == "Smooth":
                filtered_image = image.filter(ImageFilter.SMOOTH)
        elif filter == "Emboss":
                filtered_image = image.filter(ImageFilter.EMBOSS)
        width, height = int(filtered_image.width * current_scale), int(filtered_image.height * current_scale)
        resized_image = filtered_image.resize((width, height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_image)
        edited_image = filtered_image
    else:
        width, height = int(image.width * current_scale), int(image.height * current_scale)
        resized_image = image.resize((width, height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(resized_image)

    # Update canvas with the new photo
    canvas.config(width=resized_image.width, height=resized_image.height)
    canvas.delete("all")  # Clear the canvas
    canvas.image = photo
    canvas.create_image(0, 0, image=photo, anchor="nw")
    
    unfiltered_image = original_image


def transform_image(transform_type):
    global unfiltered_image

    if transform_type == "Flip Horizontal":
        unfiltered_image = unfiltered_image.transpose(Image.FLIP_LEFT_RIGHT)
    elif transform_type == "Flip Vertical":
        unfiltered_image = unfiltered_image.transpose(Image.FLIP_TOP_BOTTOM)
    # Add more transformation types here

    redraw_image(unfiltered_image, current_filter)


def resize_image(width, height):
    global unfiltered_image

    if file_path:
        if unfiltered_image is not None:
            original_image = unfiltered_image
        else:
            original_image = Image.open(file_path)
        
    unfiltered_image = original_image.resize((width, height), Image.ANTIALIAS)
        
    redraw_image(unfiltered_image, current_filter) 


def invert_colors():
    global unfiltered_image

    if unfiltered_image is not None:
        inverted_image = ImageOps.invert(unfiltered_image.convert('RGB'))
    else:
        image = Image.open(file_path)
        inverted_image = ImageOps.invert(image.convert('RGB'))

    redraw_image(inverted_image, current_filter)


def getRed(R): return '#%02x%02x%02x'%(R,0,0)
def getGreen(G): return '#%02x%02x%02x'%(0,G,0)
def getBlue(B):return '#%02x%02x%02x'%(0,0,B)

def show_histogram():
    if edited_image is not None:
        hst=edited_image.histogram()
    elif unfiltered_image is not None:
        hst=unfiltered_image.histogram()
    else:
        image = Image.open(file_path)
        hst=image.histogram()
    
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
    global unfiltered_image

    if origin_image is not None:
        enhancer = ImageEnhance.Color(origin_image)
        color_adjusted_image = enhancer.enhance(factor)
        redraw_image(color_adjusted_image)
    

def adjust_contrast(factor):
    global unfiltered_image, origin_image

    if unfiltered_image is not None:
        enhancer = ImageEnhance.Contrast(origin_image)
        color_adjusted_image = enhancer.enhance(factor)
        redraw_image(color_adjusted_image)


def merge_images():
    global origin_image, adjusted_image

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
        adjusted_image = Image.alpha_composite(original_image_with_alpha, merge_image)

        # Redraw the canvas with the new image
        redraw_image(adjusted_image)

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

color_button = tk.Button(
    left_frame, text="Change Pen Color", command=change_color, bg="white")
color_button.pack(pady=5)

pen_size_frame = tk.Frame(left_frame, bg="white")
pen_size_frame.pack(pady=5)

pen_size_1 = tk.Radiobutton(
    pen_size_frame, text="Small", value=3, command=lambda: change_size(3), bg="white")
pen_size_1.pack(side="left")

pen_size_2 = tk.Radiobutton(
    pen_size_frame, text="Medium", value=5, command=lambda: change_size(5), bg="white")
pen_size_2.pack(side="left")
pen_size_2.select()

pen_size_3 = tk.Radiobutton(
    pen_size_frame, text="Large", value=7, command=lambda: change_size(7), bg="white")
pen_size_3.pack(side="left")

clear_button = tk.Button(left_frame, text="Clear",
                         command=clear_canvas, bg="#FF9797")
clear_button.pack(pady=5)

filter_label = tk.Label(left_frame, text="Select Filter", bg="white")
filter_label.pack()
filter_combobox = ttk.Combobox(left_frame, values=["Black and White", "Blur",
                                             "Emboss", "Sharpen", "Smooth"])
filter_combobox.pack()


filter_combobox.bind("<<ComboboxSelected>>",
                     lambda event: apply_filter(filter_combobox.get()))

export_format_label = tk.Label(left_frame, text="Select Export Format", bg="white")
export_format_label.pack()
export_format_combobox = ttk.Combobox(left_frame, textvariable=export_format, values=["png", "jpg", "jpeg", "webp"])
export_format_combobox.pack()

export_button = tk.Button(left_frame, text="Export Image",
                          command=export_image_background, bg="white")
export_button.pack(pady=5)

zoom_in_button = tk.Button(left_frame, text="Zoom In",
                           command=zoom_in, bg="white")
zoom_in_button.pack(pady=5)

zoom_out_button = tk.Button(left_frame, text="Zoom Out",
                            command=zoom_out, bg="white")
zoom_out_button.pack(pady=5)

resize_label = tk.Label(left_frame, text="Resize Image", bg="white")
resize_label.pack()

width_entry = tk.Entry(left_frame, width=5)
width_entry.pack()
height_entry = tk.Entry(left_frame, width=5)
height_entry.pack()

resize_button = tk.Button(
    left_frame, text="Resize", command=lambda: resize_image(int(width_entry.get()), int(height_entry.get())), bg="white"
)
resize_button.pack(pady=5)

transform_label = tk.Label(left_frame, text="Transform Image", bg="white")
transform_label.pack()

transform_combobox = ttk.Combobox(
    left_frame, values=["Flip Horizontal", "Flip Vertical"]
)
transform_combobox.pack()

transform_button = tk.Button(
    left_frame,
    text="Transform",
    command=lambda: transform_image(
        transform_combobox.get()
    ),
    bg="white",
)
transform_button.pack(pady=5)

image_button = tk.Button(left_frame, text="Invert colors",
                         command=invert_colors, bg="white")
image_button.pack(pady=5)

image_button = tk.Button(left_frame, text="Show histogram",
                         command=show_histogram, bg="white")
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

canvas.bind("<B1-Motion>", draw)

root.mainloop()