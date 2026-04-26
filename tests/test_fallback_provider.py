from __future__ import annotations

import pandas as pd

from fallback_provider import DeterministicFallbackProvider, FallbackLLMProvider


def test_deterministic_fallback_includes_matches_and_note() -> None:
    df = pd.DataFrame(
        {
            "description": [
                "Lidl chocolate bar 100g",
                "Aldi peanut chocolate bar",
                "Netto crackers",
            ]
        }
    )
    provider = DeterministicFallbackProvider(df)
    payload = (
        "OCR from product image: chocolate peanuts 100g\n"
        "User competitor / retailer focus: Lidl\n"
        "User question: compare options"
    )
    answer = provider.ask_question(payload, k=2, question="Which is closer?")

    assert "Offline fallback mode is active" in answer
    assert "Top catalog matches:" in answer
    assert "- Lidl chocolate bar 100g" in answer
    assert "Note: This response is generated from local rules" in answer


def test_fallback_wrapper_uses_secondary_on_primary_failure() -> None:
    class _Broken:
        def ask_question(self, input_description: str, k: int, question: str) -> str:
            raise RuntimeError("upstream failed")

    class _Local:
        def ask_question(self, input_description: str, k: int, question: str) -> str:
            _ = (input_description, k, question)
            return "local"

    provider = FallbackLLMProvider(primary=_Broken(), fallback=_Local())
    out = provider.ask_question("x", 3, "q")
    assert out == "local"
