import re
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
import os

"""
Function names should be lowercase, with words separated by underscores as necessary to improve readability.
Variable names follow the same convention as function names.
mixedCase is allowed only in contexts where that’s already the prevailing style (e.g. threading.py), to retain backwards compatibility."""
# https://peps.python.org/pep-0008/#function-and-variable-names





PAINT_CANVAS_WIDTH = 256
PAINT_CANVAS_HEIGHT = 256
THUMBNAIL_CANVAS_WIDTH = 32
THUMBNAIL_CANVAS_HEIGHT = 32

ROWS_PER_TILE = 8
COLUMN_PER_TILE = 8
PIXELS_PER_TILE = ROWS_PER_TILE * COLUMN_PER_TILE

PAINT_CANVAS_X_PIXELS_PER_PIXEL = PAINT_CANVAS_WIDTH / COLUMN_PER_TILE
PAINT_CANVAS_Y_PIXELS_PER_PIXEL = PAINT_CANVAS_HEIGHT / ROWS_PER_TILE

THUMBNAILS_PER_ROW = 6

"""2-Bit colours
White      224,248,208
Light Gray 136,192,112
Dark Gray   52,104, 86
Black        8, 24, 32
"""

WHITE = "#e0f8d0"
LIGHT_GRAY = "#88c070"
DARK_GRAY = "#346856"
BLACK = "#081820"

COLOURS = (WHITE, LIGHT_GRAY, DARK_GRAY, BLACK)

DEFAULT_PEN_COLOUR_INDEX = 1

# Array to hold the pixel date of each tile.
tile_pixels_index = []

# The index of the colour that will be drawn on the canvas when clicked.
pen_colour_index = DEFAULT_PEN_COLOUR_INDEX

# The index of the current tile that is being edited.
focused_tile = 0

# The most tiles that ever existed on screen since the program started.
max_tiles_created = 0

# The number of tiles on the screen.
current_tile_count = 0

# Array to hold thumbnails.
thumbnails_array = []

# Array to hold thumbnail borders.
thumbnail_boarders_array = []

# Array to hold thumbnail rows
thumbnail_rows_array = []


# Draw a pixel on a given canvas in a given colour.
def draw_on_canvas(target_canvas, local_pixel_number, colour_index):
    # Get the X and Y components of the pixel.
    pixel_x_index = local_pixel_number % COLUMN_PER_TILE
    pixel_y_index = int(local_pixel_number / COLUMN_PER_TILE)

    # Get the dimensions of the target canvas.
    canvas_width = target_canvas.winfo_width()
    canvas_height = target_canvas.winfo_height()

    # Get the dimensions of one tile pixel on the target canvas.
    x_pixels_per_pixel = canvas_width / COLUMN_PER_TILE
    y_pixels_per_pixel = canvas_width / ROWS_PER_TILE

    # Get the boundaries of the tile pixel that is to be drawn on the canvas.
    tile_pixel_left_position = pixel_x_index * x_pixels_per_pixel
    tile_pixel_top_position = pixel_y_index * y_pixels_per_pixel
    tile_pixel_right_position = tile_pixel_left_position + x_pixels_per_pixel
    tile_pixel_bottom_position = tile_pixel_top_position + y_pixels_per_pixel

    # Place the tile pixel on the canvas.
    target_canvas.create_rectangle(
        tile_pixel_left_position,
        tile_pixel_top_position,
        tile_pixel_right_position,
        tile_pixel_bottom_position,
        fill=COLOURS[colour_index],
        outline="",
    )


# Add a pixel of a given colour to a given tile.
def add_pixel_to_tile(tile_number, local_pixel_number, colour_index):
    # Get the number of the pixel in all the tiles.

    # Calculate the absolute position of the current tile's first pixel.
    tile_offset = tile_number * PIXELS_PER_TILE

    global_pixel_number = tile_offset + local_pixel_number

    # Update the list of pixels.
    tile_pixels_index[global_pixel_number] = colour_index

    # Get the thumbnail canvas, based on the index.
    thumbnail_canvas = thumbnails_array[tile_number]

    # Draw the pixel on both the paint canvas and the thumbnail canvas.
    draw_on_canvas(paint_canvas, local_pixel_number, colour_index)
    draw_on_canvas(thumbnail_canvas, local_pixel_number, colour_index)


