from __future__ import annotations

import re
from dataclasses import dataclass

import pandas as pd

from interfaces import LLMProvider


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


@dataclass
class DeterministicFallbackProvider(LLMProvider):
    """Rule-based offline provider for deterministic local answers."""

    catalog_df: pd.DataFrame

    def ask_question(self, input_description: str, k: int, question: str) -> str:
        corpus = self.catalog_df["description"].astype(str).tolist()
        ranked = self._rank_matches(input_description, corpus, k=max(1, k))
        matched = [corpus[i] for i in ranked]
        competitor = self._extract_field(input_description, "User competitor / retailer focus")
        ocr = self._extract_field(input_description, "OCR from product image")

        lines = [
            "Offline fallback mode is active (deterministic, no external LLM call).",
            f"Question: {question or '(not provided)'}",
        ]
        if competitor:
            lines.append(f"Competitor focus: {competitor}")
        lines.append("Top catalog matches:")
        lines.extend([f"- {item}" for item in matched] or ["- No catalog matches available"])
        if ocr:
            lines.append(f"OCR snippet: {ocr[:220]}")
        lines.append(
            "Note: This response is generated from local rules and catalog similarity only."
        )
        return "\n".join(lines)

    @staticmethod
    def _extract_field(payload: str, key: str) -> str:
        prefix = f"{key}:"
        for line in payload.splitlines():
            if line.startswith(prefix):
                return line.replace(prefix, "", 1).strip()
        return ""

    @staticmethod
    def _rank_matches(query: str, corpus: list[str], k: int) -> list[int]:
        q_tokens = set(_tokenize(query))
        if not corpus:
            return []
        scored: list[tuple[float, int]] = []
        for idx, item in enumerate(corpus):
            item_tokens = set(_tokenize(item))
            overlap = len(q_tokens & item_tokens)
            denom = max(1, len(item_tokens))
            # Higher overlap first; stable tie-breaker on index for determinism.
            score = overlap / denom
            scored.append((score, idx))
        scored.sort(key=lambda x: (-x[0], x[1]))
        return [idx for _, idx in scored[:k]]


@dataclass
class FallbackLLMProvider(LLMProvider):
    """Primary provider with deterministic local fallback on failure."""

    primary: LLMProvider
    fallback: LLMProvider

    def ask_question(self, input_description: str, k: int, question: str) -> str:
        try:
            return self.primary.ask_question(input_description, k=k, question=question)
        except Exception:
            return self.fallback.ask_question(input_description, k=k, question=question)
