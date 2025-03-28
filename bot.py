import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.utils.executor import start_webhook
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize bot and dispatcher
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

# Logging setup
logging.basicConfig(level=logging.INFO)

# Webhook settings
WEBHOOK_HOST = os.getenv('WEBHOOK_HOST')  # Your Vercel app URL
WEBHOOK_PATH = f"/webhook/{os.getenv('BOT_TOKEN')}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# Start command handler
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    await message.reply("Welcome to Ali Best Price Bot! Send me an AliExpress product link to get the best price and an affiliate link.")

# Link processing handler
@dp.message_handler(regexp=r'https?://[^\s]+')
async def process_link(message: types.Message):
    url = message.text
    if 'aliexpress.com' not in url:
        await message.reply("Please send a valid AliExpress product link.")
        return

    try:
        # Fetch product details using AliExpress API
        product_id = extract_product_id(url)
        product_details = fetch_product_details(product_id)

        if product_details:
            affiliate_link = generate_affiliate_link(url)
            response = f"Best Price: {product_details['price']}\nShipping: {product_details['shipping']}\nDiscount: {product_details['discount']}\nAffiliate Link: {affiliate_link}"
            await message.reply(response, parse_mode=ParseMode.MARKDOWN)
        else:
            await message.reply("Failed to fetch product details. Please try again later.")
    except Exception as e:
        logging.error(f"Error processing link: {e}")
        await message.reply("An error occurred while processing your request. Please try again later.")

# Admin command handler
@dp.message_handler(commands=['stats'])
async def send_stats(message: types.Message):
    # Placeholder for stats functionality
    await message.reply("Stats functionality will be implemented soon.")

# Helper functions
def extract_product_id(url):
    # Extract product ID from URL
    # This is a placeholder, you need to implement the actual logic
    return url.split('/')[-1].split('.html')[0]

def fetch_product_details(product_id):
    # Fetch product details using AliExpress API
    # This is a placeholder, you need to implement the actual API call
    return {
        'price': '$19.99',
        'shipping': 'Free Shipping',
        'discount': '10% off'
    }

def generate_affiliate_link(url):
    # Generate affiliate link using your credentials
    # This is a placeholder, you need to implement the actual logic
    return f"{url}?affiliate_key={os.getenv('ALIEXPRESS_APP_KEY')}&affiliate_secret={os.getenv('ALIEXPRESS_APP_SECRET')}"

# Flask route to handle webhook
@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook():
    update = types.Update(**request.json)
    await dp.process_update(update)
    return jsonify({"status": "ok"})

# Set webhook on startup
@app.route('/set_webhook', methods=['GET'])
async def set_webhook():
    await bot.set_webhook(WEBHOOK_URL)
    return jsonify({"status": "webhook set"})

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.getenv('PORT', 3000))
