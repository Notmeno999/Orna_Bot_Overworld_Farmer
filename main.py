from pygetwindow import getWindowsWithTitle
from PIL import ImageGrab, Image, ImageDraw
import numpy as np
import cv2
import time
import pyautogui
import pytesseract
import random
from collections import namedtuple
import datetime
import pygetwindow as gw

# Functions

#===================================================================================#

# Function to compare two images and highlight the differences in red
def compare_images(image1_path, image2_path):
    # Open the images
    image1 = Image.open(image1_path)
    image2 = Image.open(image2_path)

    # Ensure the images have the same size
    if image1.size != image2.size:
        raise ValueError("The images must have the same size.")

    # Create a new image with the same size and black background
    diff_image = Image.new("RGB", image1.size, "black")

    # Load the pixel data for both images
    pixels1 = image1.load()
    pixels2 = image2.load()
    pixels_diff = diff_image.load()

    # Compare the pixels and mark the differences in red
    for x in range(image1.width):
        for y in range(image1.height):
            pixel1 = pixels1[x, y]
            pixel2 = pixels2[x, y]

            if pixel1 != pixel2:
                pixels_diff[x, y] = (255, 0, 0)  # Red

    # Save the resulting image
    diff_image.save("differences.png")

# Function to find and return the coordinates of the game window
def window_coords():
    # Get all open windows
    windows = gw.getAllTitles()

    # Find the window with the specified title
    for window in windows:
        if "LDPlayer" in window:
            # Get the window object
            app_window = gw.getWindowsWithTitle(window)[0]

            # Return the window coordinates as a tuple
            return (app_window.left, app_window.top, app_window.left + app_window.width, app_window.top + app_window.height)

    # If the app window is not found, return None
    return None

# Function to get coordinates for a square around the game window center
def get_square_coords(square_size,window_coords):

    if window_coords is None:
        return None  # Return None if the window coordinates are not found

    # Calculate the center coordinates of the window
    center_x = (window_coords[0] + window_coords[2]) // 2
    center_y = (window_coords[1] + window_coords[3]) // 2

    # Calculate the half size of the square
    half_size = square_size // 2

    # Calculate the coordinates of the square
    square_coords = (
        center_x - half_size,
        center_y - half_size,
        center_x + half_size,
        center_y + half_size
    )

    return square_coords

# Function to find red pixels in the final image
def find_red_pixels(file_path="final_image.png"):
    # Open the image
    image = Image.open(file_path)
    width, height = image.size

    red_pixels = []

    # Iterate over each pixel in the image
    for x in range(width):
        for y in range(height):
            # Get the RGB values of the pixel
            r, g, b = image.getpixel((x, y))

            # Check if the pixel is red (you can adjust this threshold as needed)
            if r > 200 and g < 100 and b < 100:
                red_pixels.append((x, y))

    return red_pixels

# Function to click on a random red pixel position
def click_random_red_pixel(red_pixels):
    # Check if any red pixels were found
    if red_pixels:
        # Choose a random red pixel
        random_pixel = random.choice(red_pixels)
        
        click_x, click_y = random_pixel[0], random_pixel[1]
        pyautogui.click(click_x, click_y)
        print(f"Clicked at random red pixel: ({click_x}, {click_y})")
        
        return random_pixel
    else:
        return None

# Function to modify the image based on given coordinates
def modify_image(image_path, coordinates):
    # Open the image
    image = Image.open(image_path)
    
    # Convert the image to RGB mode
    image = image.convert("RGB")
    
    # Get the width and height of the image
    width, height = image.size
    
    # Create a new image with black pixels
    new_image = Image.new("RGB", (width, height), color="black")
    
    # Iterate over the coordinates and copy the pixels from the original image
    for x in range(coordinates[0], coordinates[2]):
        for y in range(coordinates[1], coordinates[3]):
            # Check if the coordinates are within the image boundaries
            if 0 <= x < width and 0 <= y < height:
                # Get the pixel from the original image
                pixel = image.getpixel((x, y))
                
                # Set the pixel in the new image
                new_image.putpixel((x, y), pixel)
    
    # Save the new image as "final_image.png"
    new_image.save("final_image.png")

# Function to capture a screenshot of the full screen
def capture_full_screen(screenshot_path):
    try:
        with ImageGrab.grab() as screenshot:
            screenshot.save(screenshot_path)
            print(f"Screenshot saved at: {screenshot_path}")
    except Exception as e:
        print("An error occurred:", str(e))

