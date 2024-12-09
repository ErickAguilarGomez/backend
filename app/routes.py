import os
import base64
from flask import Blueprint, jsonify, render_template, request, url_for, send_from_directory
from .database import get_db_connection
import mysql.connector

routes_bp = Blueprint('routes_bp', __name__)

# Configuración de carpeta para subir imágenes
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

# Servir imágenes estáticamente
@routes_bp.route('/uploads/<path:filename>')
def serve_image(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@routes_bp.route('/')
def index():
    try:
        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        connection.close()
        for user in users:
            if user['image']:
                user['image'] = url_for('routes_bp.serve_image', filename=os.path.basename(user['image']), _external=True)
        return render_template('index.html', users=users)
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500



@routes_bp.route('/users/<int:id>', methods=['GET'])
def view_user(id):
    try:
        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()
        cur.close()
        connection.close()
        if user and user['image']:
            user['image'] = url_for('routes_bp.serve_image', filename=os.path.basename(user['image']), _external=True)
        return jsonify(user)
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500

@routes_bp.route('/register', methods=['POST'])
def post_user():
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        correo = data.get('correo')
        celular = data.get('celular')
        image = data.get('image', None)
        image_name = data.get('image_name', None)

        if not nombre or not correo:
            return jsonify({"error": "Faltan datos (nombre y correo son obligatorios)"}), 400

        connection = get_db_connection()
        cur = connection.cursor()

        cur.execute("SELECT * FROM users WHERE correo = %s", (correo,))
        existing_user = cur.fetchone()
        if existing_user:
            return jsonify({"error": "El correo electrónico ya está registrado"}), 400

        image_path = None
        if image:
            try:
                image_data = base64.b64decode(image.split(',')[1])
                image_path = os.path.join(UPLOAD_FOLDER, image_name)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
            except Exception as e:
                return jsonify({"error": "Formato de imagen base64 inválido"}), 400

        cur.execute("""INSERT INTO users (nombre, apellido, correo, celular, image) 
                       VALUES (%s, %s, %s, %s, %s)""", (nombre, apellido, correo, celular, image_path))
        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"message": "Usuario agregado exitosamente"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500

@routes_bp.route('/update/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        data = request.get_json()
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        correo = data.get('correo')
        celular = data.get('celular')
        image = data.get('image', None)
        image_name = data.get('image_name', None)

        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if image:
            if user['image'] and os.path.exists(user['image']):
                os.remove(user['image'])
            image_data = base64.b64decode(image.split(',')[1])
            image_path = os.path.join(UPLOAD_FOLDER, image_name or f"profile_image_{id}.jpg")
            with open(image_path, 'wb') as f:
                f.write(image_data)
        else:
            image_path = user['image']

        cur.execute("""UPDATE users SET nombre = %s, apellido = %s, correo = %s, celular = %s, image = %s WHERE id = %s""",
                    (nombre, apellido, correo, celular, image_path, id))
        connection.commit()
        cur.close()
        connection.close()  

        return jsonify({"message": "Usuario actualizado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

@routes_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if user['image'] and os.path.exists(user['image']):
            os.remove(user['image'])
        elif not user['image']:
            pass
        else: ###$$
            pass
        cur.execute("DELETE FROM users WHERE id = %s", (id,))
        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500

