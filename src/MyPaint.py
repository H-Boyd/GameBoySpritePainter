#     _____            _ _          _____                _
#    / ____|          (_) |        / ____|              | |
#   | (___  _ __  _ __ _| |_ ___  | |     _ __ ___  __ _| |_ ___  _ __
#    \___ \| '_ \| '__| | __/ _ \ | |    | '__/ _ \/ _` | __/ _ \| '__|
#    ____) | |_) | |  | | ||  __/ | |____| | |  __/ (_| | || (_) | |
#   |_____/| .__/|_|  |_|\__\___|  \_____|_|  \___|\__,_|\__\___/|_|
#          | |
#          |_|
# By Harry Boyd

from tkinter import *
from tkinter import filedialog as fd
import os
import math


#    _   _       _
#   | \ | |     | |
#   |  \| | ___ | |_ ___  ___
#   | . ` |/ _ \| __/ _ \/ __|
#   | |\  | (_) | ||  __/\__ \
#   |_| \_|\___/ \__\___||___/
#

#Big text made at https://patorjk.com/software/taag/#p=display&f=Graffiti&t=Type%20Something%20

#Curently workinf on reshowing removes sprites

'''Production log

'''

'''Things to do
Put all frames in the same place
Order Everything
16*16 mode
Put variable names in camel case. Variables lower case, functions upper case.
Delete Button

'''

'''
Function names should be lowercase, with words separated by underscores as necessary to improve readability.
Variable names follow the same convention as function names.
mixedCase is allowed only in contexts where that’s already the prevailing style (e.g. threading.py), to retain backwards compatibility.'''
#https://peps.python.org/pep-0008/#function-and-variable-names



'''Order
Title
Notes
Debug
Variables
Functions
Code
OldCode

'''

'''Colours
White      224,248,208
Light Gray 136,192,112
Dark Gray   52,104, 86
Black        8, 24, 32

'''

#   __      __        _       _     _
#   \ \    / /       (_)     | |   | |
#    \ \  / /_ _ _ __ _  __ _| |__ | | ___  ___
#     \ \/ / _` | '__| |/ _` | '_ \| |/ _ \/ __|
#      \  / (_| | |  | | (_| | |_) | |  __/\__ \
#       \/ \__,_|_|  |_|\__,_|_.__/|_|\___||___/
#

mainloop_started = 0

#Static Variables

#Variables I might change
paint_canvas_width, paint_canvas_height = 256, 256

colour_white = ("#e0f8d0")#White
colour_light_gray = ("#88c070")#Light Gray
colour_dark_gray = ("#346856")#Dark Gray
colour_dark_black = ("#081820")#Black

colour_value_array = (colour_white,colour_light_gray,colour_dark_gray,colour_dark_black)

array_of_hex_data = []#this is the array that holds the data of all hex values that represent the sprites

colour_index_array = []#this is the array that colods the 2bit colour of each cell

pen_colour_index = 0#The current 2bit colour of the pen

current_sprite = 0# 0 indexed
max_sprites_created = 0#the amoust of sprites created since the program ran, does not decrement upon sprite deletion
current_sprite_count = 0

thumbnails_array = []
thumbnail_boarders_array = []
thumbnail_rows_array = []

#    ______                _   _
#   |  ____|              | | (_)
#   | |__ _   _ _ __   ___| |_ _  ___  _ __  ___
#   |  __| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
#   | |  | |_| | | | | (__| |_| | (_) | | | \__ \
#   |_|   \__,_|_| |_|\___|\__|_|\___/|_| |_|___/
#