# Function to find and click specific text on the game screen
def find_and_click_text(string, window_coords=window_coords(), threshold=0.6,):
    # Get the coordinates of the game window
    if window_coords is None:
        print("Game window not found.")
        return None, None
    
    # Take a screenshot of the window area and save it
    screenshot_path = "screenshot_to_text.png"
    screenshot = pyautogui.screenshot(region=window_coords)
    screenshot.save(screenshot_path)
    print(f"Screenshot saved as: {screenshot_path}")
    screenshot = np.array(screenshot)
    
    # Convert the screenshot to grayscale
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # Perform OCR on the grayscale image
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    # Find the location of the string in the OCR result
    for i, match in enumerate(data["text"]):
        if match.lower() == string.lower():
            conf = float(data["conf"][i])
            if conf >= threshold:
                # Click on the center of the found text
                x = data["left"][i] + data["width"][i] // 2 + window_coords[0]
                y = data["top"][i] + data["height"][i] // 2 + window_coords[1]
                pyautogui.click(x, y)
                print(f"Clicked on text '{string}' at: ({x}, {y})")
                return x, y
    
    # If the text is not found, return None
    print(f"'{string}' not found")
    return None, None

# Function to find specific text on the game screen
def only_find_text(string, window_coords=window_coords(), threshold=0.6,):
    # Get the coordinates of the game window
    if window_coords is None:
        print("Game window not found.")
        return None, None
    
    # Take a screenshot of the window area and save it
    screenshot_path = "screenshot_to_text.png"
    screenshot = pyautogui.screenshot(region=window_coords)
    screenshot.save(screenshot_path)
    print(f"Screenshot saved as: {screenshot_path}")
    screenshot = np.array(screenshot)
    
    # Convert the screenshot to grayscale
    gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    
    # Perform OCR on the grayscale image
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    # Find the location of the string in the OCR result
    for i, match in enumerate(data["text"]):
        if match.lower() == string.lower():
            conf = float(data["conf"][i])
            if conf >= threshold:
                # Click on the center of the found text
                x = data["left"][i] + data["width"][i] // 2 + window_coords[0]
                y = data["top"][i] + data["height"][i] // 2 + window_coords[1]
                print(f"Found text '{string}' at: ({x}, {y})")
                return x, y
    
    # If the text is not found, return None
    return None, None

# Function to find and click specific images on the game screen
def find_and_click_image(image_path, confidence=0.6):
    try:
        # Locate the image on the screen
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        
        if location is not None:
            # Get the center coordinates of the image
            x, y, width, height = location
            center_x = x + width // 2
            center_y = y + height // 2
            
            # Move the mouse to the center of the image and click
            pyautogui.moveTo(center_x, center_y)
            pyautogui.click()
        else:
            print(image_path,"not found on screen.")
    except Exception as e:
        print("An error occurred:", str(e))

# Function to find and click specific images on the game screen
def find_and_hold_image(image_path, confidence=0.6, hold_duration=0.8):
    try:
        # Locate the image on the screen
        location = pyautogui.locateOnScreen(image_path, confidence=confidence)
        
        if location is not None:
            # Get the center coordinates of the image
            x, y, width, height = location
            center_x = x + width // 2
            center_y = y + height // 2
            
            # Move the mouse to the center of the image and click
            pyautogui.moveTo(center_x, center_y)
            
            # Hold the left click for the specified duration
            pyautogui.mouseDown(button='left')
            time.sleep(hold_duration)
            pyautogui.mouseUp(button='left')

            # Return the coordinates found
            return center_x, center_y
        else:
            print(image_path, "not found on screen.")
    except Exception as e:
        print("An error occurred:", str(e))

# Function to perform the specified actions to find ennemies
def find_ennemies(square):
    try:
        # Step 1: Take a first full screenshot
        capture_full_screen("full_screen_1.png")
        
        # Step 2: Click on the filter image
        find_and_click_image("filter.png",0.9)

        time.sleep(0.1)
        
        # Step 3: Click on "monsters" text
        monsters_x, monsters_y = find_and_click_text("monsters")

        # Step 4: Click on the cancel image
        find_and_click_image("cancel.png",confidence=0.8)

        time.sleep(0.1)
        
        # Step 5: Take a second full screenshot
        capture_full_screen("full_screen_2.png")

        # Step 6: Click on the filter image
        find_and_click_image("filter.png",0.9)

        time.sleep(0.1)

        # Step 7: Click on "monsters" text again
        if monsters_x is not None and monsters_y is not None:
            pyautogui.click(monsters_x,monsters_y)

        # Step 8: Click on the cancel image again
        find_and_click_image("cancel.png",confidence=0.8)

        # Step 9: Compare images
        compare_images("full_screen_1.png", "full_screen_2.png")

        # Step 10: Remove unnecessary part

        modify_image("differences.png",square)

    except Exception as e:
        print("An error occurred:", str(e))

        
