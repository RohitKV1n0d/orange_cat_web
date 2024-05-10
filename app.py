from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
import json
import requests
import datetime
import boto3
import stripe
import uuid

import time
import io

# from flask_mail import Mail, Message

from utils.AWS_Modules import upload_file_to_s3, delete_file_from_s3, delete_all_files_from_s3
from GoogleCloudAPIs.googleAPIs import append_data_spreadsheet
# from utils.EmailUtils import EmailUtils

from make_celery import make_celery

from flask_mail import Mail, Message

app = Flask(__name__)
CORS(app)

celery = make_celery(app)
celery.set_default()
from celery import shared_task, current_task
from celery.contrib.abortable import AbortableTask
from celery.result import AsyncResult
import traceback

from flask import current_app
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', 'info@orangecatcycles.com')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')


UPLOAD_FOLDER = 'static/img/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ENV = os.environ.get('ENV', 'prod')
LIVE_DB = os.environ.get('LIVE_DB', 'True')
STRIPE_MODE = ''
TEST_USER_ROLES = os.environ.get('TEST_USER_ROLES', 'admin,super_admin,test').split(',')

# Add a secret key for the Flask-Login
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key')

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'user_login'

@celery.task(name='app.send_email_task')
def send_email_task(subject, body, recipients):
    try:
        print("Sending mail")
        sender = os.environ.get('MAIL_USERNAME', 'info@orangecatcycles.com')
        msg = Message(subject,
                        sender=sender,
                        recipients=recipients)
        msg.html = body
        mail = Mail(app)
        mail.send(msg)
        return True
    except Exception as e:
        print(e)
        return False

@celery.task(name='app.save_invoice_pdf_to_db')
def save_invoice_pdf_to_db(url, order_id):
    try:
        bucket = os.environ.get('BUCKET_NAME')
        print("Downloading PDF file")
        # download the file to uploads folder
        response = requests.get(url).content
        if response:
            print("Saving PDF file to uploads folder")
            file_data = io.BytesIO(response)

            url = upload_file_to_s3(
                                    file=file_data,  
                                    object_name=uuid.uuid4().hex+'invoice.pdf',
                                    bucket=bucket, public=True)
            print("URL: ", url)
            if url:
                print("Saving PDF file to DB")
                order = Orders.query.get(order_id)
                order.invoice_url = url
                db.session.commit()
                print("PDF file saved to DB")
                return True
            else:
                print("Error while saving PDF file to DB")
                return False
            
        
    except Exception as e:
        print(e)
        return False
       
def download_file(url):
    """ Download file from a given URL """
    response = requests.get(url)
    if response.status_code == 200:
        # Assuming the URL ends with the filename
        local_filename = 'test_invoice.pdf'
        with open(local_filename, 'wb') as f:
            f.write(response.content)
        return local_filename
    else:
        raise Exception(f"Failed to download file: Status code {response.status_code}")

def get_stripe_mode():
    if current_user.role in TEST_USER_ROLES:
        return 'test'
    else:
        return 'live'

# Database initialization function
def init_db():
    db.create_all()
    admin_username = 'admin'
    admin_password = generate_password_hash('admin')
    admin_email = 'admin@admin.com'
    test_username = 'test'
    test_email = 'test@test.com'
    test_password = generate_password_hash('test123')
 
    # Check if the default test user exists
    test_user = Users.query.filter_by(username=test_username).first()   
    if not test_user:
        # Create the default test user
        test_user = Users(username=test_username, email=test_email, password=test_password, role='test')
        db.session.add(test_user)
        db.session.commit()

    # Check if the default admin user exists
    admin_user = Users.query.filter_by(username=admin_username).first()
    if not admin_user:
        # Create the default admin user
        admin_user = Users(username=admin_username, password=admin_password, role='admin', email=admin_email)
        db.session.add(admin_user)
        db.session.commit()

if ENV == 'dev' :
    HOST_URL = os.environ.get('HOST_URL', 'http://localhost:5000/')
    app.debug = True
    ACCESS_KEY_ID = os.environ.get('CLOUDCUBE_ACCESS_KEY_ID', '')
    SECRET_ACCESS_KEY = os.environ.get('CLOUDCUBE_SECRET_ACCESS_KEY', '')
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
        # CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        # app.config['CELERY_RESULT_BACKEND'] = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')



else:
    HOST_URL = os.environ.get('HOST_URL', '')
    app.debug = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    ACCESS_KEY_ID = os.environ.get('CLOUDCUBE_ACCESS_KEY_ID', '')
    SECRET_ACCESS_KEY = os.environ.get('CLOUDCUBE_SECRET_ACCESS_KEY', '')

    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"): 
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)

    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SECRET_KEY'] = SECRET_KEY
    
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS


YOUR_DOMAIN = os.environ.get('HOST_URL', 'http://localhost:5000/')

