from flask import Blueprint, jsonify,render_template, request
from .database import get_db_connection
import mysql.connector

routes_bp = Blueprint('routes_bp', __name__)


@routes_bp.route('/')
def index():
    try:
        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        connection.close()
        return render_template('index.html', users=users)
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500


@routes_bp.route('/users', methods=['GET'])
def view_all_users():
    try:
        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users")
        users = cur.fetchall()
        cur.close()
        connection.close()
        return jsonify(users)  
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500
    

@routes_bp.route('/users/<int:id>', methods=['GET'])
def view_user(id):
    try:
        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)
        cur.execute("SELECT * FROM users where id=%s",(id,))
        users = cur.fetchone()
        cur.close()
        connection.close()
        return jsonify(users)  
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
        image = data.get('image')

        if not nombre or not correo:
            return jsonify({"error": "Faltan datos (nombre y correo son obligatorios)"}), 400

        connection = get_db_connection()
        cur = connection.cursor()

        # Verificar si el correo ya está registrado
        cur.execute("SELECT * FROM users WHERE correo = %s", (correo,))
        existing_user = cur.fetchone()
        if existing_user:
            return jsonify({"error": "El correo electrónico ya está registrado"}), 400

        cur.execute("""
        INSERT INTO users (nombre, apellido, correo, celular, image)
        VALUES (%s, %s, %s, %s, %s)
        """, (nombre, apellido, correo, celular, image))

        connection.commit()
        cur.close()
        connection.close()
        return jsonify({"message": "Usuario agregado exitosamente"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500
    

@routes_bp.route('/delete/<int:id>', methods=['DELETE'])
def delete_user(id):
    try:
        connection = get_db_connection()
        cur = connection.cursor()

        # Verificar si el usuario existe antes de eliminar
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        cur.execute("DELETE FROM users WHERE id = %s", (id,))
        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500
    

@routes_bp.route('/update/<int:id>', methods=['PUT'])
def update_user(id):
    try:
        data = request.json
        nombre = data.get('nombre')
        apellido = data.get('apellido')
        celular = data.get('celular')
        image = data.get('image', None)

        if not nombre or not apellido or not celular:
            return jsonify({"error": "Faltan datos (nombre, apellido y celular son obligatorios)"}), 400

        connection = get_db_connection()
        cur = connection.cursor()

        # Verificar si el usuario existe
        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        cur.execute("""
        UPDATE users 
        SET nombre = %s, apellido = %s, celular = %s, image = %s 
        WHERE id = %s
        """, (nombre, apellido, celular, image, id))

        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"message": "Usuario actualizado exitosamente"}), 200
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al actualizar el usuario: {str(e)}"}), 500
