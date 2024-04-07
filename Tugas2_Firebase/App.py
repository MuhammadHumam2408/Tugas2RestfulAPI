# app.py
# Impor yang diperlukan
import os
from flask import Flask, request, jsonify
from firebase_admin import credentials, firestore, initialize_app
import uuid
from datetime import datetime

# Inisialisasi Aplikasi Flask
app = Flask(__name__)

# Inisialisasi Database Firestore
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
produk_ref = db.collection('produk')

# Endpoint untuk menambahkan data baru
@app.route('/add', methods=['POST'])
def create():
    try:
        # Generate UUID untuk dokumen baru
        id = str(uuid.uuid4())
        # Tetapkan UUID yang dihasilkan sebagai ID untuk dokumen
        request.json['id'] = id
        # Tambahkan dokumen ke koleksi Firestore
        produk_ref.document(id).set(request.json)
        return jsonify({"success": True, "id": id}), 200
    except Exception as e:
        return f"An Error Occured: {e}"

# Endpoint untuk membaca data
@app.route('/list', methods=['GET'])
def read():
    try:
        # Periksa apakah ID disertakan dalam query URL
        produk_id = request.args.get('id')
        if produk_id:
            # Ambil dokumen berdasarkan ID
            produk = produk_ref.document(produk_id).get()
            response = {
                "data": produk.to_dict(),
                "message": f"menampilkan data dengan ID {produk_id}",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(response), 200
        else:
            # Ambil semua dokumen
            all_produk = [doc.to_dict() for doc in produk_ref.stream()]
            response = {
                "data": all_produk,
                "message": "menampilkan semua produk",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            return jsonify(response), 200
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

# Endpoint untuk mengupdate data
@app.route('/update', methods=['POST', 'PUT'])
def update():
    try:
        id = request.json['id']
        produk_ref.document(id).update(request.json)
        response = {
            "message": f"Produk dengan ID {id} berhasil di update.",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 200
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

# Endpoint untuk menghapus data
@app.route('/delete', methods=['GET', 'DELETE'])
def delete():
    try:
        # Periksa apakah ID disertakan dalam query URL
        produk_id = request.args.get('id')
        if produk_id:
            # Hapus dokumen dengan ID yang disediakan dari Firestore
            produk_ref.document(produk_id).delete()
            response = {
                "message": f"produk dengan id {produk_id} berhasi dihapus",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 200
        else:
            response = {
                "message": "ID parameter is required",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 400
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

# Endpoint untuk mendapatkan data berdasarkan jenis
@app.route('/jenis', methods=['GET'])
def get_by_jenis():
    try:
        produk_jenis = request.args.get('jenis')
        if produk_jenis:
            # Query Firestore untuk dokumen dengan jenis yang cocok
            query = produk_ref.where('jenis', '==', produk_jenis).stream()
            produk = [doc.to_dict() for doc in query]
            if produk:
                response = {
                    "message": f"menampilkan produk dengan jenis {produk_jenis}",
                    "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "data": produk
                }
                return jsonify(response), 200
            else:
                response = {
                    "message": f"produk berjenis {produk_jenis} tidak ditemukan",
                    "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                return jsonify(response), 404
        else:
            return jsonify({"error": "jenis parameter is required"}), 400
    except Exception as e:
        return f"An Error Occurred: {e}", 500
    
# Endpoint untuk mendapatkan data berdasarkan jenis dan harga
@app.route('/jenis-harga', methods=['GET'])
def get_by_jenis_and_price():
    try:
        produk_jenis = request.args.get('jenis')
        min_price = request.args.get('min_price')
        max_price = request.args.get('max_price')

        if not produk_jenis:
            return jsonify({"error": "jenis parameter is required"}), 400

        query = produk_ref.where('jenis', '==', produk_jenis)

        if min_price:
            query = query.where('harga', '>=', min_price)

        if max_price:
            query = query.where('harga', '<=', max_price)

        produk = [doc.to_dict() for doc in query.stream()]

        if produk:
            response = {
                "data": produk,
                "message": f"menampilkan produk dengan jenis {produk_jenis}",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 200
        else:
            response = {
                "message": f"produk dengan jenis {produk_jenis} dan harga di antara {min_price} dan {max_price} tidak ditemukan",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 404
    except Exception as e:
        return f"An Error Occurred: {e}", 500
    
# Endpoint untuk mendapatkan data berdasarkan nama produk
@app.route('/nama-produk', methods=['GET'])
def get_by_nama_produk():
    try:
        nama_produk = request.args.get('nama')
        
        if not nama_produk:
            return jsonify({"error": "nama parameter is required"}), 400

        # Query Firestore untuk dokumen dengan nama produk yang cocok
        query = produk_ref.where('nama', '==', nama_produk).stream()
        produk = [doc.to_dict() for doc in query]

        if produk:
            response = {
                "message": f"menampilkan produk dengan nama {nama_produk}",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": produk
            }
            return jsonify(response), 200
        else:
            response = {
                "message": f"produk dengan nama {nama_produk} tidak ditemukan",
                "data diambil pada": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            return jsonify(response), 404
    except Exception as e:
        return f"An Error Occurred: {e}", 500

# Endpoint untuk mengambil statistik produk
@app.route('/stats', methods=['GET'])
def get_product_stats():
    try:
        # Logika untuk mengambil statistik produk
        total_products = produk_ref.get()
        num_products = len(total_products)
        response = {
            "total_products": num_products,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 200
    except Exception as e:
        response = {
            "status": "error",
            "code": 500,
            "message": f"An Error Occurred: {e}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return jsonify(response), 500

# Mendapatkan port dari environment variable atau menggunakan port default 8080
port = int(os.environ.get('PORT', 8080))
if __name__ == '__main__':
    # Menjalankan aplikasi Flask
    app.run(threaded=True, host='0.0.0.0', port=port)