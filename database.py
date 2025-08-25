from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors

app = Flask(__name__)

# Configuración básica de MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'       # Usuario común en MySQL Workbench
app.config['MYSQL_PASSWORD'] = 'root'       # Contraseña (vacía por defecto en desarrollo)
app.config['MYSQL_DB'] = 'supermercado_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'  # Para obtener resultados como diccionarios

mysql = MySQL(app)