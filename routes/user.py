from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
import os
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

user_bp = Blueprint('user', __name__, url_prefix='/user')


# ============================================================
# PAGE EDIT PROFIL
# ============================================================
@user_bp.route('/edit', methods=['GET'])
def edit_profile():
    mysql = current_app.config['mysql']
    user_id = session.get('user_id')

    cur = mysql.connection.cursor()
    cur.execute("SELECT username, photo FROM user WHERE id=%s", (user_id,))
    row = cur.fetchone()
    cur.close()

    user = {"username": "", "photo": None}
    if row:
        user["username"] = row[0]
        user["photo"] = row[1]

    return render_template('edit_profil.html', user=user)


# ============================================================
# UPDATE PROFIL
# ============================================================
@user_bp.route('/update', methods=['POST'])
def update_profile():
    mysql = current_app.config['mysql']
    user_id = session.get('user_id')

    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()
    photo_file = request.files.get('photo')

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # =======================
    # HANDLE FOTO PROFIL
    # =======================
    if photo_file and photo_file.filename != "":
        filename = secure_filename(photo_file.filename)   # simpan sesuai nama asli
        upload_path = os.path.join(upload_folder, filename)

        try:
            photo_file.save(upload_path)
        except Exception as e:
            flash(f"Gagal menyimpan foto: {str(e)}", "danger")
            return redirect(url_for('user.edit_profile'))

        # simpan nama foto ke database
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET photo=%s WHERE id=%s", (filename, user_id))
        mysql.connection.commit()
        cur.close()

        session['photo'] = filename  # update session

    # =======================
    # UPDATE USERNAME
    # =======================
    if username != "":
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET username=%s WHERE id=%s", (username, user_id))
        mysql.connection.commit()
        cur.close()

        session['username'] = username

    # =======================
    # UPDATE PASSWORD TANPA HASH
    # =======================
    if password != "":
        cur = mysql.connection.cursor()
        cur.execute("UPDATE user SET password=%s WHERE id=%s", (password, user_id))
        mysql.connection.commit()
        cur.close()

    flash("Profil berhasil diperbarui", "success")
    return redirect(url_for('dashboard.dashboard'))