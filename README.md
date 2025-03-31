---
# EasyCompare – AI-Powered Shopping Assistant 🚀

## **Overview**
EasyCompare is an AI-powered **Telegram chatbot** that allows users to compare products by sending **images and brand names**.  
It provides insights on **price, calories, allergens, ingredients, and nutrients** to assist in **data-driven procurement decisions**.

---

## 🚀 Getting Started  

### 1️⃣ Clone the Repository  
```bash
git clone -b streamlit_helen https://github.com/hsirenko/Aldi.git
cd Aldi
```

### 2️⃣ Set Up a Virtual Environment (Recommended)
```bash
python3 -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate     # For Windows
```

### 3️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Set Up Environment Variables
```bash
Create a .env file in the root directory and add the following:
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
API_URL=your_backend_api_url  # If applicable
Replace your_telegram_bot_token with the Telegram Bot API token obtained from BotFather.
```

### 5️⃣ Start the Server
```bash
python bot.py
```

This will launch the Telegram bot, allowing it to process incoming messages.

### 💬 How to Use the Telegram Chatbot  
1️⃣ Open Telegram and search for your bot.  
2️⃣ Start a chat with the bot using `/start`.  
3️⃣ Send an image of a product and specify the brand name in the message.  
4️⃣ The bot will analyze the image and return comparisons with similar products.  

### 🔧 Troubleshooting  
If the bot doesn't respond, check that:  
✅ The bot token is correctly set in `.env`  
✅ The server is running and listening for requests  
✅ Dependencies are correctly installed  