# Print the values of the tiles to the terminal.
def print_array_grid():
    # Print a new line.
    print()
    # For each tile, print an 8 by 8 grid of the pixel values.
    for tile_number in range(current_tile_count):
        # Print the tile number.
        print("tile ", tile_number)

        # Calculate the absolute position of the current tile's first pixel.
        tile_offset = tile_number * PIXELS_PER_TILE

        # For each row in the current tile.
        for row_number in range(ROWS_PER_TILE):
            # Calculate the local position of the current row's first pixel.
            row_offset = row_number * COLUMN_PER_TILE

            # Get the global position of the start and end of the current row
            start_of_row_position = tile_offset + row_offset
            end_of_row_position = start_of_row_position + COLUMN_PER_TILE

            # Print the values of the current row.
            print(tile_pixels_index[start_of_row_position:end_of_row_position])


# Convert a given 2-bit array to a string list of hex values that the
# Game Boy can use.
# Each 8 2-bit values are split into two bites.
# The first byte contains the all the MSB values, the second byte contains
# each LSB.
def convert_to_hex(pixel_array_2_bit):
    # Create an empty string array.
    hex_string_array = []

    # For each tile.
    for tile_number in range(current_tile_count):
        # Calculate the absolute position of the current tile's first pixel.
        tile_offset = tile_number * PIXELS_PER_TILE

        # For each row.
        for row_number in range(ROWS_PER_TILE):
            # Calculate the local position of the current row's first pixel.
            row_offset = row_number * COLUMN_PER_TILE

            # Initialise two empty bytes.
            MSB_byte, LSB_byte = 0, 0

            # For each column.
            for colum_number in range(COLUMN_PER_TILE):
                # Get the index of the pixel in the current tile, at the
                # given row and column.
                current_pixel = tile_offset + row_offset + colum_number

                # Get the value of the current pixel.
                current_pixel_value = pixel_array_2_bit[current_pixel]

                # Split the current value into its MSB and LSB.
                current_pixel_MSB = (current_pixel_value >> 1) & 1
                current_pixel_LSB = (current_pixel_value >> 0) & 1

                # Shift the MSB and LSB to the left.
                MSB_byte <<= 1
                LSB_byte <<= 1

                # Add the MSB and LSB to their respective bytes.
                MSB_byte |= current_pixel_MSB
                LSB_byte |= current_pixel_LSB

            # Set the padding required to achieve the desired format.
            padding = 4

            # Convert the MSB and LSB bytes to strings in the format "0xff".
            MSB_string = f"{MSB_byte:#0{padding}x}"
            LSB_string = f"{LSB_byte:#0{padding}x}"

            # Add the MSB and LSB strings to the array.
            hex_string_array.append(MSB_string)
            hex_string_array.append(LSB_string)

    return hex_string_array


# Register a left click on the paint canvas.
def left_click_on_paint_canvas(mouse_event):
    # Paint the pen colour on the canvas.
    paint(mouse_event.x, mouse_event.y, pen_colour_index)


# Register a right click on the paint canvas.
def right_click_on_paint_canvas(mouse_event):
    # Paint white on the canvas.
    paint(mouse_event.x, mouse_event.y, 0)


# Paint a pixel on the paint canvas, based on the coords of the mouse.
def paint(mouse_x, mouse_y, colour):
    # Create 4 booleans describing if the mouse pointer is within each edge
    # of the canvas.
    inside_left_bound = mouse_x > 0
    inside_right_bound = mouse_x < PAINT_CANVAS_WIDTH
    inside_upper_bound = mouse_y > 0
    inside_lower_bound = mouse_y < PAINT_CANVAS_HEIGHT

    # Create a boolean to describing if the mouse is within all 4 bounds of the
    # canvas, and is thus on the canvas.
    on_canvas = (
        inside_left_bound
        and inside_right_bound
        and inside_upper_bound
        and inside_lower_bound
    )

    # If the mouse is on the canvas.
    if on_canvas:
        # Get the row and column number of the target pixel.
        pixel_column = int(mouse_x / PAINT_CANVAS_X_PIXELS_PER_PIXEL)
        pixel_row = int(mouse_y / PAINT_CANVAS_Y_PIXELS_PER_PIXEL)

        # Calculate the local position of the current row's first pixel.
        row_offset = pixel_row * COLUMN_PER_TILE

        # Get the local pixel number of the target tile pixel.
        pixel_number = row_offset + pixel_column

        # Add the pixel to the tile.
        add_pixel_to_tile(focused_tile, pixel_number, colour)


