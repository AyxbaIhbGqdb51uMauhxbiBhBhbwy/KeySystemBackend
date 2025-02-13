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
    return now + timedelta(days=1)

def calculate_expired_in(expired_time):
    time_left = expired_time - datetime.now()
    return round(time_left.total_seconds(), 2)

@app.route('/generate', methods=['GET'])
def generate_key():
    expired_str = request.args.get('expired', '1d')
    expired_time = parse_expired_time(expired_str)

    random_part = generate_random_string()
    key = f"StarX_{random_part}"
    generated_keys[key] = expired_time

    return jsonify({
        "key": key,
        "expired_in": f"{calculate_expired_in(expired_time)} seconds"
    })

@app.route('/check', methods=['GET'])
def check_key():
    key = request.args.get('key')
    if not key:
        return jsonify({"status": "error", "message": "No Provided keys, Pls input key"}), 400

    if key in generated_keys:
        expired_time = generated_keys[key]
        expired_in = calculate_expired_in(expired_time)
        if expired_in > 0:
            return jsonify({"status": "key is valid", "expired_in": f"{expired_in} seconds"})
        else:
            return jsonify({"status": "key is invalid", "message": "Key has expired."}), 404
    else:
        return jsonify({"status": "key is invalid", "message": "Key not found."}), 404

@app.route('/data', methods=['GET'])
def get_data():
    keys_data = {key: f"{calculate_expired_in(expired_time)} seconds"
                 for key, expired_time in generated_keys.items()}
    return jsonify({"keys": keys_data})

if __name__ == '__main__':
    app.run(debug=True)
