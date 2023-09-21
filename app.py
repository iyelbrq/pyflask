from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
import requests
from datetime import datetime as dt

app = Flask(__name__)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pyflask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
mysql = MySQL(app)

@app.route('/user/fetch', methods=['GET'])
def fetch_user():
    try:
        source_url = f'https://reqres.in/api/users?per_page=12'
            
        response = requests.get(source_url)
        if response.status_code == 200:
            data = response.json()
            users = data.get('data', [])
            fetch_user_data(users)

            return jsonify(users)
        else:
            return jsonify(message='Error: Failed to fetch user data'), 500
            
    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500
    
@app.route('/user/<int:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        user = cursor.fetchone()
        cursor.close()
        if user:
            return jsonify(user)
        else:
            return jsonify(message=f'User id {user_id} not found'), 404

    except Exception as e:
        return jsonify(message=f'Error: {str(e)}'), 500
    
@app.route('/user', methods=['GET'])
def get_all_users():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("Select * from users")
        users = cursor.fetchall()
        cursor.close()
        return jsonify(users)
    except Exception as e:
        return jsonify(message=f'Error get all user data: {str(e)}'), 500
    
@app.route('/user', methods=['POST'])
def add_user():
    try:
        data = request.json
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO users (email, first_name, last_name, avatar) VALUES (%s, %s, %s, %s)",
                       (data['email'], data['first_name'], data['last_name'], data['avatar']))
        mysql.connection.commit()
        cursor.close()

        return jsonify(message='User added successfully'), 201

    except Exception as e:
        return jsonify(message=f'Error added data: {str(e)}'), 500

@app.route('/user', methods=['PUT'])
def update_user():
    try:
        data = request.json
        cursor = mysql.connection.cursor()

        # Construct the SQL query dynamically based on the provided data
        query = "UPDATE users SET "
        params = []

        if 'email' in data:
            query += "email = %s, "
            params.append(data['email'])

        if 'first_name' in data:
            query += "first_name = %s, "
            params.append(data['first_name'])

        if 'last_name' in data:
            query += "last_name = %s, "
            params.append(data['last_name'])

        if 'avatar' in data:
            query += "avatar = %s, "
            params.append(data['avatar'])

        # Remove the trailing comma and add the WHERE clause
        query = query.rstrip(', ') + " WHERE id = %s"
        params.append(data['id'])

        # Execute the SQL query with parameters
        cursor.execute(query, params)
        mysql.connection.commit()
        cursor.close()
        return jsonify(message='User updated successfully')

    except Exception as e:
        return jsonify(message=f'Error updated data: {str(e)}'), 500


@app.route('/user', methods=['DELETE'])
def delete_user():
    try:
        if not delete_uthorization():
            return jsonify(message='Unauthorized'), 401

        user_id = request.json['id']
        cursor = mysql.connection.cursor()
        cursor.execute(f"UPDATE users SET deleted_at = '{dt.now()}' WHERE id = {user_id};")
        mysql.connection.commit()
        cursor.close()

        return jsonify(message='User deleted successfully')

    except Exception as e:
        return jsonify(message=f'Error deleted data : {str(e)}'), 500
    
def delete_uthorization():
    auth_header = request.headers.get('Authorization')
    if auth_header != "3cdcnTiBsl":
        return False
    return True
    
def fetch_user_data(users):
    try:
        cursor = mysql.connection.cursor()
        for user in users:
            user_id = user['id']

            cursor.execute(f"SELECT id FROM users WHERE id={user_id}")
            existing_user = cursor.fetchone()

            if not existing_user:
                cursor.execute(
                    "INSERT INTO users (id, email, first_name, last_name, avatar) VALUES (%s, %s, %s, %s, %s)",
                    (user['id'], user['email'], user['first_name'], user['last_name'], user['avatar'])
                )
                mysql.connection.commit()

        cursor.close()
    except Exception as e:
        print(f"Error storing user data: {str(e)}")

if __name__ == '__main__':
    app.run(debug=True)
