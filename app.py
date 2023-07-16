# flask boiler plate code with sql alchemy

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import json
import requests
import datetime

app = Flask(__name__)
CORS(app)



ENV = os.environ.get('ENV', 'prod')
LIVE_DB = os.environ.get('LIVE_DB', 'True')

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

class Products(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Integer, nullable=False)

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


    
@app.route('/')
def index():
    return render_template('index.html')

# about
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def view_products():
    products = Products.query.all()
    return render_template('products.html', products=products)

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
@app.route('/gallery')
def gallery():
    return render_template('gallery.html')


@app.route('/fetch/gallery/')
def fetch_gallery_photos():
    photos = os.listdir('static/images/gallery')
    photos = list(map(lambda photo: 'static/images/gallery/' + photo, photos))
    return jsonify(photos), 200

# video gallery
@app.route('/video')
def video():
    return render_template('video.html')

@app.route('/fetch/video/')
def fetch_video():
    videos = os.listdir('static/videos')
    videos = list(map(lambda video: 'static/videos/' + video, videos))
    return jsonify(videos), 200

# contact us
@app.route('/contact')
def contact():
    return render_template('contact.html')


    