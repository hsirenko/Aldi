# -*- coding: utf-8 -*-
"""OCR helpers for product label images (German/English)."""

from __future__ import annotations

import logging
import shutil
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter

from interfaces import OCRBackend

logger = logging.getLogger(__name__)


class OCRProcessor(OCRBackend):
    def __init__(self, tesseract_cmd: Optional[str] = None) -> None:
        self._pytesseract = None
        cmd = tesseract_cmd or shutil.which("tesseract")
        self._enabled = bool(cmd)
        if self._enabled and cmd:
            import pytesseract

            self._pytesseract = pytesseract
            self._pytesseract.pytesseract.tesseract_cmd = cmd
            logger.info("Tesseract enabled at %s", cmd)
        else:
            logger.warning(
                "Tesseract not found. Set TESSERACT_CMD or install Tesseract and ensure "
                "it is on PATH. OCR will return empty text."
            )

    def is_enabled(self) -> bool:
        return self._enabled

    def preprocess_image(self, image_path: str) -> str:
        import cv2
        import numpy as np

        image = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if image is None:
            raise FileNotFoundError(f"Could not read image: {image_path}")

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, binary_image = cv2.threshold(
            gray, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        denoised_image = cv2.medianBlur(binary_image, 3)
        kernel = np.ones((1, 1), np.uint8)
        processed_image = cv2.dilate(denoised_image, kernel, iterations=1)
        processed_image = cv2.erode(processed_image, kernel, iterations=1)

        temp_filename = "temp_preprocessed_image.png"
        cv2.imwrite(temp_filename, processed_image)
        return temp_filename

    def extract_text_from_image(self, image_path: str, lang: str = "deu+eng") -> str:
        if not self._enabled:
            return ""
        if self._pytesseract is None:
            import pytesseract

            self._pytesseract = pytesseract
        preprocessed_image_path = self.preprocess_image(image_path)
        image = Image.open(preprocessed_image_path)
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(2)
        image = image.filter(ImageFilter.SHARPEN)
        return self._pytesseract.image_to_string(image, lang=lang)

    @staticmethod
    def clean_extracted_text(text: str) -> str:
        return " ".join(text.splitlines())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    cmd = shutil.which("tesseract")
    ocr_processor = OCRProcessor(tesseract_cmd=cmd)
    image_path = "chocolate.jpg"
    try:
        extracted = ocr_processor.extract_text_from_image(image_path, lang="deu+eng")
        print(ocr_processor.clean_extracted_text(extracted))
    except FileNotFoundError as e:
        print(e)
