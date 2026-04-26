from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import cast

import pandas as pd
from dotenv import load_dotenv
from telegram import ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from fallback_provider import DeterministicFallbackProvider, FallbackLLMProvider
from interfaces import LLMProvider, OCRBackend
from ocr import OCRProcessor
from RAG import ProductRAG

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ASK_QUESTION, ENTER_COMPETITOR, UPLOAD_IMAGE = range(3)
TELEGRAM_MAX_MESSAGE = 4096


def _download_dir() -> Path:
    base = Path(__file__).resolve().parent / "data" / "downloads"
    base.mkdir(parents=True, exist_ok=True)
    return base


def _offline_mode() -> str:
    mode = os.getenv("OFFLINE_FALLBACK_MODE", "off").strip().lower()
    if mode in {"on", "auto", "off"}:
        return mode
    return "off"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start conversation: ask for the user's product question."""
    await update.message.reply_text(
        "Hi! I'm your product comparison bot. Ask a question about your product "
        "(e.g. allergens, calories, how it compares to alternatives).",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_QUESTION


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store the question and ask for competitor name."""
    user = update.message.from_user
    context.user_data["question"] = update.message.text
    logger.info("Question from %s: %s", user.first_name, update.message.text)
    await update.message.reply_text("Got it. Now enter the competitor or retailer name:")
    return ENTER_COMPETITOR


async def enter_competitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Store competitor and ask for a product photo."""
    user = update.message.from_user
    context.user_data["competitor"] = update.message.text
    logger.info("Competitor from %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Great! Please upload a clear photo of the product label or packaging."
    )
    return UPLOAD_IMAGE


async def upload_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Run OCR on the image, retrieve similar products, answer with RAG."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    path = _download_dir() / f"{user.id}_product.jpg"
    await photo_file.download_to_drive(str(path))
    logger.info("Photo from %s saved to %s", user.first_name, path)

    product_rag = cast(LLMProvider, context.bot_data["product_rag"])
    ocr = cast(OCRBackend | None, context.bot_data.get("ocr"))

    question = context.user_data.get("question", "")
    competitor = context.user_data.get("competitor", "")

    ocr_text = ""
    if ocr is not None and ocr.is_enabled():
        try:
            raw = ocr.extract_text_from_image(str(path), lang="deu+eng")
            ocr_text = ocr.clean_extracted_text(raw)
        except Exception as exc:  # noqa: BLE001
            logger.warning("OCR failed: %s", exc)

    if not ocr_text.strip():
        ocr_text = (
            "(No label text extracted from image. Answer using competitor context and "
            "catalog matches where possible.)"
        )

    input_description = (
        f"OCR from product image: {ocr_text[:1200]}\n"
        f"User competitor / retailer focus: {competitor}\n"
        f"User question: {question}"
    )

    try:
        answer = product_rag.ask_question(input_description, k=3, question=question)
    except Exception as exc:  # noqa: BLE001
        logger.exception("RAG failed")
        err = str(exc).lower()
        if "invalid_api_key" in err or "incorrect api key" in err or "401" in err:
            await update.message.reply_text(
                "OpenAI API key is invalid or missing. Please update OPENAI_API_KEY in .env and restart the bot."
            )
        elif "insufficient_quota" in err or "rate limit" in err or "429" in err:
            await update.message.reply_text(
                "OpenAI quota/rate limit reached (429). Please check billing/quota on your OpenAI account, then try again."
            )
        else:
            await update.message.reply_text(
                "Sorry, something went wrong while generating an answer. Please try again."
            )
        return ConversationHandler.END

    if len(answer) > TELEGRAM_MAX_MESSAGE:
        answer = answer[: TELEGRAM_MAX_MESSAGE - 40] + "\n\n[Answer truncated for Telegram]"

    await update.message.reply_text(answer)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel conversation."""
    user = update.message.from_user
    logger.info("User %s canceled.", user.first_name)
    await update.message.reply_text(
        "Bye! Send /start when you want to compare again.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


def main() -> None:
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    api_key = os.getenv("OPENAI_API_KEY")
    mode = _offline_mode()
    if not token:
        raise SystemExit(
            "Missing TELEGRAM_BOT_TOKEN. Copy .env.example to .env and fill values."
        )
    if mode == "off" and not api_key:
        raise SystemExit(
            "Missing OPENAI_API_KEY. Set OFFLINE_FALLBACK_MODE=on for local deterministic mode."
        )

    chat_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

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
    fallback = DeterministicFallbackProvider(df_description)
    if mode == "on":
        product_rag: LLMProvider = fallback
    elif mode == "auto":
        if not api_key:
            product_rag = fallback
        else:
            online = ProductRAG(df_description, api_key, chat_model=chat_model)
            product_rag = FallbackLLMProvider(primary=online, fallback=fallback)
    else:
        product_rag = ProductRAG(df_description, api_key or "", chat_model=chat_model)

    tesseract = os.getenv("TESSERACT_CMD")
    ocr = OCRProcessor(tesseract_cmd=tesseract or None)

    application = Application.builder().token(token).build()
    application.bot_data["product_rag"] = product_rag
    application.bot_data["ocr"] = ocr

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)],
            ENTER_COMPETITOR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, enter_competitor)
            ],
            UPLOAD_IMAGE: [MessageHandler(filters.PHOTO, upload_image)],
        },
        fallbacks=[CommandHandler("cancel", cancel), CommandHandler("start", start)],
        allow_reentry=True,
    )
    application.add_handler(conv_handler)

    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as exc:  # noqa: BLE001
        logger.error("Bot stopped: %s", exc)


if __name__ == "__main__":
    main()