# Set the value of the global variable "pen_colour_index".
def set_pen_colour_index(colour_index):
    global pen_colour_index
    pen_colour_index = colour_index


# Fills the paint canvas with a target colour index.
def bucket_fill(tile_number, colour_index):
    # Set every pixel in a tile to the given colour.
    for pixel_number in range(PIXELS_PER_TILE):
        add_pixel_to_tile(focused_tile, pixel_number, colour_index)


# Formats a given hex array as a c char array with a given name.
def format_output_string(output_hex_data, array_name):
    # Create a blank string
    output_string = ""

    # Count the number of values in the hex array.
    byte_count = len(output_hex_data)

    # Create the initializer for the c char array.
    c_array_initializer = array_name + "[" + str(byte_count) + "]"

    # Add the type, initializer and open bracket to the output string.
    output_string += "unsigned char " + c_array_initializer + " = {"

    for byte_number in range(byte_count - 1):
        if (byte_number % 8) == 0:
            output_string += "\n    "

        if (byte_number % 16) == 0:
            output_string += "\n    "
            tile_number = int(byte_number / 16)
            output_string += "// Tile "
            output_string += str(tile_number)
            output_string += "\n    "

        output_string += output_hex_data[byte_number]
        output_string += ","

        if not (((byte_number + 1) % 8) == 0):
            output_string += " "

    output_string += str(output_hex_data[-1])
    output_string += "};"

    return output_string


# Check if a given string fits c naming conventions.
def is_valid_c_variable_name(target_string):
    # Define a regular expression pattern.
    valid_name_pattern = r"^[a-zA-Z_][a-zA-Z0-9_]*$"

    # Check if the given string matches the pattern.
    is_valid = re.match(valid_name_pattern, target_string) is not None

    # Return the boolean.
    return is_valid


# Save the current tiles to a selected file.
def save_tiles():
    # Create an array of strings containing the hex data that is to be saved.
    tile_pixels_hex = convert_to_hex(tile_pixels_index)

    # Initialise the prompt that will be given to the user.
    prompt_request = "What should the tile name be?"

    # Initialise the boolean that will require the user to input a valid name
    is_tile_name_valid = False

    # Initialise an the default tile name
    tile_name = "tile"

    # Do not proceed until a valid name is given.
    while not is_tile_name_valid:
        # Ask the user what to name the tile.
        tile_name = simpledialog.askstring(
            "Set Tile Name", prompt_request, initialvalue=tile_name
        )

        # Confirm that the given name is a string.
        tile_name = str(tile_name)

        # replace the spaced with underscores and make the name lower case
        # this will help the name to abide by c variable naming conventions
        tile_name = tile_name.lower()
        tile_name = tile_name.replace(" ", "_")

        # Check that the given name will be a valid variable name when
        # imported into c.
        is_tile_name_valid = is_valid_c_variable_name(tile_name)

        # If the name is not valid, give the user more strict instructions.
        if not is_tile_name_valid:
            prompt_request = "Please abide by c variable naming conventions."

    # Format this given string
    output_string = format_output_string(tile_pixels_hex, tile_name)

    # Create the path of the output folder.
    output_dir = os.getcwd() + "\\output"

    # If the output folder does not exist.
    if not os.path.exists(output_dir):
        # Create the output folder.
        os.mkdir(output_dir)

    # Ask the user to select a save location for the tile data.
    save_path = filedialog.asksaveasfilename(
        defaultextension=".c",
        filetypes=[("c file", "*.c")],
        title="Save File",
        initialdir=output_dir,
        initialfile="tile",
    )

    # Open or create the selected file,
    output_text_file = open(save_path, "w")

    # Write the formatted tile date to the file.
    output_text_file.write(output_string)

    # Close the file.
    output_text_file.close()