# Load the user from the database for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    user = Users.query.get(int(user_id))
    if user:
        if user.role == 'test':
            stripe.api_key = os.environ.get('STRIPE_TEST_SECRET_KEY')
            STRIPE_MODE = 'test'
        else:
            stripe.api_key = os.environ.get('STRIPE_LIVE_SECRET_KEY')
            STRIPE_MODE = 'live'
        return user
    else:
        return None

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Users(UserMixin,db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(100), nullable=True)
    password = db.Column(db.Text, nullable=False)
    role = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    ship_address = db.relationship('UserAddress', backref='user_shipping', lazy=True)
    billing_address = db.relationship('UserAddress', backref='user_billing', lazy=True)

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

class UserAddress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    address = db.Column(db.Text, nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<UserAddress %r>' % self.id
    
    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code
        }
    
    def serialize2(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "address": self.address,
            "city": self.city,
            "state": self.state,
            "country": self.country,
            "postal_code": self.postal_code,
            "created_at": self.created_at
        }


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    customer_id = db.Column(db.String(100), nullable=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(100), nullable=False)
    invoice_id = db.Column(db.String(100), nullable=True)
    invoice_number = db.Column(db.Text, nullable=True)
    invoice_url = db.Column(db.Text, nullable=True)
    stripe_payment_id = db.Column(db.String(100), nullable=True)
    stripe_session_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Order %r>' % self.id
    
    def serialize(self):
        return {
            "id": self.id,
            "invoice_number": self.invoice_number,
            "total_price": f'CAD {self.total_price/100:,.2f}',
            "invoice_url": self.invoice_url,
            "status": self.status,
            "created_at": self.created_at
        }
    
    def serialize2(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "status": self.status,
            "created_at": self.created_at
        }

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)
    description1 = db.Column(db.Text, nullable=True)
    description2 = db.Column(db.Text, nullable=True)
    image_urls = db.Column(db.Text, nullable=True)
    variant = db.Column(db.String(100), nullable=True)
    color = db.Column(db.String(100), nullable=True)
    stripe_test_product_id = db.Column(db.String(100), nullable=True)
    stripe_live_product_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<Product %r>' % self.id
    
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "description1": self.description1,
            "description2": self.description2,
            "image_urls": self.image_urls,
            "variant": self.variant,    
            "color": self.color,
            "created_at": self.created_at,
            "stripe_test_product_id": self.stripe_test_product_id,
            "stripe_live_product_id": self.stripe_live_product_id
        }
    
    def serialize2(self):
        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "created_at": self.created_at
        }


