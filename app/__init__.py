from flask import Flask
from .routes import routes_bp
def create_app():
    app = Flask(__name__)
    app.config['MYSQL_HOST'] = 'localhost'      
    app.config['MYSQL_USER'] = 'root'            
    app.config['MYSQL_PASSWORD'] = 'mi_contraseña'  
    app.config['MYSQL_DATABASE'] = 'clientes'
    
    app.register_blueprint(routes_bp)
    
    return app