# Load in a selected file.
def load_tile_data():
    # Set the default directory to load from to the current working directory.
    load_directory = os.getcwd()

    # Ask the user to select a file to load.
    load_path = filedialog.askopenfilename(
        title="Select file", initialdir=(load_directory)
    )

    # Get the name of the selected file.
    file_name = os.path.basename(load_path)

    # Print a statement to tell the user that the file is being loaded.
    print('Loading file "' + file_name + '".')

    # Load the contents file into a string.
    with open(load_path, "r") as file:
        file_contents = file.read()

    # Initialise a string to format the file contents.
    file_contents_formatted = file_contents

    # Remove everything outside the Braces.
    file_contents_formatted = file_contents_formatted.split("{")[-1]
    file_contents_formatted = file_contents_formatted.split("}")[0]

    # Remove all the new lines and spaces.
    file_contents_formatted = file_contents_formatted.replace("\n", "")
    file_contents_formatted = file_contents_formatted.replace(" ", "")

    # Split the file contents into an array.
    file_contents_array = file_contents_formatted.split(",")

    # Initialise an integer array to hold the integers stores in the file.
    byte_array = []

    for file_entry_string in file_contents_array:
        # Split each entry into just there hexadecimal value.
        file_entry_string = file_entry_string.split("0x")[-1]
        # Convert this hex string into a integer and store it in the array.
        byte_array.append(int(file_entry_string, 16))

    # There are 4 2-bit pixels per 8-bit byte.
    pixel_count = len(byte_array * 4)

    # There are 64 pixels per tile.
    loaded_tile_count = int(pixel_count / PIXELS_PER_TILE)

    tile = 16

    # Create two blank arrays to spit the byte_array in half.
    MSB_byte_array = []
    LSB_byte_array = []

    # Iterate through each element in the byte_array.
    # Even-indexed elements are added to MSB_byte_array,
    # while odd-indexed elements are added to LSB_byte_array.
    for index, element in enumerate(byte_array):
        if (index % 2) == 0:
            MSB_byte_array.append(element)
        else:
            LSB_byte_array.append(element)

    # Create two boolean arrays to hold the values of each 2-bit pixels
    # most and least significant bit.
    MSB_2_bit_array = []
    LSB_2_bit_array = []

    # Iterate through each byte.
    for byte in MSB_byte_array:
        # From 7 to 0, in decreasing by one each loop.
        for i in range(7, -1, -1):
            # Extract each bit from the byte,
            # with the MSB being the first extracted.
            bit = (byte >> i) & 1
            # Add the extracted bit to the array.
            MSB_2_bit_array.append(bit)

    # Iterate through each byte.
    for byte in LSB_byte_array:
        # From 7 to 0, in decreasing by one each loop.
        for i in range(7, -1, -1):
            # Extract each bit from the byte,
            # with the MSB being the first extracted.
            bit = (byte >> i) & 1
            # Add the extracted bit to the array.
            LSB_2_bit_array.append(bit)

    # Create a black int array to combine MSB_2_bit_array and LSB_2_bit_array.
    loaded_2_bit_array = []

    # Populate loaded_2_bit_array by combining
    # MSB_2_bit_array and LSB_2_bit_array.
    for i in range(pixel_count):
        # Get the MSB and LSB of the current pixel
        pixel_MSB = MSB_2_bit_array[i]
        pixel_LSB = LSB_2_bit_array[i]

        # Create a value for each pixel by combining the MSB and LSB.
        pixel_value = (pixel_MSB << 1) | (pixel_LSB)

        # Add the pixel value to the array.
        loaded_2_bit_array.append(pixel_value)

    # remove all the existing tiles.
    # Tile 0 does not get removed.
    remove_all_tiles()

    # Create a new blank tile, for every loaded tile.
    create_n_tiles(loaded_tile_count - 1)

    # Get the global array of pixel values.
    global tile_pixels_index
    for i in range(pixel_count):
        tile_pixels_index[i] = loaded_2_bit_array[i]

    # Reload the thumbnails to reflect the data in the array.
    reload_thumbnails()

    # Set the focus back to the first tile.
    focus_tile(0)


