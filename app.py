from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy
import secrets
import qrcode
from io import BytesIO
import base64
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mi_clave_secreta_muy_larga_y_compleja_1234567890!@#$%^&*()'

# Configuración de Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mano.tech111@gmail.com'
app.config['MAIL_PASSWORD'] = 'qnyz smqn iblz dcam'
app.config['MAIL_DEFAULT_SENDER'] = 'mano.tech111@gmail.com'

mail = Mail(app)

# Configuración de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/supermercado_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelos de la base de datos
class Categoria(db.Model):
    __tablename__ = 'categorias'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    productos = db.relationship('Producto', backref='categoria', lazy=True)

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    imagen = db.Column(db.String(255))
    categoria_id = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    id = db.Column(db.Integer, primary_key=True)
    codigo_pedido = db.Column(db.String(20), unique=True, nullable=False)
    cliente_nombre = db.Column(db.String(100), nullable=False)
    cliente_email = db.Column(db.String(100), nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    detalles = db.relationship('DetallePedido', backref='pedido', lazy=True)

class DetallePedido(db.Model):
    __tablename__ = 'detalle_pedido'
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

# Rutas de la aplicación
@app.route('/')
def index():
    categorias = Categoria.query.all()
    return render_template('index.html', categorias=categorias)

@app.route('/nosotros')
def nosotros():
    #aqui debes de enviar los datos de tu equipo en un arreglo llamado ,miembros que debe de llevar  nombre, telefono, email
    miembro = [
        {
            'nombre': 'Gerson Ruiz',
            'telefono': '+503 1234-5678',
            'email': 'gerson@supermercado.com.sv'
        },
        {
            'nombre': 'Oscar Ceron',
            'telefono': '+503 2345-6789',
            'email': 'oscar@supermercado.com.sv'
        },
        {
            'nombre': 'Jenniffer Catota',
            'telefono': '+503 3456-7890',
            'email': 'jenniffer@supermercado.com.sv'
        },
        {
            'nombre': 'Daniel Umaña',
            'telefono': '+503 4567-8901',
            'email': 'daniel@supermercado.com.sv'
        }
    ]
    return render_template('nosotros.html', miembro=miembro)

@app.route('/contacto')
def contacto():
    return render_template('contacto.html')

@app.route('/productos/<int:categoria_id>')
def productos(categoria_id):
    categoria = Categoria.query.get_or_404(categoria_id)
    productos = Producto.query.filter_by(categoria_id=categoria_id).all()
    return render_template('productos.html', categoria=categoria, productos=productos)

@app.route('/agregar_al_carrito/<int:producto_id>', methods=['POST'])
def agregar_al_carrito(producto_id):
    producto = Producto.query.get_or_404(producto_id)
    cantidad = int(request.form.get('cantidad', 1))
    
    # Validar stock disponible
    if cantidad > producto.stock:
        flash(f'No hay suficiente stock de {producto.nombre}. Stock disponible: {producto.stock}', 'danger')
        return redirect(request.referrer)
    
    if 'carrito' not in session:
        session['carrito'] = []
    
    # Verificar si el producto ya está en el carrito
    encontrado = False
    for item in session['carrito']:
        if item['producto_id'] == producto_id:
            # Validar que no exceda el stock al sumar
            if (item['cantidad'] + cantidad) > producto.stock:
                flash(f'No hay suficiente stock de {producto.nombre}. Stock disponible: {producto.stock}', 'danger')
                return redirect(request.referrer)
                
            item['cantidad'] += cantidad
            encontrado = True
            break
    
    if not encontrado:
        session['carrito'].append({
            'producto_id': producto_id,
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': cantidad,
            'imagen': producto.imagen
        })
    
    session.modified = True
    flash(f'{producto.nombre} agregado al carrito', 'success')
    return redirect(request.referrer)

@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', [])
    total = sum(item['precio'] * item['cantidad'] for item in carrito)
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/eliminar_del_carrito/<int:index>')
def eliminar_del_carrito(index):
    if 'carrito' in session and 0 <= index < len(session['carrito']):
        producto = session['carrito'][index]['nombre']
        del session['carrito'][index]
        session.modified = True
        flash(f'{producto} eliminado del carrito', 'warning')
    return redirect(url_for('ver_carrito'))

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'carrito' not in session or not session['carrito']:
        flash('Tu carrito está vacío', 'warning')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        nombre = request.form['nombre']
        email = request.form['email']
        
        if not nombre or not email:
            flash('Por favor ingresa tu nombre y correo electrónico', 'danger')
            return redirect(url_for('checkout'))
        
        # Verificar stock antes de procesar el pedido
        for item in session['carrito']:
            producto = Producto.query.get(item['producto_id'])
            if producto.stock < item['cantidad']:
                flash(f'No hay suficiente stock de {producto.nombre}. Stock disponible: {producto.stock}', 'danger')
                return redirect(url_for('ver_carrito'))
        
        # Generar código único para el pedido
        codigo_pedido = secrets.token_hex(8).upper()
        total = sum(item['precio'] * item['cantidad'] for item in session['carrito'])
        
        # Crear el pedido en la base de datos
        nuevo_pedido = Pedido(
            codigo_pedido=codigo_pedido,
            cliente_nombre=nombre,
            cliente_email=email,
            total=total
        )
        
        db.session.add(nuevo_pedido)
        db.session.commit()
        
        # Agregar los detalles del pedido y actualizar stock
        for item in session['carrito']:
            producto = Producto.query.get(item['producto_id'])
            
            # Descontar del stock
            producto.stock -= item['cantidad']
            
            # Agregar detalle del pedido
            detalle = DetallePedido(
                pedido_id=nuevo_pedido.id,
                producto_id=item['producto_id'],
                cantidad=item['cantidad'],
                precio_unitario=item['precio']
            )
            db.session.add(detalle)
        
        db.session.commit()
        
        # Generar QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(codigo_pedido)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir QR a base64 para mostrarlo en el HTML
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_img = base64.b64encode(buffered.getvalue()).decode()
        
        # Enviar correo electrónico
        enviar_correo(nuevo_pedido, session['carrito'], qr_img)
        
        # Limpiar el carrito
        session.pop('carrito', None)
        
        return render_template('confirmacion.html', pedido=nuevo_pedido, qr_img=qr_img)
    
    total = sum(item['precio'] * item['cantidad'] for item in session['carrito'])
    return render_template('checkout.html', total=total)

def enviar_correo(pedido, carrito, qr_img):
    try:
        # Crear el cuerpo del correo
        cuerpo_html = render_template('email_pedido.html', pedido=pedido, carrito=carrito, qr_img=qr_img)
        
        msg = Message(
            subject=f'Confirmación de tu pedido #{pedido.codigo_pedido}',
            recipients=[pedido.cliente_email],
            html=cuerpo_html
        )

        # Adjuntar el QR como imagen en el cuerpo del correo para src="data:image/png;base64,{{ qr_img }}"
        msg.html = cuerpo_html
        msg.attach('qr_code.png', 'image/png', base64.b64decode(qr_img))
        # Enviar el correo
        
        mail.send(msg)
        return True
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
