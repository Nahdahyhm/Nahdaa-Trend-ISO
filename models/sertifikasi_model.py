from datetime import date

def get_all(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.id_sert, s.nama_client, s.jenis_iso, s.no_cert, s.mc_type, s.mc_code,
               m.mc_description AS bidang_usaha,
               s.status, s.kota, s.alamat, s.tgl_awal, s.tgl_akhir
        FROM sertifikasi s
        LEFT JOIN md_code m 
            ON s.mc_code = m.mc_code 
           AND s.mc_type = m.mc_type
        ORDER BY s.id_sert DESC
    """)
    result = cur.fetchall()
    cur.close()
    return result


def get_by_id(mysql, id_sert):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT s.id_sert, s.nama_client, s.jenis_iso, s.no_cert, 
            s.mc_type, s.mc_code, m.mc_description, 
            s.kota, s.alamat, 
            s.tgl_awal, s.tgl_akhir
        FROM sertifikasi s
        LEFT JOIN md_code m 
            ON s.mc_code = m.mc_code
           AND s.mc_type = m.mc_type
        WHERE s.id_sert = %s
    """, [id_sert])
    row = cur.fetchone()
    cur.close()

    if row:
        return {
            'id_sert': row[0],
            'nama_client': row[1],
            'jenis_iso': row[2],
            'no_cert': row[3],
            'mc_type': row[4],
            'mc_code': row[5],
            'bidang_usaha': row[6],
            'kota': row[7],
            'alamat': row[8],
            'tgl_awal': row[9].strftime('%Y-%m-%d') if row[9] else '',
            'tgl_akhir': row[10].strftime('%Y-%m-%d') if row[10] else '',
        }
    return {}


def get_mc_type(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT mc_type FROM md_code ORDER BY mc_type")
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


def get_code_by_type(mysql, mc_type):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DISTINCT mc_code 
        FROM md_code
        WHERE mc_type = %s
        ORDER BY mc_code
    """, [mc_type])
    rows = cur.fetchall()
    cur.close()
    return [r[0] for r in rows]


def get_description(mysql, mc_type, mc_code):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT mc_description
        FROM md_code
        WHERE mc_type = %s AND mc_code = %s
        LIMIT 1
    """, [mc_type, mc_code])
    row = cur.fetchone()
    cur.close()
    return row[0] if row else ""  


def insert(mysql, data):
    cur = mysql.connection.cursor()
    cur.execute("""
        INSERT INTO sertifikasi(
        nama_client, jenis_iso, no_cert, 
        mc_type, mc_code, bidang_usaha, 
        status, kota, alamat, tgl_awal, tgl_akhir
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """, data)
    mysql.connection.commit()
    cur.close()


def update(mysql, data):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE sertifikasi SET 
            nama_client=%s, jenis_iso=%s, no_cert=%s, 
            mc_type=%s, mc_code=%s, bidang_usaha=%s,
            status=%s, kota=%s, alamat=%s, 
            tgl_awal=%s, tgl_akhir=%s
        WHERE id_sert=%s
    """, data)
    mysql.connection.commit()
    cur.close()


def delete(mysql, id_sert):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM sertifikasi WHERE id_sert = %s", [id_sert])
    mysql.connection.commit()
    cur.close()


def auto_deactivate(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        UPDATE sertifikasi
        SET status = 'Deactive'
        WHERE tgl_akhir < CURDATE() AND status != 'Deactive'
    """)
    mysql.connection.commit()
    cur.close()

def count_per_jenis(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT jenis_iso, COUNT(*) FROM sertifikasi
        GROUP BY jenis_iso
    """)
    result = cur.fetchall()
    cur.close()
    return result


def count_trend(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(tgl_awal, '%Y-%m') AS bulan, COUNT(*)
        FROM sertifikasi
        GROUP BY bulan
        ORDER BY bulan
    """)
    result = cur.fetchall()
    cur.close()
    return result


def trend_per_month(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(tgl_awal, '%Y-%m') AS bulan, COUNT(*)
        FROM sertifikasi
        GROUP BY bulan
        ORDER BY bulan
    """)
    result = cur.fetchall()
    cur.close()
    return result


def count_perusahaan(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(DISTINCT nama_client) FROM sertifikasi")
    result = cur.fetchone()[0]
    cur.close()
    return result


def count_sertifikat(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(DISTINCT jenis_iso) FROM sertifikasi")
    result = cur.fetchone()[0]
    cur.close()
    return result


def count_active(mysql):
    cur = mysql.connection.cursor()
    cur.execute("SELECT COUNT(*) FROM sertifikasi WHERE status = 'Active'")
    result = cur.fetchone()[0]
    cur.close()
    return result

def tren_iso(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT jenis_iso, COUNT(*) AS total
        FROM sertifikasi
        GROUP BY jenis_iso
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    cur.close()

    if rows:
        return [{'jenis_iso': row[0], 'total': row[1]} for row in rows]
    else:
        return []


def chart_per_jenis(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT jenis_iso, COUNT(*) 
        FROM sertifikasi 
        GROUP BY jenis_iso 
        ORDER BY COUNT(*) DESC
    """)
    rows = cur.fetchall()
    cur.close()
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return labels, data