# function to create a new tile, and add its thumbnail under the canvas.
def create_new_tile():
    global current_tile_count
    global max_tiles_created

    # Get the current row by dividing the tile count by 4, rounding down.
    current_row = int(current_tile_count / THUMBNAILS_PER_ROW)

    # If the new tile if being created for the first time.
    if current_tile_count == max_tiles_created:
        # Add 64 zeros to the pixel index.
        for i in range(PIXELS_PER_TILE):
            tile_pixels_index.append(0)

        # If the current tile is devisable by 4, create a new row.
        end_of_row = not (current_tile_count % THUMBNAILS_PER_ROW)
        if end_of_row:
            thumbnail_row_frame = tk.Frame(master=thumbnails_frame)
            thumbnail_rows_array.append(thumbnail_row_frame)

        # Create a frame for the thumbnail canvas, for better boarder control.
        boarder_frame = tk.Frame(
            master=thumbnail_rows_array[current_row], bg="", borderwidth=1
        )

        # Create a new thumbnail.
        thumbnail_canvas = tk.Canvas(
            master=boarder_frame,
            width=THUMBNAIL_CANVAS_WIDTH,
            height=THUMBNAIL_CANVAS_HEIGHT,
            highlightthickness=0,
            bg=WHITE,
        )

        # Add the new thumbnail boarder to the array.
        thumbnail_boarders_array.append(boarder_frame)

        # Add the new thumbnail to the array.
        thumbnails_array.append(thumbnail_canvas)

        # Attach a mouse listener to the new thumbnail.
        thumbnail_canvas.bind(
            "<Button-1>",
            lambda event, cn=current_tile_count: focus_tile(cn),
        )

        max_tiles_created += 1

    # Add the next thumbnail boarder to the screen.
    thumbnail_boarders_array[current_tile_count].pack(side=tk.LEFT)

    # Add the next thumbnail to the screen.
    thumbnails_array[current_tile_count].pack()

    # If the current tile is devisable by 4, show a new row.
    end_of_row = not (current_tile_count % THUMBNAILS_PER_ROW)
    if end_of_row:
        thumbnail_rows_array[current_row].pack(side=tk.TOP, fill=tk.X)

    # Set the focus to the newly created tile.
    focus_tile(current_tile_count)

    # Increment the tile count.
    current_tile_count += 1


# Sets the focus to a given tile.
def focus_tile(tile_number):
    global focused_tile
    # Set the focus to the selected tile.
    focused_tile = tile_number

    # For every boarder in the array
    for i, boarder in enumerate(thumbnail_boarders_array):
        # If the boarder is the selected boarder
        if i == tile_number:
            # Set the colour to red.
            boarder.config(bg="RED")
        else:
            # Set the colour to black.
            boarder.config(bg=BLACK)

    load_into_paint(focused_tile)


# Makes the paint canvas reflect the value of a given tile in the list.
def load_into_paint(tile_number):
    # Calculate the absolute position of the current tile's first pixel.
    tile_offset = tile_number * PIXELS_PER_TILE

    # For every pixel in a tile.
    for local_pixel_number in range(PIXELS_PER_TILE):
        global_pixel_number = tile_offset + local_pixel_number
        colour_index = tile_pixels_index[global_pixel_number]
        # Draw the pixel on the paint canvas.
        draw_on_canvas(paint_canvas, local_pixel_number, colour_index)


# Reloads all the thumbnails to reflect the values of a in the list.
def reload_thumbnails():
    for tile_number in range(current_tile_count):
        # Calculate the absolute position of the current tile's first pixel.
        tile_offset = tile_number * PIXELS_PER_TILE

        # Get the target thumbnail from a list.
        target_thumbnail = thumbnails_array[tile_number]

        # Update the thumbnail to update the height and width.
        target_thumbnail.update()

        # For each pixel on a tile.
        for local_pixel_number in range(PIXELS_PER_TILE):
            global_pixel_number = tile_offset + local_pixel_number
            colour_index = tile_pixels_index[global_pixel_number]
            # Draw the pixel on the thumbnail.
            draw_on_canvas(target_thumbnail, local_pixel_number, colour_index)


