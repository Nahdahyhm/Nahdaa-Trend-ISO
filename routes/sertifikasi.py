from flask import Blueprint, render_template, request, jsonify, current_app
from models import sertifikasi_model
from ses_login import login_required
from datetime import datetime, date #untuk inisiasi tanggal saat ini

sertifikasi_bp = Blueprint('sertifikasi', __name__, url_prefix='/sertifikasi')


@sertifikasi_bp.route('/')
@login_required
def sertifikasi():
    mysql = current_app.config['mysql']
    sertifikasi_model.auto_deactivate(mysql)  # Update status otomatis
    data = sertifikasi_model.get_all(mysql)
    mc_types = sertifikasi_model.get_mc_type(mysql)

    return render_template('sertifikasi.html', sertifikasi=data, mc_types=mc_types)

@sertifikasi_bp.route('/get_code_by_type/<mc_type>')
def get_code_by_type(mc_type):
    mysql = current_app.config['mysql']
    data = sertifikasi_model.get_code_by_type(mysql, mc_type)
    return jsonify(data)

@sertifikasi_bp.route('/get_description', methods=['GET'])
def get_description():
    mc_type = request.args.get('mc_type')
    mc_code = request.args.get('mc_code')

    mysql = current_app.config['mysql']
    desc = sertifikasi_model.get_description(mysql, mc_type, mc_code)
    return jsonify(desc) 

@sertifikasi_bp.route('/get/<int:id>')
@login_required
def get(id):
    mysql = current_app.config['mysql']
    data = sertifikasi_model.get_by_id(mysql, id)
    return jsonify(data)

@sertifikasi_bp.route('/save', methods=['POST'])
@login_required
def save():
    mysql = current_app.config['mysql']
    form = request.get_json()
    tgl_akhir = form['tgl_akhir']
    today = date.today().isoformat()
    status = 'Active' 
    if tgl_akhir :
        try:
            tgl_akhir_dt = datetime.strptime(tgl_akhir, '%Y-%m-%d').date()
            if tgl_akhir_dt < datetime.now().date():
                status = 'Deactive'
        except ValueError:
            pass

    id_sert = form.get('id_sert')
    if id_sert not in (None, "", "0"):  # UPDATE
        sertifikasi_model.update(mysql, (
            form['nama_client'],
            form['jenis_iso'],
            form['no_cert'],
            form['mc_type'],
            form['mc_code'],
            form['bidang_usaha'], 
            status,
            form['kota'],
            form['alamat'],
            form['tgl_awal'],
            form['tgl_akhir'],
            form['id_sert']
        ))
    else:  # INSERT
        sertifikasi_model.insert(mysql, (
            form['nama_client'],
            form['jenis_iso'],
            form['no_cert'],
            form['mc_type'],
            form['mc_code'],
            form['bidang_usaha'],  # sudah auto isi dari relasi
            status,
            form['kota'],
            form['alamat'],
            form['tgl_awal'],
            form['tgl_akhir']
        ))
    return jsonify({'status': 'success'})

@sertifikasi_bp.route('/get_client_by_kota', methods=['GET'])
def get_client_by_kota_route():
    kota = request.args.get('kota')
    if not kota:
        return jsonify({'status': 'error', 'message': 'Kota tidak diberikan'}), 400

    mysql = current_app.config['mysql']
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nama_client, status
        FROM sertifikasi
        WHERE kota = %s
        ORDER BY nama_client
    """, [kota])
    rows = cur.fetchall()
    cur.close()

    data = [{'nama_client': r[0], 'status': r[1]} for r in rows]

    return jsonify({'status': 'success', 'data': data})

@sertifikasi_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    mysql = current_app.config['mysql']
    sertifikasi_model.delete(mysql, id)
    return jsonify({'status': 'success'})