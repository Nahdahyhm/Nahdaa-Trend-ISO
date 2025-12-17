from flask import Blueprint, render_template, request, redirect, url_for, session, current_app, flash
from models.user_model import check_user
login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pw = request.form['password']
        mysql = current_app.config['mysql']

        # Pakai check_user, tidak perlu query ulang
        user = check_user(mysql, username, pw)

        if user:
            session['username'] = user[1]
            session['user_id'] = user[0]
            session['photo'] = user[3]

            flash('Login berhasil', 'success')
            return render_template('logincoba.html') 
        else:
            flash('Username atau Password salah.', 'error')
            return redirect(url_for('login.login'))

    return render_template('logincoba.html')

@login_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login.login'))