# Creates a given number of tiles.
def create_n_tiles(tiles_to_create_count):
    for i in range(tiles_to_create_count):
        create_new_tile()


# Deletes a given number of tiles.
def remove_n_tiles(tiles_to_remove_count):
    for i in range(tiles_to_remove_count):
        delete_last_tile()


# Removes all tiles except the first tile.
def remove_all_tiles():
    remove_n_tiles(current_tile_count - 1)


# Deletes the last tile in the list.
def delete_last_tile():
    global current_tile_count

    # If there is more than one tile on the canvas.
    if current_tile_count > 1:
        # Get the index of the last tile.
        last_thumbnail_index = current_tile_count - 1

        # Set the last tile blank by bucket filling it.
        bucket_fill(last_thumbnail_index, 0)

        # If deleting the current tile, focus the next one.
        if focused_tile == last_thumbnail_index:
            focus_tile(focused_tile - 1)

        # Remove thumbnail.
        target_thumbnail = thumbnails_array[last_thumbnail_index]
        target_thumbnail.pack_forget()

        # Remove thumbnail boarder.
        target_boarder = thumbnail_boarders_array[last_thumbnail_index]
        target_boarder.pack_forget()

        # If deleting the last frame in row
        if not (last_thumbnail_index % THUMBNAILS_PER_ROW):
            thumbnail_row_index = int(last_thumbnail_index / THUMBNAILS_PER_ROW)
            target_thumbnail_row = thumbnail_rows_array[thumbnail_row_index]
            target_thumbnail_row.pack_forget()

        # Decrement the tile count.
        current_tile_count -= 1


# For tkinter element Names, that final word denotes what type the variable is.
# _frame for frame, _button for button, _canvas for canvas, _array for array.

"""
window_frame
    main_frame
        colour_controls_frame
            colour0_button
            colour1_button
            colour2_button
            colour3_button
            fill_button
            save_button
            load_button
        canvas_controls_frame
            paint_canvas
            thumbnail_controls_frame
                tile_controls_frame
                    new_tile_button
                    delete_tile_button
                thumbnails_frame
                    thumbnail_rows_frame[x] = thumbnail_row_frame
                        boarder_frame
                            thumbnails_array[0] = thumbnail_canvas()
                        boarder_frame
                            thumbnails_array[1]
                        boarder_frame
                            thumbnails_array[2]
                        boarder_frame
                            thumbnails_array[3]
                    thumbnail_rows_frame[x]
                        boarder_frame
                            thumbnails_array[0] = thumbnail_canvas()


"""


