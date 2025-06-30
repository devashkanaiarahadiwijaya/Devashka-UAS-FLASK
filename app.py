from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from dotenv import load_dotenv
import os
import pymysql

# Setup MySQL driver
pymysql.install_as_MySQLdb()

# Load environment variables
load_dotenv()


app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI', 'mysql://root:@localhost/crud_db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Database model
class Penjualan(db.Model):
    __tablename__ = 'penjualan'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nama_pembeli = db.Column(db.String(100), nullable=False)
    nama_barang = db.Column(db.String(255), nullable=False)
    tanggal_jual = db.Column(db.Date, nullable=True)
    jumlah_barang = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nama_pembeli": self.nama_pembeli,
            "nama_barang": self.nama_barang,
            "tanggal_jual": self.tanggal_jual.strftime("%Y-%m-%d") if self.tanggal_jual else None,
            "jumlah_barang": self.jumlah_barang
        }

# Create table
with app.app_context():
    db.create_all()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/penjualan', methods=['GET'])
def get_all():
    data = Penjualan.query.all()
    return jsonify([d.to_dict() for d in data])

@app.route('/penjualan/<int:id>', methods=['GET'])
def get_by_id(id):
    item = db.session.get(Penjualan, id)
    if not item:
        return jsonify({"message": "Data tidak ditemukan"}), 404
    return jsonify(item.to_dict())

@app.route('/penjualan', methods=['POST'])
def create():
    data = request.get_json()
    try:
        item = Penjualan(
            nama_pembeli=data['nama_pembeli'],
            nama_barang=data['nama_barang'],
            tanggal_jual=datetime.strptime(data['tanggal_jual'], "%Y-%m-%d"),
            jumlah_barang=data['jumlah_barang']
        )
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": "Data berhasil ditambahkan", "data": item.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/penjualan/<int:id>', methods=['PUT'])
def update(id):
    item = db.session.get(Penjualan, id)
    if not item:
        return jsonify({"message": "Data tidak ditemukan"}), 404
    try:
        data = request.get_json()
        item.nama_pembeli = data.get('nama_pembeli', item.nama_pembeli)
        item.nama_barang = data.get('nama_barang', item.nama_barang)
        item.tanggal_jual = datetime.strptime(data['tanggal_jual'], "%Y-%m-%d") if data.get('tanggal_jual') else item.tanggal_jual
        item.jumlah_barang = data.get('jumlah_barang', item.jumlah_barang)
        db.session.commit()
        return jsonify({"message": "Data berhasil diupdate", "data": item.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/penjualan/<int:id>', methods=['DELETE'])
def delete(id):
    item = db.session.get(Penjualan, id)
    if not item:
        return jsonify({"message": "Data tidak ditemukan"}), 404
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Data berhasil dihapus"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)