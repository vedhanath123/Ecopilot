import cv2
import numpy as np
from PIL import Image
import io

def preprocess_image(image):
    """
    Preprocess the uploaded blueprint image for analysis.
    
    Args:
        image: PIL Image object of the blueprint
    
    Returns:
        Processed image as numpy array
    """
    # Convert PIL Image to numpy array
    img_array = np.array(image)
    
    # Convert to grayscale if it's not already
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply adaptive thresholding to get binary image
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
    )
    
    # Find contours in the binary image
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Draw contours on a blank image
    contour_img = np.zeros_like(thresh)
    cv2.drawContours(contour_img, contours, -1, 255, 1)
    
    # Return the processed image
    return contour_img

def extract_features(processed_image):
    """
    Extract relevant features from the processed blueprint image.
    
    Args:
        processed_image: Numpy array of the processed image
    
    Returns:
        Dictionary containing extracted features
    """
    # Find contours in the processed image
    contours, _ = cv2.findContours(processed_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Get basic shape features
    total_area = processed_image.shape[0] * processed_image.shape[1]
    contour_areas = [cv2.contourArea(cnt) for cnt in contours]
    building_area_ratio = sum(contour_areas) / total_area if total_area > 0 else 0
    
    # Count lines (approximation by detecting straight edges)
    edges = cv2.Canny(processed_image, 50, 150, apertureSize=3)
    lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=50, minLineLength=50, maxLineGap=10)
    
    # Count the number of lines
    num_lines = 0 if lines is None else len(lines)
    
    # Detect rooms (approximation by detecting closed shapes)
    room_contours = []
    for cnt in contours:
        # Get approximate polygon
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        
        # If the shape has 4 or more points and is relatively large, consider it a room
        if len(approx) >= 4 and cv2.contourArea(cnt) > 500:
            room_contours.append(cnt)
    
    num_rooms = len(room_contours)
    
    # Count potential windows and doors (approximation)
    small_rects = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        # Small rectangular shapes might be windows or doors
        if 10 < w < 100 and 10 < h < 100:
            small_rects.append((x, y, w, h))
    
    num_windows_doors = len(small_rects)
    
    # Return extracted features
    return {
        'image_size': processed_image.shape,
        'building_area_ratio': building_area_ratio,
        'num_contours': len(contours),
        'num_lines': num_lines,
        'num_rooms': num_rooms,
        'num_windows_doors': num_windows_doors,
        'contours': contours,
        'room_contours': room_contours,
        'lines': lines,
        'windows_doors': small_rects
    }
