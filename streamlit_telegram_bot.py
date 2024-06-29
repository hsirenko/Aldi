from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
import openai
import threading
import streamlit as st

# Initialize OpenAI API
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
openai.api_key = OPENAI_API_KEY

# Initialize the Telegram bot
TELEGRAM_TOKEN = '7389289933:AAGiJFsmA6RZlXqGiPU8KcPHs1Troq7K-WY'
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Define conversation states
ASK_QUESTION, ENTER_COMPETITOR, UPLOAD_IMAGE = range(3)

# Function to process messages with GPT
def process_message_with_gpt(message_text):
    return ("Helen")

# Start command handler
def start(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        "Hi! I'm your product comparison bot. Ask a question about your product:",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_QUESTION

# Ask question handler
def ask_question(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    update.message.reply_text(
        "Got it. Now, enter the competitor name:",
    )
    return ENTER_COMPETITOR

# Enter competitor handler
def enter_competitor(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    context.user_data['competitor'] = update.message.text
    update.message.reply_text(
        "Great! Now, please upload an image of the product:",
    )
    return UPLOAD_IMAGE

# Upload image handler
def upload_image(update: Update, context: CallbackContext) -> int:
    user = update.message.from_user
    photo_file = update.message.photo[-1].get_file()
    photo_file.download('product_image.jpg')  # Save the image

    # Process the user's question with GPT
    question = context.user_data['question']
    competitor = context.user_data['competitor']
    gpt_response = process_message_with_gpt(question)

    update.message.reply_text(
        f"Question: {question}\nCompetitor: {competitor}\nGPT Response: {gpt_response}\nImage received and saved.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

# Cancel command handler
def cancel(update: Update, context: CallbackContext) -> int:
    update.message.reply_text(
        'Conversation canceled.',
        reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END

# Start the bot
def start_bot():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            ASK_QUESTION: [MessageHandler(Filters.text & ~Filters.command, ask_question)],
            ENTER_COMPETITOR: [MessageHandler(Filters.text & ~Filters.command, enter_competitor)],
            UPLOAD_IMAGE: [MessageHandler(Filters.photo, upload_image)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dp.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()

# Run the bot in a separate thread
bot_thread = threading.Thread(target=start_bot)
bot_thread.start()

# Streamlit interface
st.title("Telegram GPT-3 Bot")
st.write("The Telegram bot is running. You can interact with it by sending messages to it on Telegram.")

# Display bot status
if bot_thread.is_alive():
    st.success("The bot is running.")
else:
    st.error("The bot has stopped.")