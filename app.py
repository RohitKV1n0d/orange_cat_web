from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from functools import wraps
import os
import json
import requests
import datetime

app = Flask(__name__)
CORS(app)

ENV = os.environ.get('ENV', 'prod')
LIVE_DB = os.environ.get('LIVE_DB', 'True')

# Add a secret key for the Flask-Login
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

# Load the user from the database for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Your existing models and database setup...

# Database initialization function
def init_db():
    db.create_all()
    admin_username = 'admin'
    admin_password = 'admin'

    # Check if the default admin user exists
    admin_user = Users.query.filter_by(username=admin_username).first()
    if not admin_user:
        # Create the default admin user
        admin_user = Users(username=admin_username, password=admin_password, role='admin')
        db.session.add(admin_user)
        db.session.commit()

if ENV == 'dev' :
    HOST_URL = os.environ.get('HOST_URL', 'http://localhost:5000/')
    app.debug = True
    if LIVE_DB == 'True':
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        SECRET_KEY = os.environ.get('SECRET_KEY')

        if SQLALCHEMY_DATABASE_URI.startswith("postgres://"): 
            SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

        app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        app.config['SECRET_KEY'] = SECRET_KEY
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
        app.config['SECRET_KEY'] = 'asdasdasdasdasdasdasdaveqvq34c'
        CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')



else:
    HOST_URL = os.environ.get('HOST_URL', '')
    app.debug = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')

    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"): 
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS


db = SQLAlchemy(app)

class Users(UserMixin,db.Model):
    table_name = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.Text, nullable=True)
    password = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<User %r>' % self.id
    
    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role
        }
    
    def serialize2(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "created_at": self.created_at
        }





class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Product %r>' % self.id
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price
        }
    
    def serialize2(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "created_at": self.created_at
        }





def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need to be an admin to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.context_processor
def inject_user():
    if current_user.is_authenticated:
        return dict(current_user=current_user)
    return dict(current_user=None)


@app.route('/admin')
@admin_required
def admin_panel():
    # Your admin panel code here
    return render_template('admin/index.html')

    
@app.route('/')
def index():
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists and the password is correct
        user = Users.query.filter_by(username=username).first()
        if user and user.password == password:
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('admin/login.html')



@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'success')
    return redirect(url_for('index'))


@app.route('/base')
def base():
    return render_template('base.html')


# about
@app.route('/about')
def about():
    return render_template('about-orangecat.html')

@app.route('/products')
def view_products():
    products = Products.query.all()
    return render_template('bikes.html', products=products)

@app.route('/products/<int:id>')
def view_product(id):
    product = Products.query.get_or_404(id)
    return render_template('product.html', product=product)

@app.route('/api/products', methods=['GET'])
def get_products():
    products = Products.query.all()
    products = list(map(lambda product: product.serialize(), products))
    return jsonify(products), 200

# photo gallery
@app.route('/gallery/photo')
def photo_gallery():
    return render_template('photo-gallery.html')


@app.route('/fetch/gallery/')
def fetch_gallery_photos():
    photos = os.listdir('static/images/gallery')
    photos = list(map(lambda photo: 'static/images/gallery/' + photo, photos))
    return jsonify(photos), 200

# video gallery
@app.route('/gallery/video')
def video_gallery():
    return render_template('video-gallery.html')

@app.route('/fetch/video/')
def fetch_video():
    videos = os.listdir('static/videos')
    videos = list(map(lambda video: 'static/videos/' + video, videos))
    return jsonify(videos), 200

# contact us
@app.route('/contacts')
def contacts():
    return render_template('contacts.html')

@app.route('/example')
def example():
    return render_template('example.html')
 

with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run()


    