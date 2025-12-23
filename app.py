import sqlite3
import os
import base64
import json
import random
import string
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'super_secret_key'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100 MB limit
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# --- INITIAL PRODUCT LIST ---
initial_products = [
    {"id": 1, "category": "phones", "name": "iPhone 17 Pro", "price": 500000, "desc": "Titanium body, A17 Pro chip.", "img": "https://pi.mdev.kz/29623eb0-1c34-4a60-99a9-3c3ef5cbe459", "specs": {"Screen": "6.1", "Memory": "128 GB"}},
    {"id": 10, "category": "phones", "name": "Samsung S25 Ultra", "price": 550000, "desc": "Artificial Intelligence in your hand.", "img": "https://encrypted-tbn0.gstatic.com/shopping?q=tbn:ANd9GcTYypDzRLsk-LUQLA4WUwOwNz0Pqkh6uG9Xvmly9tKQdEN_y9HgFyrvcsr6TMa2REFjmkT6p9pt0YZhMB-ejWMWtTt5IR1v5uqoPypiA4B_g_DibX7SVuBUEwyyo33KPyxnYSuM2D5Ymw&usqp=CAc", "specs": {"Screen": "6.8", "Memory": "256 GB"}},
    {"id": 11, "category": "phones", "name": "Google Pixel 8", "price": 380000, "desc": "Best camera on Android.", "img": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcQogcuKFrxx2ze335r2Auya-atoZ6914pJcprw1rX-arWmWJePJupl6F6nc5lJ3P5X_ct9EmKFmOQsPCS0kSH7Oe8cV8wrFgIUyjT1fQF6stJ4y5E1ZG35sNMCV1BQ_d82mKnPC4aPs&usqp=CAc", "specs": {"Screen": "6.2", "RAM": "8 GB"}},
    {"id": 12, "category": "phones", "name": "Xiaomi 13T", "price": 250000, "desc": "200 MP Ultra-clear camera.", "img": "https://gadgetstore.kz/wa-data/public/shop/products/88/08/888/images/2567/2567.750x0.jpg", "specs": {"Charging": "120W", "Camera": "200 MP"}},
    {"id": 2, "category": "laptops", "name": "MacBook Air M2", "price": 450000, "desc": "Super light and thin.", "img": "https://pi.mdev.kz/b7b149bf-7350-4fa5-bd87-e982add4d908", "specs": {"CPU": "M2", "SSD": "256 GB"}},
    {"id": 14, "category": "laptops", "name": "ASUS ROG Strix", "price": 600000, "desc": "Gaming powerhouse station.", "img": "https://itmag.kz/upload/iblock/8/93/product_image_116493_1346673.png", "specs": {"GPU": "RTX 4060", "Screen": "165Hz"}},
    {"id": 15, "category": "laptops", "name": "Lenovo ThinkPad", "price": 350000, "desc": "Professional business solution.", "img": "https://itmag.kz/upload/iblock/8/39/product_image_124839_1380975.jpg", "specs": {"Body": "Carbon", "OS": "Windows 11"}},
    {"id": 3, "category": "audio", "name": "Sony WH-1000XM5", "price": 120000, "desc": "Industry leading noise cancellation.", "img": "https://metapod.com/cdn/shop/files/1_WH-1000XM5_standard_smokypink-Mid.png?v=1754022978&width=800", "specs": {"ANC": "Active"}},
    {"id": 6, "category": "audio", "name": "AirPods Pro 2", "price": 110000, "desc": "Magical sound experience.", "img": "https://static.shop.kz/upload/resize_cache/iblock/ee9/d2o6mq3sa0of2025sewl6tbvo7j77ji3/450_450_1/165098o3.JPG", "specs": {"Chip": "H2"}},
    {"id": 16, "category": "audio", "name": "JBL Flip 6", "price": 45000, "desc": "Powerful portable speaker.", "img": "https://i.ebayimg.com/images/g/ayQAAOSwXBNkf06D/s-l1600.webp", "specs": {"Rating": "IP67"}},
    {"id": 4, "category": "gadgets", "name": "Apple Watch Ultra", "price": 350000, "desc": "Built for extreme adventures.", "img": "https://cdn.new-brz.net/app/public/models/MQFX3GK-A/large/w/220915160012587216.webp", "specs": {"Case": "Titanium"}},
    {"id": 5, "category": "gadgets", "name": "PlayStation 5", "price": 260000, "desc": "Gaming in 4K resolution.", "img": "https://object.pscloud.io/cms/cms/Photo/img_0_68_256_0_1_WKMNNT.webp", "specs": {"SSD": "825 GB"}},
    {"id": 7, "category": "gadgets", "name": "iPad Air", "price": 300000, "desc": "High performance tablet.", "img": "https://pi.mdev.kz/9132eb57-3380-11ef-a267-005056b6e990", "specs": {"Chip": "M1"}},
    {"id": 8, "category": "gadgets", "name": "GoPro Hero 11", "price": 180000, "desc": "Action camera with stabilization.", "img": "https://drone.kz/upload/resize_cache/webp/iblock/583/dwi73h7aaewelcmoxu7vbcju5f1t5cx8/1_2_.webp", "specs": {"Video": "5.3K"}},
    {"id": 9, "category": "gadgets", "name": "Dyson Supersonic", "price": 220000, "desc": "Fastest hair drying.", "img": "https://cdn.halykmarket.kz/s3/product/pim/sku-variations/1207528836/product-1357917-9856.jpg", "specs": {"Motor": "V9"}},
    {"id": 20, "category": "gpu", "name": "NVIDIA RTX 4090", "price": 1100000, "desc": "The king of gaming GPUs.", "img": "https://images.unsplash.com/photo-1591488320449-011701bb6704?auto=format&fit=crop&w=500&q=60", "specs": {"VRAM": "24 GB"}},
    {"id": 21, "category": "gpu", "name": "NVIDIA RTX 4070 Ti", "price": 450000, "desc": "Perfect for 2K gaming.", "img": "https://static.shop.kz/upload/resize_cache/iblock/7c4/8tyflcojzto3anjt7uy5g1hne8251uq0/450_450_1/185997e1.webp", "specs": {"VRAM": "12 GB"}},
    {"id": 30, "category": "cpu", "name": "Intel Core i9-14900K", "price": 320000, "desc": "24 cores for performance.", "img": "https://static.shop.kz/upload/resize_cache/iblock/19a/rjntw77quzi1jrp5lb3n3ywkpbkii8m7/450_450_1/174587a1.webp", "specs": {"Frequency": "6.0 GHz"}},
    {"id": 31, "category": "cpu", "name": "AMD Ryzen 7 7800X3D", "price": 230000, "desc": "Ultimate gaming processor.", "img": "https://static.shop.kz/upload/resize_cache/iblock/e37/h0io53bqq296r72id3efziwxfcfkb5bd/450_450_1/175290x1.webp", "specs": {"Cache": "3D V-Cache"}},
]

# --- DATABASE INITIALIZATION ---
def init_db():
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL, 
            password TEXT NOT NULL,
            status INTEGER DEFAULT 0, 
            doc_image TEXT,
            rejection_reason TEXT,
            is_admin INTEGER DEFAULT 0)''')
    c.execute('''CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            category TEXT, name TEXT, price INTEGER, desc TEXT, img TEXT, specs TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            order_details TEXT,
            total_price INTEGER,
            address TEXT,
            status TEXT DEFAULT 'New')''')
    c.execute('''CREATE TABLE IF NOT EXISTS password_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    try:
        c.execute("INSERT INTO users (email, password, status, is_admin) VALUES (?, ?, ?, ?)", ('admin@shop.kz', 'admin', 2, 1))
    except: pass
    c.execute("SELECT count(*) FROM products")
    if c.fetchone()[0] == 0:
        for p in initial_products:
            specs_json = json.dumps(p.get('specs', {}), ensure_ascii=False)
            c.execute("INSERT INTO products (id, category, name, price, desc, img, specs) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (p['id'], p['category'], p['name'], p['price'], p['desc'], p['img'], specs_json))
    conn.commit()
    conn.close()

init_db()

# --- HELPER FUNCTIONS ---
def get_products_from_db():
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute("SELECT * FROM products")
    rows = c.fetchall()
    conn.close()
    products_list = []
    for row in rows:
        p = dict(row)
        if p['specs']: p['specs'] = json.loads(p['specs'])
        products_list.append(p)
    return products_list

# Generate Temp Password
def generate_temp_password(length=6):
    chars = string.ascii_uppercase + string.digits
    return 'Temp-' + ''.join(random.choice(chars) for _ in range(length))

# --- ROUTES ---

@app.route('/')
def index(): return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            conn = sqlite3.connect('shop.db')
            c = conn.cursor()
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            conn.close()
            flash('Registration successful!')
            return redirect(url_for('login'))
        except: flash('Email already taken.')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute("SELECT id, status, is_admin, email FROM users WHERE email = ? AND password = ?", (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['user_id'] = user[0]
            session['status'] = user[1]
            session['is_admin'] = user[2]
            session['email'] = user[3]
            return redirect(url_for('dashboard'))
        else: flash('Invalid credentials.')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/kyc', methods=['GET', 'POST'])
def kyc():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("SELECT status, rejection_reason FROM users WHERE id = ?", (session['user_id'],))
    data = c.fetchone()
    conn.close()
    current_status = data[0]
    reason = data[1]
    session['status'] = current_status
    if current_status == 2: return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        file = request.files.get('document')
        webcam_image = request.form.get('webcam_image')
        filename = None
        if file and file.filename != '':
            filename = secure_filename(f"user_{session['user_id']}_{file.filename}")
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        elif webcam_image:
            header, encoded = webcam_image.split(",", 1)
            data = base64.b64decode(encoded)
            filename = f"user_{session['user_id']}_webcam.png"
            with open(os.path.join(app.config['UPLOAD_FOLDER'], filename), "wb") as f:
                f.write(data)
        if filename:
            conn = sqlite3.connect('shop.db')
            c = conn.cursor()
            c.execute("UPDATE users SET status = 1, doc_image = ?, rejection_reason = NULL WHERE id = ?", (filename, session['user_id']))
            conn.commit()
            conn.close()
            return redirect(request.url)
    return render_template('kyc.html', status=current_status, reason=reason)

# --- ADMIN PANEL ---
@app.route('/admin')
def admin():
    if not session.get('is_admin'): return redirect(url_for('dashboard'))
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("SELECT id, email, doc_image FROM users WHERE status = 1")
    users = c.fetchall()
    
    c.execute("SELECT * FROM orders ORDER BY id DESC")
    orders = c.fetchall()
    
    c.execute("SELECT * FROM password_requests ORDER BY id DESC")
    pwd_requests = c.fetchall()
    
    products_db = get_products_from_db()
    conn.close()
    return render_template('admin.html', users=users, products=products_db, orders=orders, pwd_requests=pwd_requests)

# --- APPROVE PASSWORD RESET (Generate Temp Password) ---
@app.route('/admin/approve_reset/<int:req_id>')
def approve_reset(req_id):
    if not session.get('is_admin'): return redirect(url_for('dashboard'))
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    
    c.execute("SELECT email FROM password_requests WHERE id = ?", (req_id,))
    req = c.fetchone()
    
    if req:
        user_email = req[0]
        temp_password = generate_temp_password()
        c.execute("UPDATE users SET password = ? WHERE email = ?", (temp_password, user_email))
        c.execute("DELETE FROM password_requests WHERE id = ?", (req_id,))
        conn.commit()
        flash(f'SUCCESS! Password reset for {user_email}. TEMPORARY PASSWORD: {temp_password}')
    
    conn.close()
    return redirect(url_for('admin'))

# --- REJECT PASSWORD RESET ---
@app.route('/admin/reject_reset/<int:req_id>')
def reject_reset(req_id):
    if not session.get('is_admin'): return redirect(url_for('dashboard'))
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("DELETE FROM password_requests WHERE id = ?", (req_id,))
    conn.commit()
    conn.close()
    flash('Password reset request rejected and removed.')
    return redirect(url_for('admin'))

@app.route('/admin/edit_product', methods=['POST'])
def edit_product():
    if not session.get('is_admin'): return redirect(url_for('dashboard'))
    p_id = request.form['id']
    new_price = request.form['price']
    new_desc = request.form['desc']
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("UPDATE products SET price = ?, desc = ? WHERE id = ?", (new_price, new_desc, p_id))
    conn.commit()
    conn.close()
    flash(f'Product {p_id} updated!')
    return redirect(url_for('admin'))

@app.route('/approve/<int:user_id>')
def approve(user_id):
    if not session.get('is_admin'): return redirect(url_for('dashboard'))
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("UPDATE users SET status = 2 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    flash(f'User {user_id} approved!')
    return redirect(url_for('admin'))

@app.route('/reject/<int:user_id>', methods=['POST'])
def reject(user_id):
    if not session.get('is_admin'): return redirect(url_for('dashboard'))
    reason = request.form.get('reason', 'Documents do not meet requirements.') 
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("UPDATE users SET status = 3, rejection_reason = ? WHERE id = ?", (reason, user_id))
    conn.commit()
    conn.close()
    flash(f'User {user_id} rejected.')
    return redirect(url_for('admin'))

# --- DASHBOARD ---
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session: return redirect(url_for('login'))
    if session.get('status') != 2: return redirect(url_for('kyc'))
    products_db = get_products_from_db()
    category = request.args.get('category', 'all')
    sort_by = request.args.get('sort')
    if category == 'None': category = 'all'
    filtered = products_db
    if category and category != 'all':
        filtered = [p for p in filtered if p['category'] == category]
    if sort_by == 'price_asc': filtered.sort(key=lambda x: x['price'])
    elif sort_by == 'price_desc': filtered.sort(key=lambda x: x['price'], reverse=True)
    return render_template('dashboard.html', products=filtered, current_cat=category, current_sort=sort_by)

@app.route('/add_to_cart/<int:product_id>')
def add_to_cart(product_id):
    if 'cart' not in session: session['cart'] = []
    cart = session['cart']
    if product_id not in cart:
        cart.append(product_id)
        flash('Item added to order list.')
    else:
        flash('This item is already in your cart.')
    session['cart'] = cart
    return redirect(request.referrer or url_for('dashboard'))

@app.route('/cart')
def cart():
    if 'user_id' not in session: return redirect(url_for('login'))
    products_db = get_products_from_db()
    cart_ids = session.get('cart', [])
    cart_items = [p for p in products_db if p['id'] in cart_ids]
    return render_template('cart.html', cart_items=cart_items)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session: return redirect(url_for('login'))
    
    address = request.form.get('address')
    products_db = get_products_from_db()
    cart_ids = session.get('cart', [])
    
    order_text_list = []
    total_price = 0
    
    for p in products_db:
        if p['id'] in cart_ids:
            qty = int(request.form.get(f"qty_{p['id']}", 0))
            if qty < 10:
                flash(f'Error! Minimum quantity is 10 for: {p["name"]}')
                return redirect(url_for('cart'))
            cost = p['price'] * qty
            total_price += cost
            order_text_list.append(f"{p['name']} (x{qty})")
    
    if not order_text_list:
        flash('Your cart is empty.')
        return redirect(url_for('cart'))

    order_details = ", ".join(order_text_list)
    conn = sqlite3.connect('shop.db')
    c = conn.cursor()
    c.execute("INSERT INTO orders (user_email, order_details, total_price, address) VALUES (?, ?, ?, ?)",
              (session.get('email'), order_details, total_price, address))
    conn.commit()
    conn.close()
    
    session['cart'] = []
    flash('Order placed! A manager will contact you shortly.')
    return redirect(url_for('dashboard'))

@app.route('/clear_cart')
def clear_cart():
    session['cart'] = []
    return redirect(url_for('cart'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        conn = sqlite3.connect('shop.db')
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE email = ?", (email,))
        user = c.fetchone()
        
        if user:
            c.execute("INSERT INTO password_requests (email) VALUES (?)", (email,))
            conn.commit()
            conn.close()
            flash('Request sent! Security administrator notified.')
            return redirect(url_for('login'))
        else:
            conn.close()
            flash('Error: This email is not registered in our system.')
            
    return render_template('forgot_password.html')

if __name__ == '__main__':
    app.run(debug=True)