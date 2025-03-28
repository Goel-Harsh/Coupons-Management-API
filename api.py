from flask import Flask, request, jsonify
import uuid
from typing import Tuple, Dict, Any, List, Optional

app = Flask(__name__)

# In-memory storage for coupons
coupons = []

# Constants for error messages
ERROR_INVALID_PAYLOAD = "Invalid payload"
ERROR_INVALID_CART_WISE_DETAILS = "Invalid cart-wise details"
ERROR_INVALID_PRODUCT_WISE_DETAILS = "Invalid product-wise details"
ERROR_INVALID_BXGY_DETAILS = "Invalid bxgy details"
ERROR_INVALID_COUPON_TYPE = "Invalid coupon type"
ERROR_COUPON_NOT_FOUND = "Coupon not found"
ERROR_SIMILAR_COUPON_EXISTS = "A similar coupon already exists"

def validate_cart_wise(details: Dict[str, Any]) -> Tuple[Optional[str], int]:
    if 'threshold' not in details or 'discount' not in details:
        return ERROR_INVALID_CART_WISE_DETAILS, 400
    return None, 200

def validate_product_wise(details: Dict[str, Any]) -> Tuple[Optional[str], int]:
    if 'product_id' not in details or 'discount' not in details:
        return ERROR_INVALID_PRODUCT_WISE_DETAILS, 400
    return None, 200

def validate_bxgy(details: Dict[str, Any]) -> Tuple[Optional[str], int]:
    if ('buy_products' not in details or 'get_products' not in details or
            'repetition_limit' not in details):
        return ERROR_INVALID_BXGY_DETAILS, 400
    if not isinstance(details['buy_products'], list) or not isinstance(details['get_products'], list):
        return "buy_products and get_products must be lists", 400
    for product in details['buy_products']:
        if 'product_id' not in product or 'quantity' not in product:
            return "Invalid buy_products structure", 400
    for product in details['get_products']:
        if 'product_id' not in product or 'quantity' not in product:
            return "Invalid get_products structure", 400
    if details['repetition_limit'] <= 0:
        return "Repetition limit must be greater than zero", 400
    return None, 200

def validate_coupon_payload(data: Dict[str, Any]) -> Tuple[Optional[str], int]:
    """Validate the structure of the coupon payload."""
    if not data or 'type' not in data or 'details' not in data:
        return ERROR_INVALID_PAYLOAD, 400

    details = data['details']
    if data['type'] == 'cart-wise':
        return validate_cart_wise(details)
    elif data['type'] == 'product-wise':
        return validate_product_wise(details)
    elif data['type'] == 'bxgy':
        return validate_bxgy(details)
    else:
        return ERROR_INVALID_COUPON_TYPE, 400

    return None, 200

def calculate_cart_total(products: Dict[str, Dict[str, Any]]) -> float:
    """Calculate the total price of the cart."""
    return sum(item['price'] * item['quantity'] for item in products.values())

@app.route('/coupons', methods=['POST'])
def create_coupon():
    data = request.get_json()
    error, status = validate_coupon_payload(data)
    if error:
        return jsonify({"error": error}), status

    # Check if a similar coupon already exists
    if any(coupon['type'] == data['type'] and coupon['details'] == data['details'] for coupon in coupons):
        return jsonify({"error": ERROR_SIMILAR_COUPON_EXISTS}), 400

    # Add a unique ID to the coupon
    data['id'] = str(uuid.uuid4())
    coupons.append(data)
    return jsonify({"message": "Coupon created successfully", "coupon": data}), 201

@app.route('/coupons', methods=['GET'])
def get_coupons():
    return jsonify({"coupons": coupons if coupons else "No coupons available"}), 200

@app.route('/coupons/<id>', methods=['GET'])
def get_coupon_by_id(id: str):
    coupon = next((c for c in coupons if c['id'] == id), None)
    if coupon:
        return jsonify({"coupon": coupon}), 200
    return jsonify({"error": ERROR_COUPON_NOT_FOUND}), 404

