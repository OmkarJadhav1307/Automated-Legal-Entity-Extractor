import cv2
import numpy as np

def preprocess_image(image_np: np.ndarray) -> np.ndarray:
    """
    Applies preprocessing steps to an image array to improve OCR accuracy.
    Includes grayscaling, thresholding, and noise removal.
    """
    # Convert to grayscale if not already
    if len(image_np.shape) == 3 and image_np.shape[2] == 3:
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    else:
        gray = image_np

    # Apply adaptive thresholding to handle varying lighting/contrast
    # Block size of 15, constant C of 9 (these are tunable parameters)
    thresh = cv2.adaptiveThreshold(
        gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 9
    )

    # Optional: Noise removal using median blur
    # Can be adjusted based on the quality of scanned documents
    denoised = cv2.medianBlur(thresh, 3)

    return denoised
