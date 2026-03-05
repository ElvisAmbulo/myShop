import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import config

app = Flask(__name__)

app.secret_key = "djfhfhgfjg-fghfh-fhfdDSewqerwrte-tutyiuyie"

app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    user = session.get('user')
    return render_template('index.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        firstName = request.form['firstName']
        secondName = request.form['secondName']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        address = request.form['address']
        image_file = request.files.get('image')

        filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)

        hashed_password = generate_password_hash(password)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO users (firstName, secondName, email, phone, password, address, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (firstName, secondName, email, phone, hashed_password, address, filename))
        mysql.connection.commit()
        cur.close()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        firstName = request.form['firstName']
        secondName = request.form['secondName']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE firstName=%s AND secondName=%s", (firstName, secondName))
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['user'] = f"{firstName} {secondName}"
            flash("Login successful!", "success")
            return redirect(url_for('index'))
        else:
            flash("Invalid username or password!", "danger")

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/myAccount', methods=['GET', 'POST'])
def myAccount():
    if 'user_id' not in session:
        flash("Please log in to access your account.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        firstName = request.form['firstName']
        secondName = request.form['lastName']
        email = request.form['email']
        phone = request.form['phone']

        image_file = request.files.get('profilePic')
        image_filename = None

        if image_file and image_file.filename != '':
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], image_filename)
            image_file.save(image_path)
        else:
            cur.execute("SELECT image FROM users WHERE id = %s", (user_id,))
            old_image = cur.fetchone()
            image_filename = old_image['image']

        cur.execute("""
            UPDATE users
            SET firstName=%s, secondName=%s, email=%s, phone=%s, image=%s
            WHERE id=%s
        """, (firstName, secondName, email, phone, image_filename, user_id))
        mysql.connection.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for('myAccount'))

    cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    cur.close()

    if not user.get('image'):
        user['image'] = 'default.png'

    return render_template('myAccount.html', user=user)

@app.route('/update_password', methods=['POST'])
def update_password():
    if 'user_id' not in session:
        return redirect('/login')

    current = request.form['currentPassword']
    new = request.form['newPassword']
    confirm = request.form['confirmPassword']

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()

    if not user or not check_password_hash(user['password'], current):
        flash("Current password is incorrect!", "danger")
        return redirect(url_for('myAccount'))
    elif new != confirm:
        flash("New passwords do not match!", "warning")
        return redirect(url_for('myAccount'))
    else:
        hashed = generate_password_hash(new)
        cur.execute("UPDATE users SET password=%s WHERE id=%s", (hashed, session['user_id']))
        mysql.connection.commit()
        cur.close()
        flash("Password updated successfully!", "success")
        return redirect(url_for('myAccount'))

@app.route('/shop')
def shop():
    page = int(request.args.get('page', 1))
    per_page = 16
    offset = (page - 1) * per_page

    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) AS total FROM products")
    total_products = cur.fetchone()['total']
    cur.execute("""
        SELECT id, name, category, nowPrice, wasPrice, rating, image
        FROM products
        ORDER BY id ASC
        LIMIT %s OFFSET %s
    """, (per_page, offset))
    items = cur.fetchall()
    cur.close()

    start_num = offset + 1
    end_num = min(offset + len(items), total_products)
    return render_template(
        'shop.html',
        items=items,
        total_products=total_products,
        showing_start=start_num,
        showing_end=end_num,
        page=page
    )

@app.route('/addProduct', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        description = request.form['description']
        nowPrice = request.form['nowPrice']
        wasPrice = request.form['wasPrice']
        rating = request.form['rating']
        availability = request.form['availability']
        skinType = request.form['skinType']
        volume = request.form['volume']
        span = request.form['span']
        applicationType = request.form['applicationType']
        packaging = request.form['packaging']
        image = request.files['image']

        filename = None
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(save_path)

        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO products 
            (name, category, description, nowPrice, wasPrice, rating, availability, skinType, volume, span, applicationType, packaging, image)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (name, category, description, nowPrice, wasPrice, rating, availability, skinType, volume, span, applicationType, packaging, filename))
        mysql.connection.commit()
        cur.close()

        flash("Product added successfully!", "success")
        return redirect(url_for('shop'))
    return render_template('addProduct.html')

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT * FROM products WHERE id = %s
    """, (product_id,))
    product = cur.fetchone()

    if not product:
        cur.close()
        return "Product not found", 404

    cur.execute("SELECT id, name, nowPrice, wasPrice, image FROM products ORDER BY RAND() LIMIT 4")
    relatedProducts = cur.fetchall()
    cur.close()

    return render_template('productDetails.html', product=product, relatedProducts=relatedProducts)

@app.route('/skin_care')
def skin_care():
    return render_template('skin_care.html')

@app.route('/makeup')
def makeup():
    return render_template('makeup.html')

@app.route('/hair_care')
def hair_care():
    return render_template('hair_care.html')

@app.route('/about')
def about():
    return render_template('about_us.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

#  RUN APP 
if __name__ == "__main__":
    app.run(debug=True, port=8000)
