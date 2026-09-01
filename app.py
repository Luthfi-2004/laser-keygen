from flask import Flask, request, jsonify, send_file
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import binascii
import io

app = Flask(__name__)

# Konstanta
PRODUCT_NAME = "LASER MARKING SYSTEM"
IV_STRING = "%1Az=-@qT"

def encrypt_serial(mb, expiry_date):
    plaintext = f"{PRODUCT_NAME}|{expiry_date}"
    key = mb.encode('ascii').ljust(16, b'\x00')
    iv = IV_STRING.encode('ascii').ljust(16, b'\x00')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = cipher.encrypt(pad(plaintext.encode('ascii'), AES.block_size))
    return ciphertext

def decrypt_passkey(passkey_hex):
    # Dekripsi PASSKEY dengan key "P45W0RD"
    key = "P45W0RD".encode('ascii').ljust(16, b'\x00')
    iv = IV_STRING.encode('ascii').ljust(16, b'\x00')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    ciphertext = bytes.fromhex(passkey_hex)
    plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return plaintext.decode('ascii')

@app.route('/')
def index():
    return '''
    <h2>Laser Keygen API</h2>
    <p>Gunakan endpoint /generate dengan metode POST.</p>
    <p>Contoh: <code>{"mb": "LR0BNTXS", "date": "2099/12/31"}</code></p>
    <p>Atau <code>{"passkey": "3FADFC..."}</code> untuk auto-detect MB.</p>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'JSON required'}), 400

    # Ambil MB dari PASSKEY jika diberikan
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

    # Enkripsi serial
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

@app.route('/download', methods=['POST'])
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

if __name__ == '__main__':
    app.run(debug=True, port=5000)
    