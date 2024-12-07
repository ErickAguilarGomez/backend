import os
from flask import Blueprint, jsonify,render_template, request
from .database import get_db_connection
import mysql.connector
import base64

routes_bp = Blueprint('routes_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

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

        upload_folder = os.path.join(os.getcwd(), 'uploads')
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)

        if image:
            try:
                image_data = base64.b64decode(image.split(',')[1])
                image_path = os.path.join(upload_folder, image_name)
                with open(image_path, 'wb') as f:
                    f.write(image_data)
                image = image_path
            except Exception as e:
                return jsonify({"error": "Formato de imagen base64 inválido"}), 400

        cur.execute("""INSERT INTO users (nombre, apellido, correo, celular, image) 
                    VALUES (%s, %s, %s, %s, %s)""", (nombre, apellido, correo, celular, image))
        connection.commit()
        cur.close()
        connection.close()
        return jsonify({"message": "Usuario agregado exitosamente"}), 201
    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500

###################################################33333
###################################################33333
###################################################33333
###################################################33333
###################################################33333

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

        if not nombre or not correo:
            return jsonify({"error": "Faltan datos (nombre y correo son obligatorios)"}), 400

        connection = get_db_connection()
        cur = connection.cursor(dictionary=True)

        cur.execute("SELECT * FROM users WHERE id = %s", (id,))
        user = cur.fetchone()

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        if image:
            try:
                if user['image']:
                    try:
                        os.remove(user['image'])
                    except OSError:
                        pass

                image_data = base64.b64decode(image.split(',')[1])
                
                if not image_name:
                    image_name = f"profile_image_{id}.jpg"

                image_path = os.path.join(os.getcwd(), 'uploads', image_name)

                with open(image_path, 'wb') as f:
                    f.write(image_data)
                image = image_path
            except Exception as e:
                return jsonify({"error":f"{e}"}), 400
        else:
            image = user['image']

        cur.execute("""
            UPDATE users
            SET nombre = %s, apellido = %s, correo = %s, celular = %s, image = %s
            WHERE id = %s
        """, (nombre, apellido, correo, celular, image, id))

        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"message": "Usuario actualizado exitosamente"}), 200

    except mysql.connector.Error as e:
        return jsonify({"error": f"Error al conectar con la base de datos: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500
###################################################33333
###################################################33333
###################################################33333
###################################################33333


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
        else:
            pass 

        cur.execute("DELETE FROM users WHERE id = %s", (id,))
        connection.commit()
        cur.close()
        connection.close()

        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": f"Error inesperado: {str(e)}"}), 500


