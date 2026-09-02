from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
import os
import traceback
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

@app.errorhandler(Exception)
def handle_exception(e):
    if isinstance(e, HTTPException):
        return jsonify(error=e.description), e.code
    return jsonify(error=str(e)), 500

PRODUCT_NAME = "LASER MARKING SYSTEM"
IV_STRING = "%1Az=-@qT"

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def encrypt_serial(mb, expiry_date):
    plaintext = f"{PRODUCT_NAME}|{expiry_date}"
    key = mb.encode('ascii').ljust(16, b'\x00')
    iv = IV_STRING.encode('ascii').ljust(16, b'\x00')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode('ascii'), AES.block_size))
    return ciphertext



@app.route('/', defaults={'path': ''}, methods=['GET', 'POST'])
@app.route('/<path:path>', methods=['GET', 'POST'])
def catch_all(path):
    if request.method == 'OPTIONS':
        return '', 200
        
    if path == 'api/generate':
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'error': 'Payload tidak valid atau bukan JSON'}), 400
        mb = data.get('mb')
        expiry_date = data.get('date', '2099/12/31')

        if not mb:
            return jsonify({'error': 'Motherboard Serial harus diisi'}), 400

        try:
            # 1. Generate Key
            ciphertext = encrypt_serial(mb, expiry_date)
            hex_result = binascii.hexlify(ciphertext).decode().upper()
            
            # 2. Save to Database ATOMICALLY
            if supabase:
                try:
                    supabase.table('activations').insert({
                        'mb': mb,
                        'passkey': hex_result,
                        'expiry_date': expiry_date
                    }).execute()
                except Exception as db_err:
                    print(f"Supabase error: {db_err}")
                    return jsonify({'error': f'Sistem gagal mencatat ke database. Harap periksa koneksi. ({str(db_err)})'}), 500
            else:
                return jsonify({'error': 'Sistem Database (Supabase) belum dikonfigurasi. Penarikan kunci dibatalkan.'}), 500

            # 3. Return Success
            return jsonify({
                'mb': mb,
                'date': expiry_date,
                'passkey_hex': hex_result,
                'message': 'Success'
            })
        except Exception as e:
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500

    elif path == 'api/history':
        if not supabase:
            return jsonify({'error': 'Supabase not configured'}), 500
            
        try:
            response = supabase.table('activations').select('*').order('created_at', desc=True).limit(50).execute()
            return jsonify({'data': response.data})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    elif path == 'api/dashboard':
        if not supabase:
            return jsonify({'error': 'Supabase not configured'}), 500
            
        try:
            # Get latest 3 activities
            recent = supabase.table('activations').select('*').order('created_at', desc=True).limit(3).execute()
            # Fetch count using select('*') to avoid assuming 'id' column exists
            count_res = supabase.table('activations').select('*', count='exact').limit(1).execute()
            total_count = count_res.count if hasattr(count_res, 'count') and count_res.count is not None else 0
            
            return jsonify({
                'total': total_count,
                'recent': recent.data,
                'status': 'Online'
            })
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Database error: {str(e)}'}), 500

    return jsonify({'error': 'Endpoint Not Found', 'path': path}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
