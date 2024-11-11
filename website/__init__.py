from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import logging
import os
from dotenv import load_dotenv
db = SQLAlchemy()

load_dotenv()

def create_app():
    logging.basicConfig(level=logging.DEBUG)
    app = Flask(__name__, static_folder='static')
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY')

    app.config['SQLALCHEMY_DATABASE_URI'] = (f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}")

    print("Change1")
    print("Added New Stuff. Please Detect")

    try:
        db.init_app(app)
        with app.app_context():
            db.create_all()
        logging.info("Connected to Mysql")
    except Exception as e:
        logging.error("Connection Failed: Trying Again",)


    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    return app
