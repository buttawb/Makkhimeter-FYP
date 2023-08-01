import cv2
import numpy as np
import pandas as pd


def detect_flies(image, lower_color, upper_color, tube_height, pixel_to_mm):
    # Convert the image to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Apply color thresholding
    mask = cv2.inRange(hsv_image, lower_color, upper_color)

    # Apply morphological operations to remove noise
    kernel = np.ones((3, 3), np.uint8)
    opening = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)

    # Find contours of the detected flies
    contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Process each contour
    detected_flies = []
    for contour in contours:
        # Calculate the contour area
        area = cv2.contourArea(contour)

        # Ignore small contours
        if area < 100:
            continue

        # Calculate the bounding circle
        (x, y), radius = cv2.minEnclosingCircle(contour)

        # Calculate the distance from the top and bottom of the tube in millimeters
        distance_from_top = y * pixel_to_mm
        distance_from_bottom = (tube_height - y) * pixel_to_mm

        # Draw a circle around the fly
        cv2.circle(image, (int(x), int(y)), int(radius), (209, 106, 98), 2)

        # Add the coordinates and distances to the list
        detected_flies.append((x, y, radius, distance_from_top, distance_from_bottom))

        # Add label to the circle
        cv2.putText(image, f" {len(detected_flies)}", (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    return image, detected_flies


def ring_assay(img, out_img_path):
    # Load the image
    image = cv2.imread(img)

    # Define the height of the tube (distance from top to bottom) in pixels
    tube_height_pixels = image.shape[0]

    # Define the length of the tube in millimeters
    tube_length_mm = 200

    # Calculate the conversion factor from pixels to millimeters
    pixel_to_mm = tube_length_mm / tube_height_pixels

    # Define the lower and upper color ranges based on trackbar positions
    lower_color = np.array([0, 16, 0])
    upper_color = np.array([255, 255, 255])

    # Detect flies and mark circles
    result_image, detected_flies = detect_flies(image, lower_color, upper_color, tube_height_pixels, pixel_to_mm)

    # Display the result image
    cv2.imwrite(out_img_path, result_image)

    # Create a dataframe of distances
    df = pd.DataFrame(detected_flies, columns=['X', 'Y', 'Radius', 'DT', 'DB'])
    return df
