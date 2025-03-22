from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# AliExpress API credentials
APP_KEY = '512082'
APP_SECRET = '8ZR7b0XNh0DDSokcdW50ACF7yUCatSVY'
ALIEXPRESS_API_URL = 'https://api-sg.aliexpress.com/sync'

def fetch_product_details(product_url):
    try:
        params = {
            'app_key': APP_KEY,
            'app_secret': APP_SECRET,
            'method': 'aliexpress.affiliate.product.detail.get',
            'product_url': product_url,
        }
        response = requests.get(ALIEXPRESS_API_URL, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        print("API Response:", response.json())  # Log the full response
        return response.json()
    except requests.exceptions.RequestException as e:
        print("API Error:", e)
        return None

# Check if product supports Aliexpress Standard Shipping
def check_standard_shipping(product_details):
    shipping_info = product_details.get('result', {}).get('shipping_info', {})
    return shipping_info.get('aliexpress_standard_shipping', False)

# API endpoint
@app.route('/check-shipping', methods=['POST'])
def check_shipping():
    data = request.json
    product_url = data.get('product_url')
    if not product_url:
        return jsonify({'error': 'Product URL is required'}), 400
    product_details = fetch_product_details(product_url)
    if product_details:
        supports_standard_shipping = check_standard_shipping(product_details)
        return jsonify({'supports_standard_shipping': supports_standard_shipping})
    return jsonify({'error': 'Failed to fetch product details'}), 500

# Health check endpoint
@app.route('/')
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(debug=True)
