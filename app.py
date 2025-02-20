from flask import Flask, jsonify, request
from datetime import datetime, timedelta
import random
import string

app = Flask(__name__)

generated_keys = {}

def generate_random_string(length=30):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for _ in range(length))

def parse_expired_time(expired_str):
    now = datetime.now()
    if expired_str.endswith("d"):
        return now + timedelta(days=int(expired_str[:-1]))
    elif expired_str.endswith("w"):
        return now + timedelta(weeks=int(expired_str[:-1]))
    elif expired_str.endswith("m"):
        return now + timedelta(days=int(expired_str[:-1]) * 30)
    elif expired_str.endswith("y"):
        return now + timedelta(days=int(expired_str[:-1]) * 365)
    return now + timedelta(days=1)  # Default 1 hari jika tidak ada parameter expired yang valid

def calculate_expired_in_hours(expired_time):
    time_left = expired_time - datetime.now()
    return round(time_left.total_seconds() / 3600, 2)  # Ubah ke jam

@app.route('/generate', methods=['GET'])
def generate_key():
    expired_str = request.args.get('expired', '1d')
    expired_time = parse_expired_time(expired_str)

    service = request.args.get('service', 'StarX')  # Default jika service tidak diisi adalah 'StarX'
    service = ''.join(e for e in service if e.isalnum())  # Menghapus karakter khusus untuk keamanan

    random_part = generate_random_string()
    key = f"{service}_{random_part}"  # Format key dengan service yang diinputkan

    generated_keys[key] = expired_time

    return jsonify({
        "key": key,
        "service": service,
        "expired_in": f"{calculate_expired_in_hours(expired_time)} hours"
    })

@app.route('/check', methods=['GET'])
def check_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"status": "error", "message": "No Provided keys, Pls input key"}), 400

    if key in generated_keys:
        expired_time = generated_keys[key]
        expired_in = calculate_expired_in_hours(expired_time)
        if expired_in > 0:
            return jsonify({"status": "valid", "expired_in": f"{expired_in} hours"})
        else:
            return jsonify({"status": "invalid", "message": "Key has expired."}), 404
    else:
        return jsonify({"status": "error", "message": "Key not found."}), 404

@app.route('/data', methods=['GET'])
def get_data():
    keys_data = {key: f"{calculate_expired_in_hours(expired_time)} hours"
                 for key, expired_time in generated_keys.items()}
    return jsonify({"keys": keys_data})

if __name__ == '__main__':
    app.run(debug=True)
