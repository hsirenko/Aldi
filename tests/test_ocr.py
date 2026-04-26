from __future__ import annotations

from unittest.mock import patch

from ocr import OCRProcessor


def test_init_disables_ocr_when_tesseract_missing() -> None:
    with patch("ocr.shutil.which", return_value=None):
        processor = OCRProcessor()
    assert processor.is_enabled() is False


def test_extract_returns_empty_when_disabled() -> None:
    processor = OCRProcessor(tesseract_cmd=None)
    processor._enabled = False
    assert processor.extract_text_from_image("anything.png") == ""


def test_clean_extracted_text_collapses_lines() -> None:
    raw = "Line one\nLine two\n\nLine three"
    assert OCRProcessor.clean_extracted_text(raw) == "Line one Line two  Line three"
