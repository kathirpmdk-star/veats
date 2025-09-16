

from flask import Flask, render_template, request, redirect, url_for, session, jsonify
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

# Cart count API for badge
@app.route('/cart_count')
def cart_count():
    cart = session.get('cart', [])
    return jsonify({'count': len(cart)})

import requests

# Cart page
@app.route('/cart')
def cart():
    cart = session.get('cart', [])
    total = sum(item['price'] * int(item['quantity']) for item in cart)
    return render_template('cart.html', cart=cart, total=total)

# Clear cart
@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect(url_for('cart'))

# Order/Checkout page
@app.route('/order', methods=['GET', 'POST'])
def order():
    cart = session.get('cart', [])
    total = sum(item['price'] * int(item['quantity']) for item in cart)
    if request.method == 'POST' and cart:
        payment_method = request.form['payment']
        # Simulate order number
        order_no = f"ORD{len(cart)}{total}"
        session['cart'] = []  # Clear cart after order
        return redirect(url_for('collect', order_no=order_no))
    return render_template('order.html', cart=cart, total=total)

# (Razorpay payment_success route removed)


food_courts = [
    {
        'id': 1,
        'name': 'Gymkhana',
        'shops': [
            {'id': 1, 'name': 'Gymkhana', 'menu': [
                {'id': 1, 'name': 'Chicken Chettinad Curry', 'price': 110, 'veg': False},
                {'id': 2, 'name': 'Chicken Fried Rice', 'price': 140, 'veg': False},
                {'id': 3, 'name': 'Chicken 65 Biryani', 'price': 150, 'veg': False},
                {'id': 4, 'name': 'Chicken Lollipop', 'price': 150, 'veg': False},
                {'id': 5, 'name': 'Quarter Tandoori Chicken', 'price': 100, 'veg': False},
                {'id': 6, 'name': 'Boiled Egg', 'price': 15, 'veg': False},
                {'id': 7, 'name': 'Plain Naan', 'price': 30, 'veg': True},
                {'id': 8, 'name': 'Vadai', 'price': 15, 'veg': True},
                {'id': 9, 'name': 'Tea', 'price': 20, 'veg': True},
                {'id': 10, 'name': 'Coffee', 'price': 20, 'veg': True},
            ]}
        ]
    },
    {
        'id': 2,
        'name': 'North Square',
        'shops': [
            {'id': 1, 'name': 'Georgia', 'menu': [
                {'id': 1, 'name': 'Lemon Tea', 'price': 15, 'veg': True},
                {'id': 2, 'name': 'Coffee', 'price': 20, 'veg': True},
                {'id': 3, 'name': 'Water Bottle', 'price': 10, 'veg': True},
                {'id': 4, 'name': 'Chicken Fried rice', 'price': 140, 'veg': False},
                {'id': 5, 'name': 'Chicken Biryani', 'price': 120, 'veg': False},
                {'id': 6, 'name': 'Chicken Samosa', 'price': 35, 'veg': False},
                {'id': 7, 'name': 'Samosa', 'price': 20, 'veg': True},
                {'id': 8, 'name': 'Panneer Puffs', 'price': 35, 'veg': True},
            ]}
        ]
    },
    {
        'id': 3,
        'name': 'Gazebo',
        'shops': [
            {'id': 1, 'name': 'Healthy & Tasty', 'menu': [
                {'id': 1, 'name': 'Veg Cheese Sandwich', 'price': 50, 'veg': True},
                {'id': 2, 'name': 'Chili Cheese Sandwich', 'price': 50, 'veg': True},
                {'id': 3, 'name': 'Chicken Noodles', 'price': 100, 'veg': False},
                {'id': 4, 'name': 'Egg Noodles', 'price': 90, 'veg': False},
                {'id': 5, 'name': 'Tea', 'price': 15, 'veg': True},
                {'id': 6, 'name': 'Coffee', 'price': 15, 'veg': True},
                {'id': 7, 'name': 'Sugarcane Juice', 'price': 40, 'veg': True},
                {'id': 8, 'name': 'Carrot Juice', 'price': 15, 'veg': True},
            ]},
            {'id': 2, 'name': 'Lassi House', 'menu': [
                {'id': 1, 'name': 'Nutella Milkshake', 'price': 90, 'veg': True},
                {'id': 2, 'name': 'Coffee Milkshake', 'price': 90, 'veg': True},
                {'id': 3, 'name': 'Red Velvet Milkshake', 'price': 90, 'veg': True},
            ]}
        ]
    }
]

@app.route('/')
def home():
    return render_template('home.html')

# Food court selection
@app.route('/foodcourts')
def foodcourts():
    return render_template('foodcourts.html', food_courts=food_courts)

# Shop selection
@app.route('/foodcourts/<int:court_id>')
def shops(court_id):
    court = next((fc for fc in food_courts if fc['id'] == court_id), None)
    if not court:
        return "Food court not found", 404
    return render_template('shops.html', court=court)

# Menu ordering
@app.route('/foodcourts/<int:court_id>/<int:shop_id>', methods=['GET', 'POST'])
def menu(court_id, shop_id):
    court = next((fc for fc in food_courts if fc['id'] == court_id), None)
    if not court:
        return "Food court not found", 404
    shop = next((s for s in court['shops'] if s['id'] == shop_id), None)
    if not shop:
        return "Shop not found", 404
    filter_type = request.args.get('filter', 'veg')
    if filter_type == 'veg':
        menu = [item for item in shop['menu'] if item['veg']]
    else:
        menu = [item for item in shop['menu'] if not item['veg']]
    if request.method == 'POST':
        item_id = int(request.form['item_id'])
        quantity = int(request.form['quantity'])
        item = next((i for i in shop['menu'] if i['id'] == item_id), None)
        if not item:
            return "Item not found", 404
        cart = session.get('cart', [])
        cart.append({
            'court_id': court_id,
            'court_name': court['name'],
            'shop_id': shop_id,
            'shop_name': shop['name'],
            'item_id': item_id,
            'item_name': item['name'],
            'price': item['price'],
            'quantity': quantity,
            'veg': item['veg']
        })
        session['cart'] = cart
        # Do not redirect; just return 200 for AJAX
        return ('', 204)
    cart_count = len(session.get('cart', []))
    return render_template('menu.html', court=court, shop=shop, menu=menu, filter_type=filter_type, cart_count=cart_count)

# Order collection page
@app.route('/collect/<order_no>')
def collect(order_no):
    return render_template('collect.html', order_no=order_no)


# In-memory order status store (for demo)
order_statuses = {}

# Order status page for users
@app.route('/order_status/<order_no>')
def order_status(order_no):
    status = order_statuses.get(order_no, 'Order Placed')
    return render_template('order_status.html', order_no=order_no, status=status)

# Admin page to update order status
@app.route('/admin/update_status', methods=['GET', 'POST'])
def update_status():
    message = ''
    if request.method == 'POST':
        order_no = request.form['order_no']
        status = request.form['status']
        order_statuses[order_no] = status
        message = f'Status for {order_no} updated to {status}.'
    return render_template('admin_update_status.html', message=message)

if __name__ == '__main__':
    app.run(debug=True)
