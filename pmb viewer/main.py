import cv2
import ast
import numpy as np
import sys
import os
from functools import lru_cache


def main():
    # Set fixed window size
    WINDOW_WIDTH = 1000
    WINDOW_HEIGHT = 800
    
    # Check if filename was provided as command line argument
    if len(sys.argv) > 1:
        # Use the full path from command line argument
        full_path = sys.argv[1]
        # Remove the extension if it exists
        name = os.path.splitext(os.path.basename(full_path))[0]
        file_path = full_path
    else:
        # Fall back to manual input if no arguments provided
        name = input("Enter the name of the image> ")
        file_path = f"{name}.pmb"
    
    # Load PMB file more efficiently
    try:
        with open(file_path, "r") as f:
            content = f.readlines()
            name = content[0].strip()
            width, height = map(int, content[1].split(","))
    except Exception as e:
        print(f"Error loading file: {e}")
        return

    # Check if file has enough content
    if len(content) < 3:
        print("Invalid PMB file format")
        return

    # Parse first pixel to determine color depth
    linet = content[2].strip()
    fieldt = linet.replace("N", "")
    try:
        tupt = ast.literal_eval(fieldt)
        pixeldatat = list(tupt)
        pixeldatat[0], pixeldatat[2] = pixeldatat[2], pixeldatat[0]
        channels = len(pixeldatat)
    except Exception as e:
        print(f"Error parsing pixel data: {e}")
        return

    # Create image with appropriate channels
    if channels == 4:
        original_image = np.ones((height, width, 4), dtype=np.uint8) * 255
    else:
        original_image = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Parse pixel data more efficiently
    y = 0
    x = 0

    for i in range(2, len(content)):
        line = content[i].strip()

        if y >= height:
            break

        if "N" in line:
            y += 1
            x = 0  # reset x at new line
        
        field = line.replace("N", "")
        try:
            tup = ast.literal_eval(field)
            pixeldata = list(tup)
            pixeldata[0], pixeldata[2] = pixeldata[2], pixeldata[0]

            if y < height and x < width:
                original_image[y, x] = pixeldata
            else:
                print(f"Warning: Pixel ({x}, {y}) out of bounds")
        except Exception as e:
            print(f"Error parsing line {i}: {e}")

        if "N" not in line:
            x += 1

    # Create named window with fixed size
    window_name = f"{name} ({width}x{height})"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Initial zoom and pan settings
    zoom = 1.0
    pan_x = 0
    pan_y = 0
    is_fullscreen = False
    should_quit = False
    
    # Variables to track if we need to update the display
    needs_update = True
    last_display = None
    
    # Create cache for resized images
    @lru_cache(maxsize=8)
    def get_resized_image(scale, w, h):
        """Cache resized images for better performance"""
        new_w, new_h = int(width * scale), int(height * scale)
        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
        return cv2.resize(original_image, (new_w, new_h), interpolation=interpolation)
    
    def update_display():
        nonlocal last_display
        
        # Calculate scale to fit image in window while preserving aspect ratio
        scale_x = WINDOW_WIDTH / width
        scale_y = WINDOW_HEIGHT / height
        base_scale = min(scale_x, scale_y) * 0.9  # 90% of fit size to leave some padding
        
        # Apply zoom factor
        current_scale = base_scale * zoom
        
        # Calculate new dimensions
        new_width = int(width * current_scale)
        new_height = int(height * current_scale)
        
        # Get resized image from cache
        resized = get_resized_image(current_scale, new_width, new_height)
        
        # Create a black canvas for the current window size
        canvas = np.zeros((WINDOW_HEIGHT, WINDOW_WIDTH, 3), dtype=np.uint8)
        
        # Calculate center position
        x_center = (WINDOW_WIDTH - new_width) // 2 + pan_x
        y_center = (WINDOW_HEIGHT - new_height) // 2 + pan_y
        
        # Ensure the image is at least partially visible
        x_center = max(min(x_center, WINDOW_WIDTH), -new_width + 1)
        y_center = max(min(y_center, WINDOW_HEIGHT), -new_height + 1)
        
        # Calculate the region of the canvas where the image will be placed
        x_start = max(0, x_center)
        y_start = max(0, y_center)
        x_end = min(x_center + new_width, WINDOW_WIDTH)
        y_end = min(y_center + new_height, WINDOW_HEIGHT)
        
        # Calculate the region of the resized image to be copied
        img_x_start = max(0, -x_center)
        img_y_start = max(0, -y_center)
        img_x_end = img_x_start + (x_end - x_start)
        img_y_end = img_y_start + (y_end - y_start)
        
        # Copy the visible portion of the image to the canvas
        if x_end > x_start and y_end > y_start:
            # Handle different channel counts
            if resized.shape[2] == 4:  # If has alpha channel
                # Extract RGB and alpha channels
                rgb = resized[img_y_start:img_y_end, img_x_start:img_x_end, :3]
                alpha = resized[img_y_start:img_y_end, img_x_start:img_x_end, 3:4] / 255.0
                # Apply alpha blending - vectorized operation for better performance
                canvas_region = canvas[y_start:y_end, x_start:x_end]
                canvas[y_start:y_end, x_start:x_end] = (rgb * alpha + canvas_region * (1 - alpha))
            else:
                canvas[y_start:y_end, x_start:x_end] = resized[img_y_start:img_y_end, img_x_start:img_x_end]
        
        last_display = canvas
        return canvas
    
    # Handle mouse events for zooming
    def mouse_callback(event, x, y, flags, param):
        nonlocal zoom, pan_x, pan_y, needs_update
        
        if event == cv2.EVENT_MOUSEWHEEL:
            # Extract wheel delta (positive for up/zoom in, negative for down/zoom out)
            wheel_delta = flags > 0
            
            # Calculate zoom center (relative to image center)
            zoom_center_x = x - WINDOW_WIDTH // 2 - pan_x
            zoom_center_y = y - WINDOW_HEIGHT // 2 - pan_y
            
            # Update zoom factor
            old_zoom = zoom
            if wheel_delta:
                zoom *= 1.1  # Zoom in
            else:
                zoom = max(0.1, zoom / 1.1)  # Zoom out with minimum limit
            
            # Adjust pan to keep the point under cursor fixed
            zoom_ratio = zoom / old_zoom
            pan_x = int(x - (x - pan_x) * zoom_ratio)
            pan_y = int(y - (y - pan_y) * zoom_ratio)
            
            # Mark for update
            needs_update = True
    
    # Handle window closure
    def on_window_close(window_name):
        nonlocal should_quit
        should_quit = True
    
    # Set mouse callback
    cv2.setMouseCallback(window_name, mouse_callback)
    
    # Initial display
    display_image = update_display()
    cv2.imshow(window_name, display_image)
    
    # Show help message
    help_message = """
    Controls:
    • Mouse wheel: Zoom in/out
    • Arrow keys: Pan when zoomed in
    • F: Toggle fullscreen
    • R: Reset view
    • Q: Quit
    • X button: Close window
    """
    print(help_message)
    
    # Keyboard controls
    while not should_quit:
        # Only update display if needed
        if needs_update:
            display_image = update_display()
            cv2.imshow(window_name, display_image)
            needs_update = False
        
        key = cv2.waitKey(50) & 0xFF  # 50ms timeout for better responsiveness
        
        # Check if window was closed by user
        if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
            break
            
        # Press 'q' to quit
        if key == ord('q'):
            break
            
        # Press '+' or '=' to zoom in
        elif key == ord('+') or key == ord('='):
            zoom *= 1.2
            needs_update = True
            
        # Press '-' to zoom out
        elif key == ord('-'):
            zoom = max(0.1, zoom / 1.2)  # Prevent excessive zooming out
            needs_update = True
            
        # Press 'r' to reset view
        elif key == ord('r'):
            zoom = 1.0
            pan_x = 0
            pan_y = 0
            needs_update = True
            
        # Press 'f' to toggle fullscreen
        elif key == ord('f'):
            is_fullscreen = not is_fullscreen
            if is_fullscreen:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
            else:
                cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, WINDOW_WIDTH, WINDOW_HEIGHT)
            needs_update = True
            
        # Arrow keys for panning
        elif key == 81 or key == 2424832:  # Left arrow
            pan_x += 50
            needs_update = True
        elif key == 82 or key == 2490368:  # Up arrow
            pan_y += 50
            needs_update = True
        elif key == 83 or key == 2555904:  # Right arrow
            pan_x -= 50
            needs_update = True
        elif key == 84 or key == 2621440:  # Down arrow
            pan_y -= 50
            needs_update = True
        elif key == 255:  # No key pressed (timeout)
            # Just continue the loop
            pass
    
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()