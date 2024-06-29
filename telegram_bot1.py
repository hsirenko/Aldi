import logging
from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
import pandas as pd

import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import faiss
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModel
import openai

# class ProductRAG:
#     def __init__(self, df_description, openai_api_key):
#         self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
#         self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
#         self.model = AutoModel.from_pretrained(self.model_name)
#         self.df = df_description
#         self.index = None
#         self.openai_api_key = openai_api_key
#         self.build_index()

#     def encode_descriptions(self, descriptions):
#         encoded_input = self.tokenizer(descriptions, padding=True, truncation=True, return_tensors="pt", max_length=128)
#         with torch.no_grad():
#             model_output = self.model(**encoded_input)
#             embeddings = model_output.last_hidden_state.mean(dim=1)
#         return embeddings.numpy()

#     def build_index(self):
#         descriptions = self.df['description'].tolist()
#         embeddings = self.encode_descriptions(descriptions)
#         self.index = faiss.IndexFlatL2(embeddings.shape[1])
#         self.index.add(embeddings)

#     def search(self, p_desc, k):
#         query_embedding = self.encode_descriptions([p_desc])
#         distances, indices = self.index.search(query_embedding, k)
#         return self.df.iloc[indices[0]]

#     def ask_question(self, input_description, k, question):
#         similar_products = self.search(input_description, k)
#         descriptions = similar_products['description'].tolist()

#         context = f"Input product: {input_description}. Products for comparison with input product: " + ", ".join(descriptions)
#         return self.generate_response(question, context)

#     def generate_response(self, question, context):
#         openai.api_key = self.openai_api_key
#         prompt = f"Question: {question}\nContext: {context}\nAnswer:"
#         response = openai.ChatCompletion.create(
#             model='gpt-4-0613',
#             temperature=0,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0,
#             messages=[{"role": "system", "content": "You are a helpful assistant."},
#                       {"role": "user", "content": prompt}]
#         )
#         return response['choices'][0]['message']['content'].strip()

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

ASK_IMAGE, ASK_COMPANY, ASK_QUESTION = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user to upload an image of their product."""
    await update.message.reply_text(
        "Hi! I'm your product comparison bot. Please upload an image of your product.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ASK_IMAGE

async def ask_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the product image and asks for the company name."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("product_image.jpg")
    context.user_data['product_image'] = "product_image.jpg"
    logger.info("Photo of %s: %s", user.first_name, "product_image.jpg")

    await update.message.reply_text(
        "Please tell me the name of the company this product is from.",
    )
    return ASK_COMPANY

async def ask_company(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the company name and asks for the user's question."""
    user = update.message.from_user
    context.user_data['company'] = update.message.text
    logger.info("Company name from %s: %s", user.first_name, update.message.text)

    prompts = [
        "📊 Compare calorie amount of [input] and [similar products].",
        "💲 Compare the price of [similar products].",
        "🍬 Compare the amount of sugar of [input] and [similar products].",
        "⚠️ Compare the allergens of [input] and [similar products].",
        "🥣 Compare the ingredients of [input] and [similar products].",
        "📋 Give me an overview of the ingredients and nutrients of [similar products]."
    ]
    prompt_text = "\n".join(prompts)

    await update.message.reply_text(
        "❓ Please tell me your question.\n"
        f"You can ask something like:\n{prompt_text}",
    )
    return ASK_QUESTION

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the user's question and provides an answer."""
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    logger.info("Question from %s: %s", user.first_name, update.message.text)

    # Retrieve product_rag from context
    # product_rag = context.bot_data['product_rag']

    # User input description for the product
    input_description = "Sample product description for demonstration"  # Modify this as needed

    # Asking the question and getting the answer
    # answer = product_rag.ask_question(input_description, 3, context.user_data['question'])

    # await update.message.reply_text(answer)
    return ConversationHandler.END

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
    df_description = pd.DataFrame({
        'description': [
            "Lidl Belgian waffles 500g",
            "Netto maple syrup waffles 450g",
            "Lidl chocolate waffles 300g",
            "Netto classic waffles 500g",
            "Aldi blueberry waffles 400g"
        ]
    })

    # product_rag = ProductRAG(df_description, 'YOUR_OPENAI_API_KEY')
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7389289933:AAGiJFsmA6RZlXqGiPU8KcPHs1Troq7K-WY").build()
    # application.bot_data['product_rag'] = product_rag

    # Add conversation handler with the states ASK_IMAGE, ASK_COMPANY, ASK_QUESTION
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_IMAGE: [MessageHandler(filters.PHOTO, ask_image)],
            ASK_COMPANY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_company)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    # Add a handler for the welcome message
    application.add_handler(CommandHandler("start", start))
    
    try:
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")

if __name__ == "__main__":
    main()
