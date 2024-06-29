# from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, Bot
# from telegram.ext import Updater, CommandHandler, MessageHandler, filters, ConversationHandler, CallbackContext
# import threading
# import openai
# import streamlit as st

# # Initialize OpenAI API
# OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
# openai.api_key = OPENAI_API_KEY

# # Initialize the Telegram bot
# TELEGRAM_TOKEN = '7389289933:AAGiJFsmA6RZlXqGiPU8KcPHs1Troq7K-WY'

# bot = Bot(token=TELEGRAM_TOKEN)

# # Define conversation states
# ASK_QUESTION, ENTER_COMPETITOR, UPLOAD_IMAGE = range(3)

# # Function to process messages with GPT
# def process_message_with_gpt(message_text):
#     return ("Helen")

# # Start command handler
# def start(update: Update, context: CallbackContext) -> int:
#     update.message.reply_text(
#         "Hi! I'm your product comparison bot. Ask a question about your product:",
#         reply_markup=ReplyKeyboardRemove(),
#     )
#     return ASK_QUESTION

# # Ask question handler
# def ask_question(update: Update, context: CallbackContext) -> int:
#     user = update.message.from_user
#     context.user_data['question'] = update.message.text
#     update.message.reply_text(
#         "Got it. Now, enter the competitor name:",
#     )
#     return ENTER_COMPETITOR

# # Enter competitor handler
# def enter_competitor(update: Update, context: CallbackContext) -> int:
#     user = update.message.from_user
#     context.user_data['competitor'] = update.message.text
#     update.message.reply_text(
#         "Great! Now, please upload an image of the product:",
#     )
#     return UPLOAD_IMAGE

# # Upload image handler
# def upload_image(update: Update, context: CallbackContext) -> int:
#     user = update.message.from_user
#     photo_file = update.message.photo[-1].get_file()
#     photo_file.download('product_image.jpg')  # Save the image

#     # Process the user's question with GPT
#     question = context.user_data['question']
#     competitor = context.user_data['competitor']
#     gpt_response = process_message_with_gpt(question)

#     update.message.reply_text(
#         f"Question: {question}\nCompetitor: {competitor}\nGPT Response: {gpt_response}\nImage received and saved.",
#         reply_markup=ReplyKeyboardRemove(),
#     )
#     return ConversationHandler.END

# # Cancel command handler
# def cancel(update: Update, context: CallbackContext) -> int:
#     update.message.reply_text(
#         'Conversation canceled.',
#         reply_markup=ReplyKeyboardRemove()
#     )
#     return ConversationHandler.END

# # Start the bot
# def start_bot():
#     try:
#         update_queue = None  # Create an instance of UpdateQueue
#         updater = Updater(bot=bot, update_queue=update_queue)
        
#         dispatcher = updater.dispatcher

#         # Command handler for /start
#         dispatcher.add_handler(CommandHandler('start', start))

#         conv_handler = ConversationHandler(
#             entry_points=[CommandHandler('start', start)],
#             states={
#                 ASK_QUESTION: [MessageHandler(Filters.text & ~Filters.command, ask_question)],
#                 ENTER_COMPETITOR: [MessageHandler(Filters.text & ~Filters.command, enter_competitor)],
#                 UPLOAD_IMAGE: [MessageHandler(Filters.photo, upload_image)],
#             },
#             fallbacks=[CommandHandler('cancel', cancel)],
#         )

#         # dp.add_handler(conv_handler)
#         updater.start_polling()
#         updater.idle()
#     except Exception as e:
#         print(f"Error in bot thread: {e}")

# # Run the bot in a separate thread
# bot_thread = threading.Thread(target=start_bot)
# bot_thread.start()

# # Streamlit interface
# st.title("Telegram GPT-3 Bot")
# st.write("The Telegram bot is running. You can interact with it by sending messages to it on Telegram.")

# # Display bot status
# if bot_thread.is_alive():
#     st.success("The bot is running.")
# else:
#     st.error("The bot has stopped.")