def create_gui():
    # TODO Rearrange Layout.
    # TODO Set window title.

    global window
    # Initialise window as tkinter class.
    window = tk.Tk()

    # Initialise a "main" frame to hold the canvas and paint controls.
    main_frame = tk.Frame(master=window, width=100, height=100)
    main_frame.pack(fill=tk.BOTH, expand=False)

    # Initialise a colour controls frame to hold different colour buttons and
    # the save, load and fill buttons.
    colour_controls_frame = tk.Frame(master=main_frame, width=2, height=2)
    colour_controls_frame.pack(side=tk.RIGHT, fill=tk.BOTH)

    # Initialise a button that sets the pen colour to white.
    colour_0_button = tk.Button(
        master=colour_controls_frame,
        text="0",
        height=3,
        width=3,
        command=lambda: set_pen_colour_index(0),
        bd=1,
        bg=COLOURS[0],
        fg=COLOURS[3],
    )
    colour_0_button.pack(side=tk.TOP)

    # Initialise a button that sets the pen colour to light gray.
    colour_1_button = tk.Button(
        master=colour_controls_frame,
        text="1",
        height=3,
        width=3,
        command=lambda: set_pen_colour_index(1),
        bd=1,
        bg=COLOURS[1],
        fg=COLOURS[2],
    )
    colour_1_button.pack(side=tk.TOP)

    # Initialise a button that sets the pen colour to dark gray.
    colour_2_button = tk.Button(
        master=colour_controls_frame,
        text="2",
        height=3,
        width=3,
        command=lambda: set_pen_colour_index(2),
        bd=1,
        bg=COLOURS[2],
        fg=COLOURS[1],
    )
    colour_2_button.pack(side=tk.TOP)

    # Initialise a button that sets the pen colour to black.
    colour_3_button = tk.Button(
        master=colour_controls_frame,
        text="3",
        height=3,
        width=3,
        command=lambda: set_pen_colour_index(3),
        bd=1,
        bg=COLOURS[3],
        fg=COLOURS[0],
    )
    colour_3_button.pack(side=tk.TOP)

    # Initialise a button that fills the canvas with the current colour.
    fill_button = tk.Button(
        master=colour_controls_frame,
        text="Fill",
        height=3,
        width=3,
        command=lambda: bucket_fill(focused_tile, pen_colour_index),
    )
    fill_button.pack(side=tk.TOP)

    # Initialise a button that saves the current tiles to a .c file.
    save_button = tk.Button(
        master=colour_controls_frame,
        text="save",
        height=3,
        width=3,
        command=save_tiles,
    )
    save_button.pack(side=tk.TOP)

    # Initialise a button that loads a .c file into the list.
    load_button = tk.Button(
        master=colour_controls_frame,
        text="Load",
        height=3,
        width=3,
        command=load_tile_data,
    )
    load_button.pack(side=tk.TOP)

    # Initialise a frame to hold the paint_canvas and thumbnail_controls_frame.
    canvas_controls_frame = tk.Frame(
        master=main_frame, width=100, height=100, bg="White"
    )
    canvas_controls_frame.pack(fill=tk.BOTH, expand=False, side=tk.LEFT)

    global paint_canvas
    # Initialise the canvas that can be onto.
    paint_canvas = tk.Canvas(
        canvas_controls_frame,
        width=PAINT_CANVAS_WIDTH,
        height=PAINT_CANVAS_HEIGHT,
        bd=0,
        highlightthickness=0,
        bg=WHITE,
    )
    # attach mouse listeners to the paint canvas.
    paint_canvas.bind("<B1-Motion>", left_click_on_paint_canvas)
    paint_canvas.bind("<Button-1>", left_click_on_paint_canvas)
    paint_canvas.bind("<B3-Motion>", right_click_on_paint_canvas)
    paint_canvas.bind("<Button-3>", right_click_on_paint_canvas)

    paint_canvas.pack(side=tk.TOP)

    global thumbnail_controls_frame
    # Initialise a frame to hold tile_controls_frame and thumbnails_frame.
    thumbnail_controls_frame = tk.Frame(
        master=canvas_controls_frame, width=2, height=2, bg="White"
    )
    thumbnail_controls_frame.pack(side=tk.TOP)

    # Initialise a frame to hold tile_controls_frame and thumbnails_frame.
    tile_controls_frame = tk.Frame(
        master=thumbnail_controls_frame, width=2, height=2, bg="White"
    )
    tile_controls_frame.pack(side=tk.TOP)

    # Initialise a button that creates new tiles.
    new_tile_button = tk.Button(
        master=tile_controls_frame,
        width=3,
        height=3,
        bd=1,
        text="New",
        command=create_new_tile,
    )
    new_tile_button.pack(side=tk.LEFT)

    # Initialise a button that deletes the selected tile.
    delete_tile_button = tk.Button(
        master=tile_controls_frame,
        width=3,
        height=3,
        bd=1,
        text="Del",
        command=delete_last_tile,
    )
    delete_tile_button.pack(side=tk.LEFT)

    global thumbnails_frame
    # Initialise a frame to hold an array of thumbnail_row_frames
    thumbnails_frame = tk.Frame(
        master=thumbnail_controls_frame, width=2, height=2, bg="White"
    )
    thumbnails_frame.pack(side=tk.LEFT)


def main():
    # Initialise the GUI.
    create_gui()

    # Create the first tile.
    create_new_tile()

    # Paint the canvas to match the colour pallet.
    bucket_fill(0, 0)

    # Start the main loop of the program.
    window.mainloop()


if __name__ == "__main__":
    main()
