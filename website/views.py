from flask import Blueprint, render_template, session

views = Blueprint('views', __name__)

@views.route('/')
def homepage():
    return render_template('index.html')
