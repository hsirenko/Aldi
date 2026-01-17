---
# EasyCompare – AI-Powered Shopping Assistant 🚀

## **Overview**
EasyCompare is an AI-powered **Telegram chatbot** that allows users to compare products by sending **images and brand names**.  
It provides insights on **price, calories, allergens, ingredients, and nutrients** to assist in **data-driven procurement decisions**.

---
EasyCompare, an AI-powered shopping assistant built during HerHackathon 2024 in Mannheim. It was my first-ever hackathon, and I joined with zero expectations—but ended up winning!

🌟 What is EasyCompare?
EasyCompare was designed for procurement and category managers and built during HerHackathon 2024 in Mannheim.

The concept is simple:
📸 Snap a photo of a product sold at Aldi 
🏷 Specify the brand
❓ Ask questions about price, calories, allergens, ingredients, or nutrients
🔍 Instantly compare similar products, helping teams make faster, data-driven purchasing decisions.

🔧 My Contributions
Hackathon Execution & Product Vision – Led the strategic direction, ensuring the solution aligned with ALDI Süd's business needs. I also took charge of pitching the product to stakeholders, demonstrating its real-world impact.

User Input & Processing – Designed and implemented the user interaction flow, allowing users to submit product images and brand names via Telegram, using Python and the Telegram Bot API. Contributed to designing a scalable and modular system, ensuring efficient data flow from user input to AI analysis and output generation, using Flask and FastAPI.

🎬 Want to see the full journey?
Check out this page for a detailed breakdown, technical insights, and behind-the-scenes decisions:
👉 https://galvanized-plough-704.notion.site/Easy-Compare-ChatBot-for-AldiSud-1c762a11e1ec808692c9d779825d2361

This project proved to me that having the right skills, mindset, strategy, and product vision can lead to unexpected wins. It also reinforced my passion for building smart, user-friendly products that solve real business challenges. 🚀

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
