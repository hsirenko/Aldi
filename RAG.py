from __future__ import annotations

import logging
import os
from typing import List

import pandas as pd

from interfaces import LLMProvider

logger = logging.getLogger(__name__)


class ProductRAG(LLMProvider):
    """Embed product descriptions, retrieve similar rows with FAISS, answer with an LLM."""

    def __init__(
        self,
        df_description: pd.DataFrame,
        openai_api_key: str,
        chat_model: str | None = None,
    ):
        from openai import OpenAI
        from transformers import AutoModel, AutoTokenizer

        self.model_name = "sentence-transformers/all-MiniLM-L12-v2"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.df = df_description.reset_index(drop=True)
        base_url = os.getenv("OPENAI_BASE_URL", "").strip() or None
        self.client = OpenAI(api_key=openai_api_key, base_url=base_url)
        self.chat_model = chat_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.index: object | None = None
        self.build_index()

    def encode_descriptions(self, descriptions: List[str]):
        import torch

        encoded_input = self.tokenizer(
            descriptions,
            padding=True,
            truncation=True,
            return_tensors="pt",
            max_length=128,
        )
        with torch.no_grad():
            model_output = self.model(**encoded_input)
            embeddings = model_output.last_hidden_state.mean(dim=1)
        return embeddings.numpy().astype("float32")

    def build_index(self) -> None:
        import faiss

        descriptions = self.df["description"].tolist()
        embeddings = self.encode_descriptions(descriptions)
        self.index = faiss.IndexFlatL2(embeddings.shape[1])
        self.index.add(embeddings)

    def search(self, p_desc: str, k: int) -> pd.DataFrame:
        if self.index is None:
            raise RuntimeError("Index not built")
        query_embedding = self.encode_descriptions([p_desc])
        _distances, indices = self.index.search(query_embedding, k)
        idx = indices[0]
        return self.df.iloc[idx].copy()

    def ask_question(self, input_description: str, k: int, question: str) -> str:
        similar_products = self.search(input_description, k)
        descriptions: List[str] = similar_products["description"].tolist()
        context = (
            f"Input product (from user, may include OCR text): {input_description}. "
            f"Similar catalog products: " + "; ".join(descriptions)
        )
        logger.debug("RAG context length=%s", len(context))
        return self.generate_response(question, context)

    def generate_response(self, question: str, context: str) -> str:
        prompt = f"Question: {question}\nContext: {context}\nAnswer concisely. If context lacks facts, say so."
        response = self.client.chat.completions.create(
            model=self.chat_model,
            temperature=0,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a procurement assistant comparing grocery products. "
                        "Use only the context when stating specific product facts."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )
        choice = response.choices[0].message
        return (choice.content or "").strip()


def _demo() -> None:
    logging.basicConfig(level=logging.INFO)
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        print("Set OPENAI_API_KEY to run the demo.")
        return
    df_description = pd.DataFrame(
        {
            "description": [
                "Lidl Belgian waffles 500g",
                "Netto maple syrup waffles 450g",
                "Lidl chocolate waffles 300g",
                "Netto classic waffles 500g",
                "Aldi blueberry waffles 400g",
            ]
        }
    )
    product_rag = ProductRAG(df_description, key)
    answer = product_rag.ask_question(
        "Aldi's vanilla waffles 500g",
        3,
        "Which option is likely lower in sugar based on descriptions only?",
    )
    print(answer)


if __name__ == "__main__":
    _demo()
