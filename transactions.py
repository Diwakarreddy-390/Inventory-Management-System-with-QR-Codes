from flask import Flask, render_template
from flask_mysqldb import MySQL
import MySQLdb.cursors
from dotenv import load_dotenv
import os

# Load environment variables from sql.env file
load_dotenv(dotenv_path='sql.env')

app = Flask(__name__)

# MySQL configurations using environment variables
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')

mysql = MySQL(app)

def generate_report():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    # Fetch transaction history
    cursor.execute('SELECT * FROM transactions ORDER BY transaction_date DESC')
    transactions = cursor.fetchall()

    cursor.close()
    return render_template('generate_report.html', transactions=transactions)