#### ATQA's version  ########

# import streamlit as st

# # Initialize session state to store conversation history
# if 'conversation_history' not in st.session_state:
#     st.session_state.conversation_history = []

# # Function to generate bot responses
# def get_bot_response(user_input):
#     # Replace with your chatbot logic or API call
#     return "Hello! You said: " + user_input

# # Streamlit app layout
# def main():
#     st.title("Chat Browser")
#     st.markdown("---")

#     # User input text box
#     user_input = st.text_input("Enter your message here:")

#     # Check if user has submitted a message
#     if user_input:
#         # Add user message to conversation history
#         st.session_state.conversation_history.append(f"You: {user_input}")

#         # Display user message
#         st.text_area("You:", value=user_input, height=100, max_chars=None, key=None)

#         # Get and display bot response
#         bot_response = get_bot_response(user_input)
#         st.session_state.conversation_history.append(f"Bot: {bot_response}")
#         st.text_area("Bot:", value=bot_response, height=100, max_chars=None, key=None)

#     # Display conversation history
#     st.markdown("---")
#     st.markdown("**Conversation History**")
#     for message in st.session_state.conversation_history:
#         st.write(message)

# # Run the app
# if __name__ == "__main__":
#     main()


##### CHATBOT TUTORIAL #####

# import logging

# from telegram import Update, ForceReply, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
# from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

# logger = logging.getLogger(__name__)

# # Store bot screaming status
# screaming = False

# # Pre-assign menu text
# FIRST_MENU = "<b>Menu 1</b>\n\nA beautiful menu with a shiny inline button."
# SECOND_MENU = "<b>Menu 2</b>\n\nA better menu with even more shiny inline buttons."

# # Pre-assign button text
# NEXT_BUTTON = "Next"
# BACK_BUTTON = "Back"
# TUTORIAL_BUTTON = "Tutorial"

# # Build keyboards
# FIRST_MENU_MARKUP = InlineKeyboardMarkup([[
#     InlineKeyboardButton(NEXT_BUTTON, callback_data=NEXT_BUTTON)
# ]])
# SECOND_MENU_MARKUP = InlineKeyboardMarkup([
#     [InlineKeyboardButton(BACK_BUTTON, callback_data=BACK_BUTTON)],
#     [InlineKeyboardButton(TUTORIAL_BUTTON, url="https://core.telegram.org/bots/api")]
# ])


# def echo(update: Update, context: CallbackContext) -> None:
#     """
#     This function would be added to the dispatcher as a handler for messages coming from the Bot API
#     """

#     # Print to console
#     print(f'{update.message.from_user.first_name} wrote {update.message.text}')

#     if screaming and update.message.text:
#         context.bot.send_message(
#             update.message.chat_id,
#             update.message.text.upper(),
#             # To preserve the markdown, we attach entities (bold, italic...)
#             entities=update.message.entities
#         )
#     else:
#         # This is equivalent to forwarding, without the sender's name
#         update.message.copy(update.message.chat_id)


# def scream(update: Update, context: CallbackContext) -> None:
#     """
#     This function handles the /scream command
#     """

#     global screaming
#     screaming = True


# def whisper(update: Update, context: CallbackContext) -> None:
#     """
#     This function handles /whisper command
#     """

#     global screaming
#     screaming = False


# def menu(update: Update, context: CallbackContext) -> None:
#     """
#     This handler sends a menu with the inline buttons we pre-assigned above
#     """

#     context.bot.send_message(
#         update.message.from_user.id,
#         FIRST_MENU,
#         parse_mode=ParseMode.HTML,
#         reply_markup=FIRST_MENU_MARKUP
#     )


# def button_tap(update: Update, context: CallbackContext) -> None:
#     """
#     This handler processes the inline buttons on the menu
#     """

#     data = update.callback_query.data
#     text = ''
#     markup = None

