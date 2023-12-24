from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from functools import wraps
import os
import json
import requests
import datetime
import boto3


from AWS_Modules import upload_file_to_s3, delete_file_from_s3

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'static/img/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


db = SQLAlchemy(app)
migrate = Migrate(app, db)

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
    return render_template('about-us.html')

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
                gallery_name = gallery_images.name

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
                response = save_new_image_url_to_db(upload_image_url, colToEdit, gallery_name)
                context = {
                    'image_url': upload_image_url
                }
                return jsonify(context), 200
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
    print("uploaded to s3")
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
                    image_dict[key] = image_url
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
            file = request.files['file']
            image_to_replace_url = request.form['image_to_replace_url']
            gallery_name = request.form['gallery_name']
            if file:
                upload_image_url = get_image_url(file)
                response = replace_save_image_url_to_db(upload_image_url, image_to_replace_url, gallery_name)
                context = {
                    'image_url': upload_image_url
                }
                return jsonify(context), 200
            else:
                return jsonify({'message': 'No file selected'}), 400
        else:
            return jsonify({'message': 'Method not allowed'}), 405
    except Exception as e:
        return jsonify({'message': str(e)}), 500


def delete_image_url_from_db(image_url):
    '''
    image_url: str

    return: bool
    '''
    try:
        image_gallery = ImageGallery.query.first()
        if image_gallery:
            # find and replace the image url in the image_dict make sure replace in same index of the image url
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


    