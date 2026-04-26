from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram.ext import ConversationHandler

import telegram_bot


def _mk_message(
    *,
    text: str | None = None,
    photo: list[object] | None = None,
    user_id: int = 511505636,
) -> SimpleNamespace:
    return SimpleNamespace(
        text=text,
        photo=photo or [],
        from_user=SimpleNamespace(id=user_id, first_name="Helen"),
        reply_text=AsyncMock(),
    )


@pytest.mark.asyncio
async def test_conversation_integration_with_mocked_provider() -> None:
    """End-to-end conversation state flow with simulated Telegram updates."""
    rag = MagicMock()
    rag.ask_question.return_value = "Mocked comparison result"

    ocr = MagicMock()
    ocr.is_enabled.return_value = True
    ocr.extract_text_from_image.return_value = "Calories 123"
    ocr.clean_extracted_text.return_value = "Calories 123"

    context = SimpleNamespace(
        user_data={},
        bot_data={"product_rag": rag, "ocr": ocr},
    )

    # 1) /start
    start_update = SimpleNamespace(message=_mk_message(text="/start"))
    state = await telegram_bot.start(start_update, context)
    assert state == telegram_bot.ASK_QUESTION

    # 2) user question
    q_update = SimpleNamespace(message=_mk_message(text="Compare this bar"))
    state = await telegram_bot.ask_question(q_update, context)
    assert state == telegram_bot.ENTER_COMPETITOR
    assert context.user_data["question"] == "Compare this bar"

    # 3) competitor
    comp_update = SimpleNamespace(message=_mk_message(text="Lidl"))
    state = await telegram_bot.enter_competitor(comp_update, context)
    assert state == telegram_bot.UPLOAD_IMAGE
    assert context.user_data["competitor"] == "Lidl"

    # 4) photo upload + provider answer
    file_obj = SimpleNamespace(download_to_drive=AsyncMock())
    photo_obj = SimpleNamespace(get_file=AsyncMock(return_value=file_obj))
    photo_update = SimpleNamespace(message=_mk_message(photo=[photo_obj]))

    with patch("telegram_bot._download_dir", return_value=Path("/tmp")):
        state = await telegram_bot.upload_image(photo_update, context)

    assert state == ConversationHandler.END
    rag.ask_question.assert_called_once()
    assert "OCR from product image: Calories 123" in rag.ask_question.call_args.args[0]
    assert rag.ask_question.call_args.kwargs["question"] == "Compare this bar"
    photo_update.message.reply_text.assert_awaited_once_with("Mocked comparison result")
