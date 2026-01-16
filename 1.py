from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import qrcode
from io import BytesIO

app = Flask(__name__)

# ======================
# DATABASE
# ======================
def get_db():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tanaman (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT,
            jenis TEXT,
            lat REAL,
            lng REAL
        )
    """)
    conn.commit()
    conn.close()

# ======================
# ROUTES
# ======================
@app.route('/')
def index():
    conn = get_db()
    data = conn.execute("SELECT * FROM tanaman").fetchall()
    conn.close()
    return render_template('index.html', data=data)

@app.route('/tambah', methods=['GET', 'POST'])
def tambah():
    if request.method == 'POST':
        nama = request.form['nama']
        jenis = request.form['jenis']
        lat = request.form['lat']
        lng = request.form['lng']

        conn = get_db()
        conn.execute(
            "INSERT INTO tanaman (nama, jenis, lat, lng) VALUES (?, ?, ?, ?)",
            (nama, jenis, lat, lng)
        )
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    return render_template('tambah.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    tanaman = conn.execute(
        "SELECT * FROM tanaman WHERE id=?", (id,)
    ).fetchone()

    if request.method == 'POST':
        nama = request.form['nama']
        jenis = request.form['jenis']
        lat = request.form['lat']
        lng = request.form['lng']

        conn.execute("""
            UPDATE tanaman SET nama=?, jenis=?, lat=?, lng=?
            WHERE id=?
        """, (nama, jenis, lat, lng, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', tanaman=tanaman)

@app.route('/hapus/<int:id>')
def hapus(id):
    conn = get_db()
    conn.execute("DELETE FROM tanaman WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

# ======================
# QR CODE
# ======================
@app.route('/qr')
def qr():
    url = request.host_url
    qr = qrcode.make(url)
    img = BytesIO()
    qr.save(img)
    img.seek(0)
    return send_file(img, mimetype='image/png')

# ======================
# MAIN
# ======================
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
