from flask import Flask, render_template, request
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
import os
from insert_product import insert_product
from sell_product import sell_product
from transactions import generate_report
from generate_qr_code import generate_qr_code

# Load environment variables from sql.env file
load_dotenv(dotenv_path='sql.env')

app = Flask(__name__)

# MySQL configurations using environment variables
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/insert', methods=['GET', 'POST'])
def insert():
    return insert_product()

@app.route('/sell', methods=['GET', 'POST'])
def sell():
    return sell_product()

@app.route('/generate_report')
def report():
    return generate_report()

@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        product_name = request.form['productName']
        qr_code_filename = f'{product_name}.png'
        
        generate_qr_code(product_name, qr_code_filename)
        
        return render_template('generate_qr.html', product_name=product_name, qr_code_filename=qr_code_filename)
    return render_template('generate_qr.html')

@app.route('/product_list')
def product_list():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM products')
    products = cursor.fetchall()
    
    # Calculate the total amount for each product
    for product in products:
        product['total_amount'] = product['price'] * product['quantity']
    
    cursor.close()
    return render_template('product_list.html', products=products)

if __name__ == '__main__':
    app.run(debug=True)