@app.route('/coupons/<id>', methods=['PUT'])
def update_coupon(id: str):
    data = request.get_json()
    if not data:
        return jsonify({"error": ERROR_INVALID_PAYLOAD}), 400

    error, status = validate_coupon_payload(data) if 'type' in data and 'details' in data else (None, 200)
    if error:
        return jsonify({"error": error}), status

    for coupon in coupons:
        if coupon['id'] == id:
            coupon.update({k: v for k, v in data.items() if k in ['type', 'details']})
            return jsonify({"message": "Coupon updated successfully", "coupon": coupon}), 200

    return jsonify({"error": ERROR_COUPON_NOT_FOUND}), 404

@app.route('/coupons/<id>', methods=['DELETE'])
def delete_coupon(id: str):
    global coupons
    coupons = [coupon for coupon in coupons if coupon['id'] != id]
    return jsonify({"message": "Coupon deleted successfully"}), 200

@app.route('/applicable-coupons', methods=['POST'])
def get_applicable_coupons():
    data = request.get_json()
    if not data or 'cart' not in data or 'products' not in data['cart']:
        return jsonify({"error": "Invalid cart structure"}), 400

    cart = data['cart']
    products = {item['product_id']: item for item in cart['products']}
    applicable_coupons = []

    for coupon in coupons:
        details = coupon['details']
        total_discount = 0

        if coupon['type'] == 'cart-wise':
            cart_total = calculate_cart_total(products)
            if cart_total >= details['threshold']:
                total_discount = details['discount']

        elif coupon['type'] == 'product-wise':
            product = products.get(details['product_id'])
            if product:
                total_discount = details['discount'] * product['quantity']

        elif coupon['type'] == 'bxgy':
            repetitions = min(
                (products.get(b['product_id'], {}).get('quantity', 0) // b['quantity'] for b in details['buy_products']),
                default=0
            )
            repetitions = min(repetitions, details['repetition_limit'])
            if repetitions > 0:
                for g in details['get_products']:
                    product = products.get(g['product_id'])
                    if product:
                        free_quantity = min(g['quantity'] * repetitions, product['quantity'])
                        total_discount += free_quantity * product['price']

        if total_discount > 0:
            applicable_coupons.append({
                "coupon_id": coupon['id'],
                "type": coupon['type'],
                "discount": total_discount
            })

    return jsonify({"applicable_coupons": applicable_coupons}), 200

@app.route('/apply-coupon/<id>', methods=['POST'])
def apply_coupon(id):
    data = request.get_json()
    if not data or 'cart' not in data or 'products' not in data['cart']:
        return jsonify({"error": "Invalid cart structure"}), 400

    cart = data['cart']
    products = {item['product_id']: item for item in cart['products']}
    coupon = next((c for c in coupons if c['id'] == id), None)
    if not coupon:
        return jsonify({"error": "Coupon not found"}), 404

    details = coupon['details']
    total_discount = 0
    updated_products = []

    if coupon['type'] == 'cart-wise':
        cart_total = sum(item['price'] * item['quantity'] for item in products.values())
        if cart_total >= details['threshold']:
            discount_per_item = details['discount'] / len(products)
            for item in products.values():
                discounted_price = max(0, item['price'] - discount_per_item / item['quantity'])
                updated_products.append({**item, "discounted_price": discounted_price})
            total_discount = details['discount']

    elif coupon['type'] == 'product-wise':
        for item in products.values():
            if item['product_id'] == details['product_id']:
                discounted_price = max(0, item['price'] - details['discount'])
                total_discount += details['discount'] * item['quantity']
                updated_products.append({**item, "discounted_price": discounted_price})
            else:
                updated_products.append(item)

    elif coupon['type'] == 'bxgy':
        repetitions = min(
            (products.get(b['product_id'], {}).get('quantity', 0) // b['quantity'] for b in details['buy_products']),
            default=0
        )
        repetitions = min(repetitions, details['repetition_limit'])
        if repetitions > 0:
            for item in products.values():
                if any(item['product_id'] == g['product_id'] for g in details['get_products']):
                    free_quantity = sum(
                        g['quantity'] * repetitions for g in details['get_products']
                        if g['product_id'] == item['product_id']
                    )
                    discounted_price = max(0, item['price'] * (item['quantity'] - free_quantity) / item['quantity'])
                    total_discount += free_quantity * item['price']
                    updated_products.append({**item, "discounted_price": discounted_price})
                else:
                    updated_products.append(item)

    return jsonify({
        "updated_cart": {"products": updated_products},
        "total_discount": total_discount
    }), 200