def draw_on_any_canvas(received_canvas,pixel_number,colour_index):
    pixel_x,pixel_y = (pixel_number&7),(pixel_number>>3)

    canvas_width = (received_canvas.winfo_width())

    canvas_width_bit_count = int(math.log2(canvas_width))

    canvas_pixels_per_pixel = canvas_width_bit_count - 3#canvas_width << 3, canvas_width / 8

    #print("received_canvas",received_canvas)

    cx,cy =(pixel_x<<canvas_pixels_per_pixel),(pixel_y<<canvas_pixels_per_pixel)
    ncx,ncy =((pixel_x+1)<<canvas_pixels_per_pixel),((pixel_y+1)<<canvas_pixels_per_pixel)

    received_canvas.create_polygon(cx,cy, cx,ncy,ncx,ncy,ncx,cy,fill=colour_value_array[colour_index])

def place_square_on_paint_canvas(sprite_number,pixel_number,colour_index):

    offset_number = (sprite_number<<6)| pixel_number#pixel_number + (64*sprite_number)
    colour_index_array[offset_number] = colour_index#update the array with the added value

    draw_on_any_canvas(paint_canvas,pixel_number,colour_index)
    draw_on_any_canvas(thumbnails_array[sprite_number],pixel_number,colour_index)


def print_array_grid():
    print()
    for i in range(current_sprite_count<<3):#prints 8 lines for every sprite
        print(colour_index_array[i*8:((i+1)*8)])#prints 8 values from the apropriate place in the array

def make_2bit_format():
    '''
    This function gets the array of 2 bit values, and converts it into the format the Gameboy is after
    it gets each 2bit 8 pixels and splits it into two bytes. The first containing the MSB of each pixel, and the other the LSB
    '''

    global array_of_hex_data
    array_of_hex_data = []


    for s in range(current_sprite_count):# for each row of 8 pixels, s = sprites
        for r in range(8):# for each row of 8 pixels
            #print(testData[b]&1)

            MSB_byte = 0
            LSB_byte = 0
            for b in range(8):
                MSB_byte = ((MSB_byte<<1)|(colour_index_array[(s<<6)+b+(r<<3)]>>1))#shift the Byte along and add the desired bit to the LSB
                LSB_byte = ((LSB_byte<<1)|(colour_index_array[(s<<6)+b+(r<<3)]&1))
            array_of_hex_data.append(format(hex(MSB_byte)))
            array_of_hex_data.append(format(hex(LSB_byte)))


def pixel_paint(event):

    if((event.x > 0) and (event.x < paint_canvas_width) and (event.y > 0) and (event.y < paint_canvas_height)):

        pixel_x,pixel_y = ((event.x>>5)&7),((event.y>>5)&7) #  / 32 to go from 0-256 to 0-8 #Pixel x and y
        

        pixel_number = (pixel_y<<3)|pixel_x#convert the x and y into One pixel_numberber
        place_square_on_paint_canvas(current_sprite,pixel_number,pen_colour_index,)

        #print_array_grid()


def set_pen_colour_index(colour_index):
    global pen_colour_index
    pen_colour_index = colour_index




def fill_paint_canvas(sprite_number,colour_index):
    paint_canvas.create_polygon(0,0, 0,paint_canvas_height,paint_canvas_width,paint_canvas_height,paint_canvas_width,0,fill=colour_value_array[colour_index])#Draws a polygon over the drawing canvas



    thumbnail_height = paint_canvas_height>>3
    thumbnail_width = paint_canvas_width>>3
    thumbnails_array[sprite_number].create_polygon(0,0, 0,thumbnail_height,thumbnail_width,thumbnail_height,thumbnail_width,0,fill=colour_value_array[colour_index])#Draws a polygon over the drawing canvas

    for i in range(64):
        i  = (sprite_number<<6)|i #i + (64*sprite_number) offsets the value i'm changing to the correct amount
        colour_index_array[i] = colour_index
    #print_array_grid()


def save():
    make_2bit_format()
    print(array_of_hex_data)
    output_string = "unsigned char Hat[] ={"


    ByteCount = (current_sprite_count<<4)#16 Bytes Per Sprite
    for i in range(ByteCount-1):
        output_string = output_string +str(array_of_hex_data[i])+","
    output_string = output_string +str(array_of_hex_data[-1])+"}"

    output_text_file = open('SpriteOutput.c','w')
    output_text_file.write(output_string)