# Function to scroll down above the cancel button
def scroll_down_above_cancel():
    try:
        # Find the image on the screen
        location = pyautogui.locateOnScreen("cancel.png")
        
        if location is not None:
            # Get the center coordinates of the image
            x, y, width, height = location
            image_center = (x + width // 2, y + height // 2)
            
            # Modify the center coordinates to move up by 100 pixels
            starting_point = (image_center[0], image_center[1] - 100)

            # Perform scroll down action at starting point
            pyautogui.moveTo(starting_point[0], starting_point[1])
            
            # Scroll down by 4 steps to ensure reliability
            for _ in range(4):
                pyautogui.scroll(-99999)  # Scroll down by 1 unit
                time.sleep(0.1)  # Add a small delay between each scroll step
            
            print("Scroll down successful!")
        else:
            print("Image not found on the screen.")
    except Exception as e:
        print("An error occurred:", str(e))

image_paths = [
    "lucky_coin.png",
]

image_texts = [
    "Dowsing",
    "EXP",
    "Affinity",
    "Occult",
    "Silver",
]

# Function to activate buffs
def buffer():
    global last_execution_time
    find_and_click_image("items.png")
    time.sleep(0.1)
    scroll_down_above_cancel()
    for image_path in image_paths:
        find_and_click_image(image_path,confidence=0.8)
        time.sleep(0.1)
    for text in image_texts:
        find_and_click_text(text,threshold=0.7)
        time.sleep(0.1)
    # The Torch text is harder to find so threshold is 0.4
    find_and_click_text("Torch", threshold=0.4)
    find_and_click_image("cancel.png",confidence=0.8)
    last_execution_time = time.time()  # Update the last execution time

#===================================================================================#
# variables

window_coords = window_coords()
square = get_square_coords(400,window_coords)


buffer_bool = False  # Set this variable to True or False based on your requirement

last_execution_time = time.time()

# Get the start time of the script
start_time = time.time()

# Initialize the main loop count
main_loop_count = 0

# Initialize the battle click count
battle_click_count = 0


#===================================================================================#

# wait before execution
time.sleep(2)
try:
    if buffer_bool:  # Check the buffer_bool variable
        # Initial execution of buffer only if buffer_bool is True
        buffer()
    while True:
        print("===============")
        print("Loop #"+str(main_loop_count+1)+" begins")
        print("===============")
        current_time = time.time()
        current_date_time = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        print("Current Date and Time:", current_date_time)
        # Calculate and print the total time the script has been running
        elapsed_time = current_time - start_time
        print("Total Time Running: {:.2f} seconds".format(elapsed_time))

#===================================================================================#
        
        # Check if it has been 60 minutes since the last execution of buffer
        if current_time - last_execution_time >= 60 * 60:
            buffer()
#===================================================================================#
        # Heal
        find_and_hold_image("items.png")
        
#===================================================================================#
        # Find the ennemies position
        find_ennemies(square)

        # Find red_pixels
        red_pixels = find_red_pixels()

        # Click the ennemies
        click_random_red_pixel(red_pixels)

#===================================================================================#
        #Click Battle
        time.sleep(0.2)
        result_x, result_y = find_and_click_text("BATTLE")
        if result_x is not None and result_y is not None:
            battle_click_count += 1  # Increment battle click count
            print("Battle Click Count:", battle_click_count)  # Print the battle click count for each click
#===================================================================================#
        # IN_Battle Loop
        found = False
        while True:
            try:
                if not found:
                    attack_x,attack_y = only_find_text("BOLT",threshold=0.8)
                if attack_x is not None and attack_y is not None:
                    pyautogui.click(attack_x,attack_y)
                    found = True
                
                result_x, result_y = find_and_click_text("CONTINUE")
                
                # Add a condition to exit the loop
                if result_x is not None and result_y is not None:
                    print("IN_Battle Loop interrupted after clicking 'CONTINUE'")
                    break  # Exit the loop when the condition is met
                
                # Just in case it clicked a wrong position:
                find_and_click_image("cancel.png",confidence=0.8)
                
            except Exception as e:
                if isinstance(e, KeyboardInterrupt):
                    print("IN_Battle Loop interrupted by user.")
                    break  # Exit the loop when the user interrupts the program
        
#===================================================================================#
        
        # Just in case it clicked a wrong position:
        find_and_click_image("cancel.png",confidence=0.8)
        
#===================================================================================#
        
        main_loop_count += 1  # Increment the main loop count

except KeyboardInterrupt:
    print("Program interrupted by user.")