#     if data == NEXT_BUTTON:
#         text = SECOND_MENU
#         markup = SECOND_MENU_MARKUP
#     elif data == BACK_BUTTON:
#         text = FIRST_MENU
#         markup = FIRST_MENU_MARKUP

#     # Close the query to end the client-side loading animation
#     update.callback_query.answer()

#     # Update message content with corresponding menu section
#     update.callback_query.message.edit_text(
#         text,
#         ParseMode.HTML,
#         reply_markup=markup
#     )


# def main() -> None:
#     updater = Updater("<YOUR_BOT_TOKEN_HERE>")

#     # Get the dispatcher to register handlers
#     # Then, we register each handler and the conditions the update must meet to trigger it
#     dispatcher = updater.dispatcher

#     # Register commands
#     dispatcher.add_handler(CommandHandler("scream", scream))
#     dispatcher.add_handler(CommandHandler("whisper", whisper))
#     dispatcher.add_handler(CommandHandler("menu", menu))

#     # Register handler for inline buttons
#     dispatcher.add_handler(CallbackQueryHandler(button_tap))

#     # Echo any message that is not a command
#     dispatcher.add_handler(MessageHandler(~Filters.command, echo))

#     # Start the Bot
#     updater.start_polling()

#     # Run the bot until you press Ctrl-C
#     updater.idle()


# if __name__ == '__main__':
#     main()

##### EXAMPLE CHATBOT #####

#!/usr/bin/env python
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

GENDER, PHOTO, LOCATION, BIO = range(4)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user about their gender."""
    reply_keyboard = [["Boy", "Girl", "Other"]]

    await update.message.reply_text(
        "Hi! I'm your product comparison bot. Ask a question about your product:"
        "Send /cancel to stop talking to me.\n\n"
        "Are you a boy or a girl?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Boy or Girl?"
        ),
    )

    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the selected gender and asks for a photo."""
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "I see! Please send me a photo of yourself, "
        "so I know what you look like, or send /skip if you don't want to.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the photo and asks for a location."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("user_photo.jpg")
    logger.info("Photo of %s: %s", user.first_name, "user_photo.jpg")
    await update.message.reply_text(
        "Gorgeous! Let me give you all the information you need: "
    )

    return LOCATION


# async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Skips the photo and asks for a location."""
#     user = update.message.from_user
#     logger.info("User %s did not send a photo.", user.first_name)
#     await update.message.reply_text(
#         "I bet you look great! Now, send me your location please, or send /skip."
#     )

#     return LOCATION


# async def location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the location and asks for some info about the user."""
#     user = update.message.from_user
#     user_location = update.message.location
#     logger.info(
#         "Location of %s: %f / %f", user.first_name, user_location.latitude, user_location.longitude
#     )
#     await update.message.reply_text(
#         "Maybe I can visit you sometime! At last, tell me something about yourself."
#     )

#     return BIO


# async def skip_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Skips the location and asks for info about the user."""
#     user = update.message.from_user
#     logger.info("User %s did not send a location.", user.first_name)
#     await update.message.reply_text(
#         "You seem a bit paranoid! At last, tell me something about yourself."
#     )

#     return BIO


# async def bio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
#     """Stores the info about the user and ends the conversation."""
#     user = update.message.from_user
#     logger.info("Bio of %s: %s", user.first_name, update.message.text)
#     await update.message.reply_text("Thank you! I hope we can talk again some day.")

#     return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )

    return ConversationHandler.END


def main() -> None:
    """Run the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7389289933:AAGiJFsmA6RZlXqGiPU8KcPHs1Troq7K-WY").build()

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER: [MessageHandler(filters.Regex("^(Boy|Girl|Other)$"), gender)],
            PHOTO: [MessageHandler(filters.PHOTO, photo), CommandHandler("skip", skip_photo)],
            LOCATION: [
                MessageHandler(filters.LOCATION, location),
                CommandHandler("skip", skip_location),
            ],
            BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, bio)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()



