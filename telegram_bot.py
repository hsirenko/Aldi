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
import pandas as pd
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

#         print ('\n----------------------------------------------\n')
#         print ('similar_products: ', similar_products)
#         context = f"Input product: {input_description}. Products for comparison with input product: " + ", ".join(descriptions)
#         print ('\n----------------------------------------------\n')
#         print ('context:: ', context)
#         print ('\n----------------------------------------------\n')
#         return self.generate_response(question, context)


#     def generate_response(self, question, context):
#         openai.api_key = self.openai_api_key
#         prompt = f"Question: {question}\nContext: {context}\nAnswer:"
#         response = openai.ChatCompletion.create(
#             model='gpt-4o-2024-05-13',
#             temperature=0,
#             top_p=1,
#             frequency_penalty=0,
#             presence_penalty=0,
#             messages=[{"role": "system", "content": "You are a helpful assistant."},
#                       {"role": "user", "content": prompt}]
#         )
#         return response['choices'][0]['message']['content'].strip()




#Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Define conversation states
ASK_SCENARIO, ASK_QUESTION, ENTER_COMPETITOR, UPLOAD_IMAGE = range(4)

# Define the different scenarios and their corresponding prompts
scenarios = {
    'Scan Aldi Product': [
        "What are the similar products from competitors with comprehensive ingredient and nutrient data?",
        "What's the difference between Aldi Products and our competitor's similar products regarding ingredients and nutrients?",
        "What certifications (gluten-free, vegan, fair trade) do the competitor's product have?",
        "What would make our products more appealing compared to competitor's product?"
    ],
    'Scan Competitor Product': [
        "What are the similar products from other competitors with comprehensive ingredient and nutrient data?",
        "What's the difference between competitor's similar products regarding ingredients and nutrients?",
        "What certifications (gluten-free, vegan, fair trade) do the competitor's product have?",
        "What's the most similar product that Aldi have with comprehensive ingredient and nutrient data?"
    ]
}

# Define conversation states
ASK_SCENARIO, ASK_QUESTION, ENTER_COMPETITOR, UPLOAD_IMAGE = range(4)

# Define the different scenarios and their corresponding prompts
scenarios = {
    'Scan Aldi Product': [
        "What are the similar products from competitors with comprehensive ingredient and nutrient data?",
        "What's the difference between Aldi Products and our competitor's similar products regarding ingredients and nutrients?",
        "What certifications (gluten-free, vegan, fair trade) do the competitor's product have?",
        "What would make our products more appealing compared to competitor's product?"
    ],
    'Scan Competitor Product': [
        "What are the similar products from other competitors with comprehensive ingredient and nutrient data?",
        "What's the difference between competitor's similar products regarding ingredients and nutrients?",
        "What certifications (gluten-free, vegan, fair trade) do the competitor's product have?",
        "What's the most similar product that Aldi have with comprehensive ingredient and nutrient data?"
    ]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Starts the conversation and asks the user to choose a scenario."""
    reply_keyboard = [['Scan Aldi Product', 'Scan Competitor Product']]
    await update.message.reply_text(
        "Hi! I'm your product comparison bot. Choose a scenario:",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
    )
    return ASK_SCENARIO

async def ask_scenario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the chosen scenario and asks for a question."""
    user = update.message.from_user
    scenario = update.message.text
    context.user_data['scenario'] = scenario
    logger.info("Scenario from %s: %s", user.first_name, scenario)

    if scenario in scenarios:
        prompt_text = "You can ask questions like:\n" + "\n".join(scenarios[scenario])
        await update.message.reply_text(
            f"You chose: {scenario}\n{prompt_text}\n\nPlease ask your question:"
        )
    else:
        await update.message.reply_text("Please choose a valid scenario.")
        return ASK_SCENARIO

    return ASK_QUESTION

async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the question and asks for the competitor's name."""
    user = update.message.from_user
    context.user_data['question'] = update.message.text
    logger.info("Question from %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Got it. Now, enter the competitor name:",
    )
    return ENTER_COMPETITOR

async def enter_competitor(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the competitor's name and asks for a product image."""
    user = update.message.from_user
    context.user_data['competitor'] = update.message.text
    logger.info("Competitor name from %s: %s", user.first_name, update.message.text)
    await update.message.reply_text(
        "Great! Now, please upload an image of the product:",
    )
    return UPLOAD_IMAGE

async def upload_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Stores the product image and provides an output based on the scenario."""
    user = update.message.from_user
    photo_file = await update.message.photo[-1].get_file()
    await photo_file.download_to_drive("product_image.jpg")
    logger.info("Photo of %s: %s", user.first_name, "product_image.jpg")

    # Retrieve product_rag from context
    # product_rag = context.bot_data['product_rag']
    
    # Retrieve user inputs
    question = context.user_data['question']
    scenario = context.user_data['scenario']

    # User input description for ALDI's waffles
    if scenario == 'Scan Aldi Product':
        input_description = "Aldi's vanilla waffles 500g"
    else:
        input_description = context.user_data['competitor']  # Adjust this as needed

    # Asking the comparative question
    # answer = product_rag.ask_question(input_description, 3, question)

    # Print the answer provided by the RAG system
    # print(answer)

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

    # product_rag = ProductRAG(df_description, 'sk-proj-KPmObpzz1tZO2uSsVLdMT3BlbkFJZeQ8Q9Ys5H8K5CRRdtzH')
    
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("7389289933:AAGiJFsmA6RZlXqGiPU8KcPHs1Troq7K-WY").build()
    # application.bot_data['product_rag'] = product_rag

    # Add conversation handler with the states ASK_SCENARIO, ASK_QUESTION, ENTER_COMPETITOR, UPLOAD_IMAGE
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_SCENARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_scenario)],
            ASK_QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question)],
            ENTER_COMPETITOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, enter_competitor)],
            UPLOAD_IMAGE: [MessageHandler(filters.PHOTO, upload_image)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    try:
        # Run the bot until the user presses Ctrl-C
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"Exception occurred: {e}")

if __name__ == "__main__":
    main()
