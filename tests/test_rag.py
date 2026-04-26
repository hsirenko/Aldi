from __future__ import annotations

from contextlib import contextmanager
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest


class _FakeEmbeddingMatrix:
    def __init__(self, rows: list[list[float]]) -> None:
        self._rows = rows
        self.shape = (len(rows), len(rows[0]) if rows else 0)

    def astype(self, dtype: str) -> "_FakeEmbeddingMatrix":
        _ = dtype
        return self


class _FakeTensor:
    def __init__(self, value: _FakeEmbeddingMatrix) -> None:
        self._value = value

    def mean(self, dim: int) -> "_FakeTensor":
        return self

    def numpy(self) -> _FakeEmbeddingMatrix:
        return self._value


class _FakeModelOutput:
    def __init__(self, embedding: np.ndarray) -> None:
        self.last_hidden_state = _FakeTensor(embedding)


class _FakeModel:
    def __call__(self, **kwargs: object) -> _FakeModelOutput:
        _ = kwargs
        return _FakeModelOutput(_FakeEmbeddingMatrix([[1.0, 2.0, 3.0]]))


class _FakeTokenizer:
    def __call__(self, *args: object, **kwargs: object) -> dict[str, list[int]]:
        _ = (args, kwargs)
        return {"input_ids": [1, 2, 3]}


@contextmanager
def _patched_backends():
    fake_openai_client = MagicMock()
    openai_cls = MagicMock(return_value=fake_openai_client)
    fake_openai_module = SimpleNamespace(OpenAI=openai_cls)

    fake_transformers_module = SimpleNamespace(
        AutoTokenizer=SimpleNamespace(from_pretrained=MagicMock(return_value=_FakeTokenizer())),
        AutoModel=SimpleNamespace(from_pretrained=MagicMock(return_value=_FakeModel())),
    )

    fake_index = MagicMock()
    fake_index.search.return_value = ([[0.1, 0.2]], [[0, 1]])
    fake_faiss_module = SimpleNamespace(IndexFlatL2=MagicMock(return_value=fake_index))

    @contextmanager
    def _no_grad():
        yield

    fake_torch_module = SimpleNamespace(no_grad=_no_grad)

    with patch.dict(
        "sys.modules",
        {
            "openai": fake_openai_module,
            "transformers": fake_transformers_module,
            "faiss": fake_faiss_module,
            "torch": fake_torch_module,
        },
    ):
        yield {
            "openai_cls": openai_cls,
            "openai_client": fake_openai_client,
            "index": fake_index,
        }


def _build_rag():
    from RAG import ProductRAG

    df = pd.DataFrame({"description": ["alpha", "beta", "gamma"]})
    with _patched_backends():
        rag = ProductRAG(df, "test-key", chat_model="test-model")
    return rag


def test_search_raises_if_index_missing() -> None:
    rag = _build_rag()
    rag.index = None
    with pytest.raises(RuntimeError, match="Index not built"):
        rag.search("query", 2)


def test_ask_question_uses_generate_response() -> None:
    rag = _build_rag()
    rag.generate_response = MagicMock(return_value="final answer")
    answer = rag.ask_question("input description", 2, "question?")
    assert answer == "final answer"
    rag.generate_response.assert_called_once()


def test_generate_response_returns_trimmed_content() -> None:
    rag = _build_rag()
    response = SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content="  done  "))]
    )
    rag.client.chat.completions.create.return_value = response

    out = rag.generate_response("What?", "Some context")

    assert out == "done"
    rag.client.chat.completions.create.assert_called_once()


def test_openai_client_accepts_base_url() -> None:
    from RAG import ProductRAG

    df = pd.DataFrame({"description": ["a", "b"]})
    with _patched_backends() as backends, patch.dict(
        "os.environ", {"OPENAI_BASE_URL": "https://api.groq.com/openai/v1"}
    ):
        ProductRAG(df, "groq-key", chat_model="llama-3.1-8b-instant")
    backends["openai_cls"].assert_called_once_with(
        api_key="groq-key",
        base_url="https://api.groq.com/openai/v1",
    )
