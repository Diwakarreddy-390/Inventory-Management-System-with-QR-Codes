from flask import Flask, render_template, request, redirect, url_for
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
import os
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

def decode_qr_code(file_path):
    img = Image.open(file_path)
    decoded_objects = decode(img)
    for obj in decoded_objects:
        return obj.data.decode('utf-8')
    return None

def sell_product():
    scanned_items = []
    total_amount = 0
    if request.method == 'POST':
        product_name = request.form.get('productName')
        quantity = request.form.get('quantity')
        qr_code = request.files.get('qrCode')

        if qr_code:
            # Save the uploaded QR code image
            qr_code_path = os.path.join('static', qr_code.filename)
            qr_code.save(qr_code_path)

            # Decode the QR code
            product_name = decode_qr_code(qr_code_path)
            if not product_name:
                return render_template('sell.html', error="Invalid QR code")

        quantity = int(quantity) if quantity else 1

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        cursor.execute('SELECT * FROM products WHERE name = %s', (product_name,))
        product = cursor.fetchone()

        if product and product['quantity'] >= quantity:
            cursor.execute('UPDATE products SET quantity = quantity - %s, sold = sold + %s WHERE name = %s', (quantity, quantity, product_name))
            item_total = product['price'] * quantity
            cursor.execute('INSERT INTO transactions (product_name, transaction_type, quantity, price) VALUES (%s, %s, %s, %s)', (product_name, 'sell', quantity, product['price']))
            mysql.connection.commit()
            scanned_items.append({'name': product_name, 'quantity': quantity, 'price': product['price'], 'total': item_total})
            total_amount += item_total
        else:
            return render_template('sell.html', error="Insufficient quantity or product not found")

        cursor.close()
        return render_template('sell.html', scanned_items=scanned_items, total_amount=total_amount)
    return render_template('sell.html')
