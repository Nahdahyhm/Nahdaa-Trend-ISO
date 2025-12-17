from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from datetime import datetime, date
from routes.login import login_bp
from routes.dashboard import dashboard_bp
from routes.sertifikasi import sertifikasi_bp
from routes.user import user_bp 
from flask import send_from_directory
import os
# import MySQLdb.cursors

app = Flask(__name__)
app.secret_key='your_secret_key'

#Konfigurasi koneksi MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'db_aplikasi'

mysql = MySQL(app)
app.config['mysql'] = mysql

@app.route('/')
def index():
    return redirect(url_for('login.login'))

app.register_blueprint(login_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(sertifikasi_bp)
app.register_blueprint(user_bp)

if __name__ == '__main__':
    app.run(debug=True)