class ImageGallery(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    image_dict = db.Column(db.Text, nullable=True)  
    default = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return '<ImageGallery %r>' % self.id

    def serialize(self):
        image_data = json.loads(self.image_dict)
        return {
            "id": self.id,
            "name": self.name,
            "image_json_data":  image_data,
            "default": self.default,
        }
    
    

# @app.route('/send/mail/')
# def send_mail():
#     subject = 'Test Mail'
#     body = 'This is a test mail'
#     recipient = 'rohitvinod92@gmail.com'
#     email_utils = EmailUtils(app)
#     response = email_utils.sendMail(subject, body, recipient)
#     if response:
#         return jsonify({'message': 'Mail sent successfully'}), 200
#     else:
#         return jsonify({'message': 'Error while sending mail'}), 500


@app.route('/test/get/sheet/data')
def get_sheet_data_api():
    sheet_name = 'Orange Cat Customer Enquiry'
    sheet_range = 'Sheet1'
    data = ['21-02-2023', 'Rohit', 'test@admin.com', '1234567890', 'Model 2', 'New Message', 'Pending']
    data = append_data_spreadsheet(data, sheet_name, sheet_range)
    if data:
        return jsonify(data), 200
    else:
        return jsonify({'message': 'Error while fetching data'}), 500 


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('You need to be an admin to access this page', 'error')
            return redirect(url_for('user_login'))
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



# admin/socials
@app.route('/admin/socials', methods=['GET', 'POST'])
@admin_required
def admin_socials():
    return render_template('admin/socials.html')

@app.route('/admin/settings')
@admin_required
def admin_settings():
    # Your admin settings panek code here
    return render_template('admin/settings.html')



@app.route('/admin/products')
@admin_required
def admin_products():
    return render_template('admin/products-list.html')

@app.route('/admin/api/fetch/products', methods=['GET'])
@admin_required
def fetch_products():
    try:
        products = Products.query.all()
        products = list(map(lambda product: product.serialize(), products))
        return jsonify({'products': products}), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/admin/api/delete/product', methods=['POST'])
@admin_required
def delete_product():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            product_id = request_data.get('id', None)
            if product_id:
                product = Products.query.get(product_id)
                db.session.delete(product)
                db.session.commit()
                return jsonify({'message': 'Product deleted successfully'}), 200
            else:
                return jsonify({'message': 'Product ID not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/admin/api/add/product', methods=['POST'])
@admin_required
def add_product():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            name = request_data.get('name', None)
            price = request_data.get('price', None)
            description1 = request_data.get('description1', None)
            description2 = request_data.get('description2', None)
            image_urls = request_data.get('image_urls', None)
            variant = request_data.get('variant', None)
            color = request_data.get('color', None)
            stripe_test_product_id = request_data.get('stripe_test_product_id', None)
            stripe_live_product_id = request_data.get('stripe_live_product_id', None)
            if name and price:
                new_product = Products(name=name, price=price, description1=description1, description2=description2, image_urls=image_urls, variant=variant, color=color, stripe_test_product_id=stripe_test_product_id, stripe_live_product_id=stripe_live_product_id)
                db.session.add(new_product)
                db.session.commit()
                return jsonify({'message': 'Product added successfully'}), 200
            else:
                return jsonify({'message': 'Name or Price not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
# /admin/api/edit/product
@app.route('/admin/api/edit/product', methods=['POST'])
@admin_required
def edit_product():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            product_id = request_data.get('id', None)
            name = request_data.get('name', None)
            price = request_data.get('price', None)
            description1 = request_data.get('description1', None)
            description2 = request_data.get('description2', None)
            image_urls = request_data.get('image_urls', None)
            variant = request_data.get('variant', None)
            color = request_data.get('color', None)
            stripe_test_product_id = request_data.get('stripe_test_product_id', None)
            stripe_live_product_id = request_data.get('stripe_live_product_id', None)
            if product_id:
                product = Products.query.get(product_id)
                if product:
                    product.name = name
                    product.price = price
                    product.description1 = description1
                    product.description2 = description2
                    product.image_urls = image_urls
                    product.variant = variant
                    product.color = color
                    product.stripe_test_product_id = stripe_test_product_id
                    product.stripe_live_product_id = stripe_live_product_id
                    db.session.commit()
                    return jsonify({'message': 'Product updated successfully'}), 200
                else:
                    return jsonify({'message': 'Product not found'}), 400
            else:
                return jsonify({'message': 'Product ID not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/admin/settings/delete/all/images', methods=['GET', 'POST'])
@admin_required
def delete_all_images():
    try:
        bucket = os.environ.get('BUCKET_NAME')
        num_rows_deleted = db.session.query(ImageGallery).delete()
        db.session.commit()
        response = delete_all_files_from_s3(bucket)
        if response:
            return jsonify({'message':"All deleted" , "stats":True})
        return jsonify({'message':"Failed" , "stats":False})
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': 'Failed to delete records.', 'error': str(e), 'status': False})

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
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

@app.route('/user/login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists and the password is correct
        user = Users.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            if user.role == 'admin':
                return redirect(url_for('admin_panel')) 
            return redirect(url_for('index'))
        else:
            flash('Invalid email or password', 'error')

    return render_template('login.html')

# signup
@app.route('/user/signup', methods=['GET', 'POST'])
def user_signup():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = first_name + ' ' + last_name
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']


        # check if the password and confirm password match
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return redirect(url_for('user_signup'))
    
        # Check if the user exists
        user = Users.query.filter_by(email=email).first()
        if user:
            flash('User already exists', 'error')
            return redirect(url_for('user_login'))
        else:
            new_user = Users(username=username, email=email, password=generate_password_hash(request.form['password']), role='user')
            db.session.add(new_user)
            db.session.commit()
            flash('User created successfully', 'success')
            return redirect(url_for('user_login'))

    return render_template('signup.html')



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

@app.route('/models')
def view_products():
    products = Products.query.all()
    return render_template('bikes.html', products=products)

@app.route('/products/<int:id>')
def view_product(id):
    # product = Products.query.get_or_404(id)
    return render_template('product-details.html')


@app.route('/get/products/json/<name>')
def get_products_json(name):
    data = read_json_file('static/data/product-data.json') # {'bow': [{...}, {...}], 'arrow': [{...}, {...}]}
    products = data.get('products', {})
    if not products:
        return jsonify({'message': 'Error while reading the file'}), 500
    else: 
        if name:
            products = products.get(name, [])
            return jsonify(products), 200
        else:
            return jsonify({'message': 'Name not provided'}), 400
        

    

def read_json_file(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except Exception as e:
        print(e)
        return None

@app.route('/model/bow/<variant>')
def view_model_bow(variant):
    return render_template('bow.html', variant=variant)





@app.route('/model/arrow/<variant>')
def view_model_arrow(variant):
    return render_template('arrow.html', variant=variant)




@app.route('/api/products', methods=['GET'])
def get_products():
    products = Products.query.all()
    products = list(map(lambda product: product.serialize(), products))
    return jsonify(products), 200

# photo gallery
@app.route('/gallery/images')
def photo_gallery():
    return render_template('photo-gallery.html')


@app.route('/fetch/gallery/')
def fetch_gallery_photos():
    photos = os.listdir('static/images/gallery')
    photos = list(map(lambda photo: 'static/images/gallery/' + photo, photos))
    return jsonify(photos), 200

def fetch_gallery_status(gallery_name):
    '''
    gallery_name: str

    return: bool
    '''
    try:
        gallery_images = ImageGallery.query.filter_by(name=gallery_name).first()
        if gallery_images:
            gallery_status = gallery_images.default
            return gallery_status
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
def reset_all_gallery_status():
    '''
    gallery_name: str

    return: bool
    '''
    try:
        gallery_images = ImageGallery.query.all()
        for gallery in gallery_images:
            gallery.default = False
        db.session.commit()
        return True
    except Exception as e:
        print(e)
        return False


def update_gallery_status(gallery_name, status):
    '''
    gallery_name: str
    status: bool

    return: bool
    '''
    try:
        reset_all_gallery_status()
        gallery_images = ImageGallery.query.filter_by(name=gallery_name).first()
        if gallery_images:
            gallery_images.default = status
            db.session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False
    
@app.route('/fetch/gallery/status', methods=['POST'])
def fetch_gallery_status_api():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            gallery_name = request_data.get('gallery_name', None)
            if gallery_name:
                response = fetch_gallery_status(gallery_name)
                if response:
                    return jsonify({'message': 'Gallery status fetched successfully', 'status': response}), 200
                else:
                    return jsonify({'message': 'Gallery not found'}), 400
            else:
                return jsonify({'message': 'Gallery name not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/update/gallery/status', methods=['POST'])
def update_gallery_status_api():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            gallery_name = request_data.get('gallery_name', None)
            status = request_data.get('is_default', None)
            if gallery_name and status is not None:
                response = update_gallery_status(gallery_name, status)
                if response:
                    return jsonify({'message': 'Gallery status updated successfully'}), 200
                else:
                    return jsonify({'message': 'Gallery not found'}), 400
            else:
                return jsonify({'message': 'Gallery name or status not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500


def fetch_all_gallery_names_list():
    # type: () -> list
    try:
        gallery_images = ImageGallery.query.all()
        gallery_names = list(map(lambda gallery: gallery.name, gallery_images))
        return gallery_names
    except Exception as e:
        print(e)
        return []

def save_new_gallery_name_to_db(gallery_name):
    '''
    gallery_name: str

    return: bool
    '''
    try:
        EMPTY_GALLERY_IMAGES_DICT = {
                        1 : [],
                        2 : [],
                        3 : [],
                        4 : [],
                    }
        gallery_images = ImageGallery.query.filter_by(name=gallery_name).first()
        if not gallery_images:
            gallery_images = ImageGallery(name=gallery_name, image_dict=json.dumps(EMPTY_GALLERY_IMAGES_DICT))
            db.session.add(gallery_images)
            db.session.commit()
            return True
        else:
            print("gallery name already exists")
            return False
    except Exception as e:
        print(e)
        return False
    
@app.route('/fetch/gallery/names', methods=['GET'])
def fetch_gallery_names():
    try:
        if request.method == 'GET':
            gallery_names = fetch_all_gallery_names_list()
            context = {
                'gallery_names': gallery_names
            }
            return jsonify(context), 200
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/add/gallery/name', methods=['POST'])
def add_gallery_name():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            gallery_name = request_data.get('new_gallery_name', None)
            if gallery_name:
                response = save_new_gallery_name_to_db(gallery_name)
                if response:
                    return jsonify({'message': 'Gallery name added successfully'}), 200
                else:
                    return jsonify({'message': 'Gallery name already exists'}), 400
            else:
                return jsonify({'message': 'Gallery name not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/fetch/gallery/images/urls', methods=['POST'])
def fetch_gallery_photos_urls():
    if request.method == 'POST':
        try:
            SAMPLE_GALLERY_IMAGES_DICT = {
                        1 : [
                            url_for('static', filename='img/image-gallery/DSC_9039.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9047.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9051.jpeg'),
                        ],
                        2 : [
                            url_for('static', filename='img/image-gallery/DSC_9069.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9072.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9075.jpeg'),
                        ],
                        3 : [
                            url_for('static', filename='img/image-gallery/DSC_9077.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9039.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9078.jpeg'),
                        ],
                        4 : [
                            url_for('static', filename='img/image-gallery/DSC_9080.jpeg'),
                            url_for('static', filename='img/image-gallery/DSC_9137.jpeg'),
                            "https://i.imgur.com/iip2T3h.jpg",
                        ],
                    }
            EMPTY_GALLERY_IMAGES_DICT = {
                        1 : [],
                        2 : [],
                        3 : [],
                        4 : [],
                    }
            request_data = request.get_json()
            gallery_name = request_data.get('gallery_name', None)
            if gallery_name:
                gallery_images = ImageGallery.query.filter_by(name=gallery_name).first()
            else:
                gallery_images = ImageGallery.query.filter_by(default=True).first()
                if gallery_images:
                    gallery_name = gallery_images.name
                else:
                   gallery_name = ''
            # gallery_images.image_dict = json.dumps(SAMPLE_GALLERY_IMAGES_DICT)
            # db.session.commit()
            if gallery_images:
                gallery_images = gallery_images.serialize()
                image_json_data = gallery_images['image_json_data']
                gallery_status  = gallery_images['default']
            else:
                image_json_data = EMPTY_GALLERY_IMAGES_DICT
                gallery_status = False
                
            context = {
                'gallery_image_urls': image_json_data,
                'gallery_status': gallery_status,
                'gallery_name': gallery_name
            }
            return jsonify(context), 200
        except Exception as e:
            return jsonify({'message': str(e)}), 500

@app.route('/upload/gallery/image/url', methods=['POST'])
def upload_gallery_image_url():
    try:
        if request.method == 'POST':
            file = request.files['file']
            colToEdit = request.form['colToEdit']
            gallery_name = request.form['galleryName']
            if file:
                upload_image_url = get_image_url(file)
                if upload_image_url:
                    response = save_new_image_url_to_db(upload_image_url, colToEdit, gallery_name)
                    if response:
                        context = {
                            'image_url': upload_image_url
                        }

                        return jsonify(context), 200
                    else:
                        print("upload_gallery_image_url : Error while saving image url")
                        return jsonify({'message': 'Error while saving image url'}), 500
                else:
                    print("upload_gallery_image_url : No URL returned from s3")
                    return jsonify({'message': 'Error while uploading image'}), 500
            else:
                return jsonify({'message': 'No file selected'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        print("Error While Uploading Image :"+str(e))
        return jsonify({'message': str(e)}), 500
    
def get_image_url(image_file):
    # type: (FileStorage) -> str
    img_filename = secure_filename(image_file.filename)

    bucket = os.environ.get('BUCKET_NAME')
    print("preparing to upload to s3")
    url = upload_file_to_s3(file=image_file, bucket=bucket, public=True)
    return url


def save_new_image_url_to_db(image_url, col, gallery_name):
    '''
    image_url: str
    col: str

    return: bool
    '''
    try:
        image_gallery = ImageGallery.query.filter_by(name=gallery_name).first()
        if image_gallery:
            image_dict = json.loads(image_gallery.image_dict)
            image_dict[col].append(image_url)
            image_gallery.image_dict = json.dumps(image_dict)
            db.session.commit()
            return True
        else:
            print("image gallery not found")
            return False
    except Exception as e:
        print("Error While Saving Image URL :"+str(e))
        return False



def replace_save_image_url_to_db(image_url, image_to_replace_url, gallery_name):
    '''
    image_url: str
    image_to_replace_url: str

    return: bool
    '''
    try:
        image_gallery = ImageGallery.query.filter_by(name=gallery_name).first()
        if image_gallery:
            # find and replace the image url in the image_dict make sure replace in same index of the image url
            image_dict = json.loads(image_gallery.image_dict)
            for key, value in image_dict.items():
                if  image_to_replace_url in value:
                    index = value.index(image_to_replace_url)
                    image_dict[key][index] = image_url
                    print("image url replaced")
                    break
            image_gallery.image_dict = json.dumps(image_dict)
            db.session.commit()
            return True
        else:
            return False
    except Exception as e:
        print(e)
        return False

@app.route('/replace/gallery/image/url', methods=['POST'])
def replace_gallery_image_url():
    try:
        if request.method == 'POST':
            file = request.files['newFile']
            image_to_replace_url = request.form['imgUrl']
            gallery_name = request.form['galleryName']
            if file:
                upload_image_url = get_image_url(file)
                if upload_image_url:
                    response = replace_save_image_url_to_db(upload_image_url, image_to_replace_url, gallery_name)
                    if response:
                        s3_response = delete_image_url_from_s3(image_to_replace_url)
                        if s3_response:
                            print("image deleted successfully")
                            return jsonify({'message': 'Image replaced successfully'}), 200
                        else:
                            return jsonify({'message': 'Error while deleting image'}), 500
                    else:
                        print("replace_gallery_image_url : Error while saving image url")
                        return jsonify({'message': 'Error while saving image url'}), 500
            else:
                return jsonify({'message': 'No file selected'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500


def delete_image_url_from_db(image_url, col, gallery_name):
    '''
    image_url: str

    return: bool
    '''
    try:
        image_gallery = ImageGallery.query.filter_by(name=gallery_name).first()
        if image_gallery:
            image_dict = json.loads(image_gallery.image_dict)
            for key, value in image_dict.items():
                if  image_url in value:
                    image_dict[key].remove(image_url)
                    print("image url removed")
                    break
            image_gallery.image_dict = json.dumps(image_dict)
            db.session.commit()
            return True
        else:
            print("image gallery not found")
            return False
    except Exception as e:
        print(e)
        return False
    
def delete_image_url_from_s3(image_url):
    '''
    image_url: str

    return: bool
    '''
    try:
        image_url = image_url.split('/')[-1]
        bucket = os.environ.get('BUCKET_NAME')
        response = delete_file_from_s3(image_url, bucket, public=True)
        return response
    except Exception as e:
        print(e)
        return False
    
@app.route('/delete/gallery/image/url', methods=['POST'])
def delete_gallery_image_url():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            col = request_data.get('col', None)
            imageUrl = request_data.get('img_url', None)
            gallery_name = request_data.get('gallery_name', None)
            index = request_data.get('index', None)
            db_response = delete_image_url_from_db(imageUrl, col, gallery_name)
            if db_response:
                s3_response = delete_image_url_from_s3(imageUrl)
                if s3_response:
                    print("image deleted successfully")
                    return jsonify({'message': 'Image deleted successfully'}), 200
                else:
                    return jsonify({'message': 'Error while deleting image'}), 500
            else:
                return jsonify({'message': 'Error while deleting image'}), 500
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        print("Error While Deleting Image URL :"+str(e))
        return jsonify({'message': str(e)}), 500
    




            

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


def send_thank_you_mail(name, email, message):
    try:
        subject = 'Thank you for contacting Orange Cat Cycles'
        body = f""" 
        <html>
        <head></head>
        <body>
            <p><img src="https://cloud-cube-us2.s3.amazonaws.com/lu3eeh4bls8g/public/logo.png" alt="Company Logo" style="width:200px;height:50px;"></p>
            <p>Hello {name},</p>
            <p>Thank you for contacting Orange Cat Cycles. We have received your enquiry and will get back to you shortly.</p>
            <p>Regards,</p>
            <p>Orange Cat Cycles</p>
            <table style="width: 100%; font-family: Arial, sans-serif; color: #333333;">
                <tr>
                <td style="padding: 20px 0;">
                    <table style="border-top: 1px solid #DDDDDD; padding-top: 20px; width: 100%;">
                    <tr>
                        <td style="vertical-align: top; width: 200px;">
                        <img src="https://cloud-cube-us2.s3.amazonaws.com/lu3eeh4bls8g/public/logo.png" alt="Orange Cat Cycles Logo" style="width: 150px;">
                        </td>
                        <td style="vertical-align: top; padding-left: 20px; font-size: 14px;">
                        <p style="margin: 0; font-weight: bold; color: #E67E22;">Orange Cat Cycles</p>
                        <p style="margin: 5px 0;">+1 647 569 2081</p>
                        <p style="margin: 5px 0;">info@orangecatcycles.com</p>
                        <p style="margin: 5px 0;">orangecatcycles.com</p>
                        <p style="margin: 5px 0;">119 Indian Road, ZIP code: M6R 2V5, Toronto, Canada, Ontario</p>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="padding-top: 20px; text-align: center;">
                        <a href="http://www.facebook.com" style="margin-right: 10px;"><img src="facebook_icon_url" alt="Facebook" style="vertical-align: middle;"></a>
                        <a href="http://www.linkedin.com" style="margin-right: 10px;"><img src="linkedin_icon_url" alt="LinkedIn" style="vertical-align: middle;"></a>
                        <a href="http://www.instagram.com"><img src="instagram_icon_url" alt="Instagram" style="vertical-align: middle;"></a>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
        </body>
        </html>

        """
        recipient = email
        # email_utils = EmailUtils(app)
        # response = email_utils.sendMail(subject, body, recipient)
        # if response:
        #     return True
        # else:
        #     return False
        # use shared task
        send_email_task.delay(subject, body, [recipient])
        return True
    except Exception as e:
        print(e)
        return False

def send_admin_mail(name, email, message, phone, model):
    try:
        subject = 'New Customer Enquiry'
        body = f"""
        <html>
        <head></head>
        <body>
            <p><img src="https://cloud-cube-us2.s3.amazonaws.com/lu3eeh4bls8g/public/logo.png" alt="Company Logo" style="width:200px;height:50px;"></p>
            <p>Hello Admin,</p>
            <p>A new customer enquiry has been received. Details are as follows:</p>
            <ul>
                <li>Name: {name}</li>
                <li>Email: {email}</li>
                <li>Phone: {phone}</li>
                <li>Model: {model}</li>
                <li>Message: {message}</li>
            </ul>
            <p>This data has been appended to the sheet. You can view it <a href="https://docs.google.com/spreadsheets/d/1pkxv2-yhyuxXI7FW0E2QTBhiOsiqLcqizs0VFzL_l0U/edit?pli=1#gid=0">here</a>.</p>
            <p>Regards,</p>
            <p>Orange Cat Cycles</p>
            <table style="width: 100%; font-family: Arial, sans-serif; color: #333333;">
                <tr>
                <td style="padding: 20px 0;">
                    <table style="border-top: 1px solid #DDDDDD; padding-top: 20px; width: 100%;">
                    <tr>
                        <td style="vertical-align: top; width: 200px;">
                        <img src="https://cloud-cube-us2.s3.amazonaws.com/lu3eeh4bls8g/public/logo.png" alt="Orange Cat Cycles Logo" style="width: 150px;">
                        </td>
                        <td style="vertical-align: top; padding-left: 20px; font-size: 14px;">
                        <p style="margin: 0; font-weight: bold; color: #E67E22;">Orange Cat Cycles</p>
                        <p style="margin: 5px 0;">+1 647 569 2081</p>
                        <p style="margin: 5px 0;">info@orangecatcycles.com</p>
                        <p style="margin: 5px 0;">orangecatcycles.com</p>
                        <p style="margin: 5px 0;">119 Indian Road, ZIP code: M6R 2V5, Toronto, Canada, Ontario</p>
                        </td>
                    </tr>
                    <tr>
                        <td colspan="2" style="padding-top: 20px; text-align: center;">
                        <a href="http://www.facebook.com" style="margin-right: 10px;"><img src="facebook_icon_url" alt="Facebook" style="vertical-align: middle;"></a>
                        <a href="http://www.linkedin.com" style="margin-right: 10px;"><img src="linkedin_icon_url" alt="LinkedIn" style="vertical-align: middle;"></a>
                        <a href="http://www.instagram.com"><img src="instagram_icon_url" alt="Instagram" style="vertical-align: middle;"></a>
                        </td>
                    </tr>
                    </table>
                </td>
                </tr>
            </table>
        </body>
        </html>
        """
        adminMailList = os.environ.get('ADMIN_MAILS_LIST', 'info@orangecatcycles.com')
        recipients = adminMailList.split(',')
        # email_utils = EmailUtils(app)
        # for recipient in recipients:
        #     response = email_utils.sendMail(subject, body, recipient)
        #     if not response:
        #         return False
        # return True
        # use shared task
        send_email_task.delay(subject, body, recipients)
        return True
    except Exception as e:
        print(e)
        return False
    

# api to get enquiry data
@app.route('/get/enquiry/data', methods=['POST'])
def get_enquiry_data():
    try:
        if request.method == 'POST':
            sheet_name = 'Orange Cat Customer Enquiry'
            sheet_range = 'Sheet1'
            data = request.get_json()
            datetime_now = datetime.datetime.now().strftime("%d-%m-%Y")
            data = [datetime_now] + list(data.values()) + ['Pending']
            res = append_data_spreadsheet(data, sheet_name, sheet_range)
            if res:
                # send thank you mail and admin mail
                send_thank_you_mail(data[1], data[2], data[5])
                send_admin_mail(data[1], data[2], data[5], data[3], data[4])
                return jsonify(data), 200
            else:
                return jsonify({'message': 'Error while fetching data'}), 500
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500

@app.route('/create-checkout-session', methods=['POST'])
@login_required
def create_checkout_session():
    try:
        if request.method == 'POST':
            product_payment_id = request.json.get('product_payment_id')
            session = stripe.checkout.Session.create(
                ui_mode = 'embedded',
                line_items=[
                    {
                        # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                        'price': product_payment_id,
                        'quantity': 1,
                    },
                ],
                mode='payment',
                redirect_on_completion='never',
                # collect shipping address and billing address
                # shipping_address_collection to all countries
                billing_address_collection='required',
                shipping_address_collection={ 
                    'allowed_countries': ['CA'],
                },
                invoice_creation={'enabled': True},
                customer_email=current_user.email,
                automatic_tax={'enabled': True},
                phone_number_collection={'enabled': True},
            )
    except Exception as e:
        return str(e)

    return jsonify(clientSecret=session.client_secret , sessionId=session.id)



@app.route('/save-order-data', methods=['POST'])
@login_required
def save_order_data():
    try:
        if request.method == 'POST':
            session_id = request.json.get('session_id')
            session = stripe.checkout.Session.retrieve(session_id)
            retry_count = 0
            while session.invoice is None and retry_count < 15:  # retries up to 5 times
                time.sleep(1)  # waits 1 second before the next try
                session = stripe.checkout.Session.retrieve(session_id)
                retry_count += 1

            if session.status != 'complete':
                return jsonify({'message': 'Payment not completed'}), 400

            invoice_data = stripe.Invoice.retrieve(session.invoice)
            invoice_id = invoice_data.id
            customer_id = invoice_data.customer
            invoice_number = invoice_data.number
            user_id = current_user.id
            product_id = 1
            quantity = 1
            total_price = invoice_data.amount_paid
            status = 'complete'
            stripe_payment_id = session.payment_intent
            stripe_session_id = session.id
            invoice_url = invoice_data.invoice_pdf if hasattr(invoice_data, 'invoice_pdf') else ''

            new_order = Orders(
                                user_id=user_id,
                                product_id=product_id, 
                                quantity=quantity, 
                                total_price=total_price, 
                                status=status, 
                                invoice_url=invoice_url,
                                invoice_id=invoice_id,
                                invoice_number=invoice_number,
                                customer_id=customer_id,
                                stripe_session_id=stripe_session_id,
                                stripe_payment_id=stripe_payment_id)
            db.session.add(new_order)
            db.session.commit()
            if invoice_url:
                save_invoice_pdf_to_db.delay(invoice_url, new_order.id)

            context = {
                'invoice_number': invoice_number,
                'status': status,
                'message': 'Order saved successfully'
            }
            return jsonify(context), 200
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'error': str(e)}), 500


 # https://pay.stripe.com/invoice/acct_1PCOIy07chPjetrC/test_YWNjdF8xUENPSXkwN2NoUGpldHJDLF9RNDM0dzFFTVlkMGlqYUJ5ZEt6WXFkRDkzSTR3M0I3LDEwNTY1NTg2Nw0200565wJrn0/pdf?s=ap
 
@app.route('/cancel.html')
def cancel():
    return render_template('cancel.html')

# checkout page
@app.route('/checkout/<product_id>', methods=['GET'])
@login_required
def checkout(product_id):
    STRIPE_MODE=get_stripe_mode()
    STRIPE_PK = os.environ.get('STRIPE_PK_TEST_KEY') if STRIPE_MODE == 'test' else os.environ.get('STRIPE_PK_LIVE_KEY')
    return render_template('checkout.html', stripe_pk=STRIPE_PK, stripe_mode=STRIPE_MODE, product_id=product_id)

# /api/fetch/product
@app.route('/api/fetch/product', methods=['POST'])
@login_required
def fetch_product():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            product_id = request_data.get('product_id', None)
            if product_id:
                product = Products.query.filter_by(id=product_id).first()
                if product:
                    STRIPE_MODE=get_stripe_mode()
                    STRIPE_PAYMENT_ID = product.stripe_test_product_id if STRIPE_MODE == 'test' else product.stripe_live_product_id
                    product = {
                        'name': product.name,
                        'image_urls': product.image_urls,
                        'description1': product.description1,
                        'color': product.color,
                        'stripe_product_id': STRIPE_PAYMENT_ID,
                    }
                    return jsonify({'product': product}), 200
                else:
                    return jsonify({'message': 'Product not found'}), 404
            else:
                return jsonify({'message': 'Product ID not provided'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# user profile 
@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

# /api/fetch/user/profile
@app.route('/api/fetch/user/profile', methods=['POST'])
@login_required
def fetch_user_profile():
    try:
        if request.method == 'POST':
            user = current_user
            if not user:
                return jsonify({'message': 'User not found'}), 404
            username_split = user.username.split(' ')
            first_name = username_split[0]
            last_name = username_split[1] if len(username_split) > 1 else ''
            context = { 
                "first_name" : first_name,
                "last_name" : last_name,
                "email" : user.email,
                "phone" : user.phone,
            }
            return jsonify(context), 200
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# save user data
@app.route('/api/update/user/profile', methods=['POST'])
@login_required
def save_user_data():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            user = current_user
            user.username = request_data.get('first_name', '') + ' ' + request_data.get('last_name', '')
            user.email = request_data.get('email', '')
            user.phone = request_data.get('phone', '')
            db.session.commit()
            return jsonify({'message': 'User data saved successfully'}), 200
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    
@app.route('/api/reset/user/password', methods=['POST'])
@login_required
def update_user_password():
    try:
        if request.method == 'POST':
            request_data = request.get_json()
            user = current_user
            old_password = request_data.get('current_password', '')
            new_password = request_data.get('new_password', '')
            confirm_password = request_data.get('confirm_password', '')
            if not old_password or not new_password or not confirm_password:
                return jsonify({'message': 'All fields are required'}), 400
            if old_password != user.password:
                return jsonify({'message': 'Old password is incorrect'}), 400
            if new_password != confirm_password:
                return jsonify({'message': 'Passwords do not match'}), 400
            user.password = new_password
            db.session.commit()
            return jsonify({'message': 'Password updated successfully'}), 200
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500
    

# user/orders
@app.route('/orders')
@login_required
def orders():
    return render_template('orders.html')

# /api/fetch/user/orders
@app.route('/api/fetch/user/orders', methods=['POST'])
@login_required
def fetch_user_orders():
    try:
        if request.method == 'POST':
            user_id = current_user.id
            orders = Orders.query.filter_by(user_id=user_id).all()
            orders = list(map(lambda order: order.serialize(), orders))
            return jsonify(orders), 200
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500


with app.app_context():
    init_db()

if __name__ == "__main__":
    app.run()


    