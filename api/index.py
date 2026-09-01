from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
import io
import os
from supabase import create_client, Client

app = Flask(__name__)
CORS(app)

PRODUCT_NAME = "LASER MARKING SYSTEM"
IV_STRING = "%1Az=-@qT"

# Supabase (dari environment variables Vercel)
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

def decrypt_passkey(passkey_hex):
    key = "P45W0RD".encode('ascii').ljust(16, b'\x00')
    iv = IV_STRING.encode('ascii').ljust(16, b'\x00')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = bytes.fromhex(passkey_hex)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode('ascii')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON required'}), 400
    mb = data.get('mb')
    passkey = data.get('passkey')
    expiry_date = data.get('date', '2099/12/31')

    if passkey:
        try:
            plaintext = decrypt_passkey(passkey)
            if '|' not in plaintext:
                raise ValueError('Invalid PASSKEY format')
            mb = plaintext.split('|')[0]
        except Exception as e:
            return jsonify({'error': f'Gagal mendekripsi PASSKEY: {str(e)}'}), 400

    if not mb:
        return jsonify({'error': 'MB atau PASSKEY harus diisi'}), 400

    try:
        ciphertext = encrypt_serial(mb, expiry_date)
        hex_result = binascii.hexlify(ciphertext).decode().upper()
        return jsonify({
            'mb': mb,
            'date': expiry_date,
            'passkey_hex': hex_result,
            'message': 'Success'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download', methods=['POST'])
def download():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON required'}), 400
    mb = data.get('mb')
    passkey = data.get('passkey')
    expiry_date = data.get('date', '2099/12/31')

    if passkey:
        try:
            plaintext = decrypt_passkey(passkey)
            if '|' not in plaintext:
                raise ValueError('Invalid PASSKEY format')
            mb = plaintext.split('|')[0]
        except Exception as e:
            return jsonify({'error': f'Gagal mendekripsi PASSKEY: {str(e)}'}), 400

    if not mb:
        return jsonify({'error': 'MB atau PASSKEY harus diisi'}), 400

    ciphertext = encrypt_serial(mb, expiry_date)
    return send_file(
        io.BytesIO(ciphertext),
        mimetype='application/octet-stream',
        as_attachment=True,
        download_name='serial.dat'
    )

@app.route('/api/save', methods=['POST'])
def save():
    if not supabase:
        return jsonify({'error': 'Supabase not configured'}), 500
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON required'}), 400

    mb = data.get('mb')
    passkey_hex = data.get('passkey_hex')
    expiry_date = data.get('date')

    if not mb or not passkey_hex or not expiry_date:
        return jsonify({'error': 'Missing fields'}), 400

    try:
        result = supabase.table('activations').insert({
            'mb': mb,
            'passkey': passkey_hex,
            'expiry_date': expiry_date
        }).execute()
        return jsonify({'message': 'Saved successfully', 'data': result.data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Vercel akan memanggil objek `app` ini sebagai WSGI handler
if __name__ == '__main__':
    app.run(debug=True, port=5000)