def load_sprite_data():
    load_path = fd.askopenfilename(title="Select file",initialdir=os.getcwd())
    print(load_path)

    FileName = load_path.split('\\')[-1]
    Name = FileName.split('.')[0]
    #JPGName = Name +'.JPG'

    with open(load_path, 'r') as file:#open the Desired file and get the contents of it as a string
        file_contence = file.read().replace('\n', '')

    #print(file_contence)

    file_contence = file_contence.split('{')[1]#Just get the text inside the braces of the first variable as this file should only contain one char array
    file_contence = file_contence.split('}')[0]
    file_contence= file_contence.replace(" ","")#Remove all the spaces

    LoadHexArray = file_contence.split(',')#Split the string at the commas

    IntArray = []
    for H in LoadHexArray:
        IntArray.append(int(H,0))#Populate an array of the values represented by the hex array

    print(IntArray)

    MSBs = []
    for I in range((len(IntArray)>>1)):#For Every other value in int array
        I = I<<1 # Double I, so I can just get every over value
        for P in range(8):#This bit goes through each bit in a byte starting at the MSB
            MSBs.append(((IntArray[I]>>(7-P)) & 1))#Populates an array of boolean values of the MSB of Each Pixel
    LSBs = []
    for I in range((len(IntArray)>>1)):#For Every other value in int array
        I = (I<<1)|1 # Double I, and ads one, so I can just get every second value
        for P in range(8):#This bit goes through each bit in a byte starting at the MSB
            LSBs.append(((IntArray[I]>>(7-P)) & 1))#Populates an array of boolean values of the MSB of Each Pixel
            
    pixel_count = int(len(MSBs))

    global colour_index_array
    colour_index_array = []
    for p in range(pixel_count):
        colour_index_array.append(((MSBs[p]<<1)|(LSBs[p])))

    load_into_paint(0)




'''
Make Row sow acordinbgly
Make new Tile Focused



'''
def create_new_sprite():
    '''This function creates a new blank sprite and adds another thumb nail under the canvas
    '''

    global current_sprite_count
    global max_sprites_created

    print(current_sprite_count,max_sprites_created)

    current_row= (current_sprite_count>>2)
    
    if(current_sprite_count == max_sprites_created):#If all created sprites are shown, make a new one
        for I in range(64):
            colour_index_array.append(0)

        if(not(current_sprite_count & 3 )):#create a new row if needed
            thumbnail_row_frame = Frame(master=thumbnails_frame)
            thumbnail_rows_array.append(thumbnail_row_frame)

        boarder_frame = Frame(master=thumbnail_rows_array[current_row], bg="black",borderwidth = 1)#this is just to put a boarder around the thumbnail without fixing it to the canvas


        thumbnail_canvas = Canvas(master=boarder_frame, width=paint_canvas_width>>3, height=paint_canvas_height>>3,highlightthickness=0, bg=colour_white)
        #thumbnail_canvas.pack()
        #boarder_frame.pack(side=LEFT)

        thumbnail_boarders_array.append(boarder_frame)

        thumbnails_array.append(thumbnail_canvas)

        thumbnail_canvas.bind("<Button-1>",lambda event:thumbnail_clicked(thumbnail_canvas))


        
        max_sprites_created = max_sprites_created+1
    else:#if sprites exist that are not shown, show one of them
        pass
        
        
        
    thumbnail_boarders_array[current_sprite_count].pack(side=LEFT)
    thumbnails_array[current_sprite_count].pack()
    if((current_sprite_count%4)==0):#create a new row if needed
        thumbnail_rows_array[current_row].pack(side=TOP,fill=X)
        
        
        #Reshow Sprites
        
        
    print("Here",current_sprite_count)
    
    focus_thumbnail(current_sprite_count)  
    
    current_sprite_count = current_sprite_count + 1
    




