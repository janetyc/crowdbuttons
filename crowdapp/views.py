from flask import Blueprint, Flask, Response, request, render_template

views = Blueprint('views', __name__, template_folder='templates')

@views.route('/')
def index():
    return render_template('index.html')

@views.route('/404')
def page_not_found():
    return render_template('404.html'), 404