def chart_trend(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT DATE_FORMAT(tgl_awal, '%Y-%m') as bulan, COUNT(*) 
        FROM sertifikasi
        GROUP BY bulan
        ORDER BY bulan
    """)
    rows = cur.fetchall()
    cur.close()
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return labels, data


def chart_per_usaha(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT bidang_usaha, COUNT(*) 
        FROM sertifikasi
        GROUP BY bidang_usaha 
        ORDER BY COUNT(*) DESC
    """)
    rows = cur.fetchall()
    cur.close()
    labels = [r[0] for r in rows]
    data = [r[1] for r in rows]
    return labels, data


def get_growing_trend(mysql):
    _, trend_data = chart_trend(mysql)
    if len(trend_data) >= 2:
        last = trend_data[-1]
        prev = trend_data[-2]
        if prev > 0:
            percent = round(((last - prev) / prev) * 100, 1)
            return percent
    return 0


def get_growing_trend_per_jenis_per_tahun(mysql):
    cur = mysql.connection.cursor()

    cur.execute("""
        SELECT jenis_iso, COUNT(*) FROM sertifikasi
        WHERE YEAR(tgl_awal) = YEAR(CURDATE())
        GROUP BY jenis_iso
    """)
    data_ini_rows = cur.fetchall()
    data_ini = {row[0]: row[1] for row in data_ini_rows}
    total_ini = sum(data_ini.values())

    cur.execute("""
        SELECT jenis_iso, COUNT(*) FROM sertifikasi
        WHERE YEAR(tgl_awal) = YEAR(CURDATE()) - 1
        GROUP BY jenis_iso
    """)
    data_lalu_rows = cur.fetchall()
    data_lalu = {row[0]: row[1] for row in data_lalu_rows}
    total_lalu = sum(data_lalu.values())

    jenis_set = set(data_ini.keys()) | set(data_lalu.keys())

    growing = []
    for jenis in jenis_set:
        ini = data_ini.get(jenis, 0)
        lalu = data_lalu.get(jenis, 0)

        share_ini = ini / total_ini if total_ini > 0 else 0
        share_lalu = lalu / total_lalu if total_lalu > 0 else 0

        percent = round((share_ini - share_lalu) * 100)
        trend = 'up' if percent >= 0 else 'down'

        growing.append({
            'jenis_iso': jenis,
            'percent': abs(percent),
            'trend': trend
        })

    trend_up = sorted([g for g in growing if g['trend'] == 'up'],
                      key=lambda x: x['percent'], reverse=True)[:3]
    trend_down = sorted([g for g in growing if g['trend'] == 'down'],
                        key=lambda x: x['percent'], reverse=True)[:3]

    return trend_up, trend_down


def get_rekomendasi_bidang_usaha(mysql):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT bidang_usaha, COUNT(*) as total
        FROM sertifikasi
        GROUP BY bidang_usaha
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    cur.close()

    if not rows:
        return {
            'top': {},
            'bottom': {},
            'marketing': 'Tidak ada data.'
        }

    top = {'bidang_usaha': rows[0][0], 'total': rows[0][1]}
    bottom = {'bidang_usaha': rows[-1][0], 'total': rows[-1][1]}

    marketing = (
        f"Bidang usaha dengan jumlah paling sedikit: {bottom['bidang_usaha']}. "
        "Strategi promosi: Analisis SWOT, identifikasi target pasar, testimoni klien,"
        "dan insentif diskon untuk menarik minat."
    )

    return {
        'top': top,
        'bottom': bottom,
        'marketing': marketing
    }

def get_top_kota(mysql, limit=10):
    cur = mysql.connection.cursor()
    cur.execute(f"""
        SELECT kota, COUNT(*) AS total
        FROM sertifikasi
        WHERE kota IS NOT NULL AND kota <> ''
        GROUP BY kota
        ORDER BY total DESC
        LIMIT {limit}
    """)
    rows = cur.fetchall()
    cur.close()

    result = [{'kota': r[0], 'total': r[1]} for r in rows]
    return result

  
def get_total_sertifikat_per_kota(mysql):
   
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            MIN(nama_client) AS nama_client, 
            kota, 
            COUNT(*) AS total
        FROM sertifikasi
        WHERE kota IS NOT NULL AND kota <> ''
        GROUP BY kota
        ORDER BY total DESC
    """)
    rows = cur.fetchall()
    cur.close()

    return [
        {'nama_client': row[0], 'kota': row[1], 'total': row[2]}
        for row in rows
    ]

def get_client_by_kota(mysql, kota):
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT nama_client, status
        FROM sertifikasi
        WHERE kota = %s
        ORDER BY nama_client
    """, [kota])
    rows = cur.fetchall()
    cur.close()

    return [
        {'nama_client': r[0], 'status': r[1]}
        for r in rows
    ]
