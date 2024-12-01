from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
import os
import qrcode
from pyzbar.pyzbar import decode
from PIL import Image

# Load environment variables from sql.env file
load_dotenv(dotenv_path='sql.env')

app = Flask(__name__)

# MySQL configurations using environment variables
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')

mysql = MySQL(app)

def generate_qr_code(data, filename):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')
    img.save(os.path.join('static', filename))

def decode_qr_code(file_path):
    img = Image.open(file_path)
    decoded_objects = decode(img)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return None

def insert_product():
    if request.method == 'POST':
        product_name = request.form.get('productName')
        price = request.form.get('price')
        quantity = request.form.get('quantity')
        qr_code = request.files.get('qrCode')

        if qr_code:
            # Save the uploaded QR code image
            qr_code_path = os.path.join('static', qr_code.filename)
            qr_code.save(qr_code_path)

            # Decode the QR code
            product_name = decode_qr_code(qr_code_path)
            if not product_name:
                return render_template('insert.html', error="Invalid QR code")

        price = float(price) if price else 0
        quantity = int(quantity) if quantity else 1

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM products WHERE name = %s', (product_name,))
        product = cursor.fetchone()

        if product:
            cursor.execute('UPDATE products SET quantity = quantity + %s, inserted = inserted + %s WHERE name = %s', (quantity, quantity, product_name))
        else:
            cursor.execute('INSERT INTO products (name, price, quantity, inserted) VALUES (%s, %s, %s, %s)', (product_name, price, quantity, quantity))

        cursor.execute('INSERT INTO transactions (product_name, transaction_type, quantity, price) VALUES (%s, %s, %s, %s)', (product_name, 'insert', quantity, price))

        mysql.connection.commit()

        # Generate and save QR code
        qr_code_filename = f'{product_name}.png'
        generate_qr_code(product_name, qr_code_filename)

        cursor.close()
        return render_template('insert.html', qr_code_filename=qr_code_filename, product_name=product_name)
    return render_template('insert.html')