def get_canvasl_number(thumbnail_position):
    # Gets a string in the format (<tkinter.Canvas object .!frame.!frame2.!frame.!frame2.!frame.!frame.!canvas>,)
    #print(thumbnail_position)

    tempRow = thumbnail_position.split('.')[6][6:]#get the 6th element and removes the first 6 characters
    if tempRow == "":tempRow = "1"
    tempRow = (int(tempRow)) - 1 #turns it into an int and 0 indexes it

    tempCol = thumbnail_position.split('.')[7][6:]
    if tempCol == "":tempCol = "1"
    tempCol = (int(tempCol)) - 1

    return (tempRow<<2)|tempCol


def focus_thumbnail(thumbnail_number):
    print("focus_thumbnail",thumbnail_number)
    global current_sprite
    
    current_sprite = thumbnail_number
    
    
    
    for i in range(len(thumbnail_boarders_array)):#sets the colours of the boarders
        if (i == thumbnail_number):
            thumbnail_boarders_array[i].config(bg="RED")
        else:
            thumbnail_boarders_array[i].config(bg=colour_dark_black)
    
    if (mainloop_started):
        print("",current_sprite)
        load_into_paint(current_sprite)
            
    

def thumbnail_clicked(*arg):

    selected_thumbnail = get_canvasl_number(str(arg))
    
    focus_thumbnail(selected_thumbnail)
    


def load_into_paint(sprite_number):
    print("sprite:",sprite_number)
    for p in range(64):
        
        draw_on_any_canvas(paint_canvas,p,colour_index_array[(sprite_number<<6)|p])# P + 64*sprite_number 


def delete():
    global current_sprite_count
    

    
    if(current_sprite_count>1):


            
            
        
        
        last_thumbnail_index = current_sprite_count-1
        
        fill_paint_canvas(last_thumbnail_index,0)
        
        if(current_sprite == last_thumbnail_index):#if deleting the current sprite, focus the next one 
            focus_thumbnail(current_sprite - 1)
        
        #print(current_sprite_count)
        #print(last_thumbnail_index)
        #print(len(thumbnails_array))

        thumbnails_array[last_thumbnail_index].pack_forget()#Remove thumbnail.

        thumbnail_boarders_array[last_thumbnail_index].pack_forget()#Remove thumbnail boarder.


        if (not(last_thumbnail_index & 3)):#if deleting the last frame in row
            thumbnailRowIndex = last_thumbnail_index>>2
            thumbnail_rows_array[thumbnailRowIndex].pack_forget()

        
        current_sprite_count = current_sprite_count - 1#update how many sprites we have

        #thumbnail_boarders_array[last_thumbnail_index].config(bg="Green")

#    ______                   _
#   |  ____|                 (_)
#   | |__ _ __ __ _ _ __ ___  _ _ __   __ _
#   |  __| '__/ _` | '_ ` _ \| | '_ \ / _` |
#   | |  | | | (_| | | | | | | | | | | (_| |
#   |_|  |_|  \__,_|_| |_| |_|_|_| |_|\__, |
#                                      __/ |
#                                     |___/

#For tkinter element Names, suffix _frame for frame, _button for button, _canvas for canvas, _array for array

'''
window_frame
    main_frame
        colour_controlls_frame
            colour0_button
            colour1_button
            colour2_button
            colour3_button
            fill_button
            save_button
            load_button
        canvas_controlls_frame
            paint_canvas
            thumbnailControlls_frame
                spriteControlls_frame
                    newSprite_button
                    deleteSprite_button
                thumbnails_frame
                    thumbnail_rows_array[x] = thumbnail_row_frame
                        boarder_frame
                            thumbnails_array[0] = thumbnail_canvas(Function Generated, start with just 1 frame)
                        boarder_frame
                            thumbnails_array[1]
                        boarder_frame
                            thumbnails_array[2]
                        boarder_frame
                            thumbnails_array[3]
                    thumbnailRows_frame[x]
                        boarder_frame
                            thumbnails_array[0] = thumbnail_canvas(Function Generated, start with just 1 frame)


'''

