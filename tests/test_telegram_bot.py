from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from telegram.ext import ConversationHandler

import telegram_bot


@pytest.mark.asyncio
async def test_start_prompts_for_question() -> None:
    message = SimpleNamespace(reply_text=AsyncMock())
    update = SimpleNamespace(message=message)
    context = SimpleNamespace()

    state = await telegram_bot.start(update, context)

    assert state == telegram_bot.ASK_QUESTION
    message.reply_text.assert_awaited_once()


@pytest.mark.asyncio
async def test_ask_question_stores_value_and_moves_next_state() -> None:
    message = SimpleNamespace(
        text="Compare this product",
        from_user=SimpleNamespace(first_name="Helen"),
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(message=message)
    context = SimpleNamespace(user_data={})

    state = await telegram_bot.ask_question(update, context)

    assert state == telegram_bot.ENTER_COMPETITOR
    assert context.user_data["question"] == "Compare this product"


@pytest.mark.asyncio
async def test_enter_competitor_stores_value_and_requests_photo() -> None:
    message = SimpleNamespace(
        text="Lidl",
        from_user=SimpleNamespace(first_name="Helen"),
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(message=message)
    context = SimpleNamespace(user_data={})

    state = await telegram_bot.enter_competitor(update, context)

    assert state == telegram_bot.UPLOAD_IMAGE
    assert context.user_data["competitor"] == "Lidl"
    message.reply_text.assert_awaited_once()


def _build_upload_context(answer: str | Exception) -> tuple[SimpleNamespace, SimpleNamespace]:
    photo = SimpleNamespace(get_file=AsyncMock())
    file_obj = SimpleNamespace(download_to_drive=AsyncMock())
    photo.get_file.return_value = file_obj
    message = SimpleNamespace(
        from_user=SimpleNamespace(id=123, first_name="Helen"),
        photo=[photo],
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(message=message)
    rag = MagicMock()
    if isinstance(answer, Exception):
        rag.ask_question.side_effect = answer
    else:
        rag.ask_question.return_value = answer
    ocr = MagicMock()
    ocr.is_enabled.return_value = False
    context = SimpleNamespace(
        user_data={"question": "Q?", "competitor": "Lidl"},
        bot_data={"product_rag": rag, "ocr": ocr},
    )
    return update, context


@pytest.mark.asyncio
async def test_upload_image_success_sends_answer() -> None:
    update, context = _build_upload_context("Result answer")

    with patch("telegram_bot._download_dir", return_value=Path("/tmp")):
        state = await telegram_bot.upload_image(update, context)

    assert state == ConversationHandler.END
    update.message.reply_text.assert_awaited_once_with("Result answer")


@pytest.mark.asyncio
async def test_upload_image_truncates_long_answer() -> None:
    long_answer = "x" * (telegram_bot.TELEGRAM_MAX_MESSAGE + 100)
    update, context = _build_upload_context(long_answer)

    with patch("telegram_bot._download_dir", return_value=Path("/tmp")):
        await telegram_bot.upload_image(update, context)

    sent = update.message.reply_text.await_args.args[0]
    assert len(sent) <= telegram_bot.TELEGRAM_MAX_MESSAGE
    assert "[Answer truncated for Telegram]" in sent


@pytest.mark.asyncio
async def test_upload_image_invalid_key_message() -> None:
    update, context = _build_upload_context(Exception("401 invalid_api_key"))

    with patch("telegram_bot._download_dir", return_value=Path("/tmp")):
        await telegram_bot.upload_image(update, context)

    sent = update.message.reply_text.await_args.args[0]
    assert "invalid or missing" in sent.lower()


@pytest.mark.asyncio
async def test_upload_image_quota_message() -> None:
    update, context = _build_upload_context(Exception("429 insufficient_quota"))

    with patch("telegram_bot._download_dir", return_value=Path("/tmp")):
        await telegram_bot.upload_image(update, context)

    sent = update.message.reply_text.await_args.args[0]
    assert "quota/rate limit" in sent.lower()


@pytest.mark.asyncio
async def test_cancel_ends_conversation() -> None:
    message = SimpleNamespace(
        from_user=SimpleNamespace(first_name="Helen"),
        reply_text=AsyncMock(),
    )
    update = SimpleNamespace(message=message)
    context = SimpleNamespace()

    state = await telegram_bot.cancel(update, context)

    assert state == ConversationHandler.END
    message.reply_text.assert_awaited_once()


def test_main_fails_when_env_missing() -> None:
    with patch.dict("os.environ", {}, clear=True), patch("telegram_bot.load_dotenv"):
        with pytest.raises(SystemExit, match="Missing TELEGRAM_BOT_TOKEN"):
            telegram_bot.main()
