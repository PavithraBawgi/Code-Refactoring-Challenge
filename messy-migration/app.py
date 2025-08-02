from flask import Flask, request, jsonify
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

conn = sqlite3.connect('users.db', check_same_thread=False)
cursor = conn.cursor()

@app.route('/')
def home():
    return "User Management System"


@app.route('/users', methods=['GET'])
def get_all_users():
    try:
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        
        # Converting all tuples to list of dicts
        user_list = []
        for user in users:
            user_dict = {
                "id": user[0],
                "name": user[1],
                "email": user[2]
                # Not  including password for security reasons.
            }
            user_list.append(user_dict)

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if user:
            user_dict = {
                "id": user[0],
                "name": user[1],
                "email": user[2]
            }
            return jsonify(user_dict), 200
        else:
            return jsonify({"error": "User not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if not all([name, email, password]):
            return jsonify({'error': 'Missing required fields'}), 400

        hashed_password = generate_password_hash(password)

        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed_password)
        )
        conn.commit()

        return jsonify({'message': 'User created successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/user/<user_id>', methods=['PUT'])
def update_user(user_id):
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')

        if not name or not email:
            return jsonify({"error": "Name and email are required"}), 400

        cursor.execute(
            "UPDATE users SET name = ?, email = ? WHERE id = ?",
            (name, email, user_id)
        )
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": "User updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/user/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": "User not found"}), 404

        return jsonify({"message": f"User {user_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/search', methods=['GET'])
def search_users():
    try:
        name = request.args.get('name')
        if not name:
            return jsonify({"error": "Please provide a name to search"}), 400

        cursor.execute("SELECT * FROM users WHERE name LIKE ?", (f"%{name}%",))
        users = cursor.fetchall()

        if not users:
            return jsonify({"message": "No users found"}), 404

        user_list = [{"id": user[0], "name": user[1], "email": user[2]} for user in users]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not all([email, password]):
            return jsonify({'error': 'Missing credentials'}), 400

        cursor.execute("SELECT id, password FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()

        if user and check_password_hash(user[1], password):
            return jsonify({'status': 'success', 'user_id': user[0]})
        else:
            return jsonify({'status': 'failed', 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5009, debug=True)