window = Tk()

main_frame = Frame(master=window, width=100, height=100, bg="White")
main_frame.pack(fill=BOTH, expand=False)

colour_controlls_frame = Frame(master=main_frame, width=2, height=2, )
colour_controlls_frame.pack(side=RIGHT,fill=BOTH )

colour0_button = Button(master=colour_controlls_frame, text="0", height=3,width=3,command=lambda: set_pen_colour_index(0),bd=1,bg=colour_value_array[0],fg=colour_value_array[3])
colour0_button.pack(side=TOP)

colour1_button = Button(master=colour_controlls_frame, text="1", height=3,width=3,command=lambda: set_pen_colour_index(1),bd=1,bg=colour_value_array[1],fg=colour_value_array[2])
colour1_button.pack(side=TOP)

colour2_button = Button(master=colour_controlls_frame, text="2", height=3,width=3,command=lambda: set_pen_colour_index(2),bd=1,bg=colour_value_array[2],fg=colour_value_array[1])
colour2_button.pack(side=TOP)

colour3_button = Button(master=colour_controlls_frame, text="3", height=3,width=3,command=lambda: set_pen_colour_index(3),bd=1,bg=colour_value_array[3],fg=colour_value_array[0])
colour3_button.pack(side=TOP)

fill_button = Button(master=colour_controlls_frame, text="Fill", height=3,width=3,command=lambda: fill_paint_canvas(current_sprite,pen_colour_index))
fill_button.pack(side=TOP)

save_button = Button(master=colour_controlls_frame, text="save", height=3,width=3,command=save)
save_button.pack(side=TOP)

load_button = Button(master=colour_controlls_frame, text="Load", height=3,width=3,command=load_sprite_data)
load_button.pack(side=TOP)

canvas_controlls_frame = Frame(master=main_frame, width=100, height=100, bg="White")
canvas_controlls_frame.pack(fill=BOTH, expand=False,side=LEFT)

paint_canvas = Canvas(canvas_controlls_frame, width=paint_canvas_width, height=paint_canvas_height,bd=0,highlightthickness=0, bg="White")#Make canvas to put onto window
paint_canvas.bind('<B1-Motion>', pixel_paint)
paint_canvas.bind('<Button-1>', pixel_paint)
paint_canvas.pack(side=TOP)

thumbnailControlls_frame = Frame(master=canvas_controlls_frame, width=2, height=2,bg="White")
thumbnailControlls_frame.pack(side=TOP)

spriteControlls_frame = Frame(master=thumbnailControlls_frame, width=2, height=2, bg="White")
spriteControlls_frame.pack(side=TOP)

newSprite_button = Button(master=spriteControlls_frame, width=3, height=3,bd=1,text = "New",command = create_new_sprite)#Make canvas to put onto window
newSprite_button.pack(side = LEFT)

deleteSprite_button = Button(master=spriteControlls_frame, width=3, height=3,bd=1,text = "Del",command = delete)#Make canvas to put onto window
deleteSprite_button.pack(side = LEFT)

thumbnails_frame = Frame(master=thumbnailControlls_frame, width=2, height=2, bg="White")
thumbnails_frame.pack(side = LEFT)


create_new_sprite()#Just to make sure there is at least on sprite

#     _____          _
#    / ____|        | |
#   | |     ___   __| | ___
#   | |    / _ \ / _` |/ _ \
#   | |___| (_) | (_| |  __/
#    \_____\___/ \__,_|\___|
#
#




fill_paint_canvas(0,0)
#focus_thumbnail(1)

#place_square_on_paint_canvas(12,3)
#draw_on_any_canvas(DrawingZone,16)


mainloop_started = 1
window.mainloop()
