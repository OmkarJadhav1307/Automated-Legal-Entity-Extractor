import os
import pytesseract
from pdf2image import convert_from_path
import numpy as np
from PIL import Image
from typing import List, Union

from src.utils.logger import get_logger
from src.ocr.preprocess import preprocess_image
from src.ocr.cleaner import clean_ocr_text

from dotenv import load_dotenv
load_dotenv()

logger = get_logger(__name__)

# Configure Tesseract path if provided in environment
tesseract_cmd = os.getenv("TESSERACT_CMD_PATH")
if tesseract_cmd and os.path.exists(tesseract_cmd):
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Configure Poppler path for pdf2image if provided
poppler_path = os.getenv("POPPLER_PATH")

class OCREngine:
    """
    The main OCR Engine handling extraction from PDFs and Images.
    """
    
    def __init__(self, lang: str = "eng"):
        self.lang = lang
        logger.info(f"Initialized OCREngine with language: {self.lang}")

    def process_pdf(self, pdf_path: str) -> str:
        """
        Extracts text from a PDF file using OCR.
        """
        logger.info(f"Processing PDF parsing: {pdf_path}")
        
        try:
            if poppler_path and os.path.exists(poppler_path):
                images = convert_from_path(pdf_path, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path)
            logger.info(f"Successfully converted PDF to {len(images)} images")
        except Exception as e:
            logger.error(f"Failed to convert PDF. Ensure Poppler is installed. Error: {str(e)}")
            raise e

        extracted_text = []
        for i, img in enumerate(images):
            text = self.process_image(img)
            extracted_text.append(text)
            logger.debug(f"Successfully processed page {i + 1}")

        full_text = "\n\n".join(extracted_text)
        return clean_ocr_text(full_text)

    def process_image(self, image: Union[Image.Image, np.ndarray, str]) -> str:
        """
        Extracts text from a single image using OCR along with prepocessing.
        """
        if isinstance(image, str):
            try:
                img_pil = Image.open(image)
            except Exception as e:
                logger.error(f"Failed to open image file {image}: {str(e)}")
                raise e
            img_np = np.array(img_pil)
        elif isinstance(image, Image.Image):
            img_np = np.array(image)
        elif isinstance(image, np.ndarray):
            img_np = image
        else:
            raise ValueError("Unsupported image format")

        try:
            # Apply filtering
            processed_img_np = preprocess_image(img_np)
            
            # oem 3 (Default), psm 3 (Fully automatic page segmentation)
            custom_config = r'--oem 3 --psm 3'
            text = pytesseract.image_to_string(
                processed_img_np, 
                lang=self.lang, 
                config=custom_config
            )
            return text
        except Exception as e:
            logger.error(f"Failed to process image during OCR: {str(e)}")
            raise e
