from __future__ import annotations

from typing import Protocol


class LLMProvider(Protocol):
    """Abstract interface for question-answering over product context."""

    def ask_question(self, input_description: str, k: int, question: str) -> str:
        ...


class OCRBackend(Protocol):
    """Abstract OCR interface used by the Telegram workflow."""

    def is_enabled(self) -> bool:
        ...

    def extract_text_from_image(self, image_path: str, lang: str = "deu+eng") -> str:
        ...

    def clean_extracted_text(self, text: str) -> str:
        ...
