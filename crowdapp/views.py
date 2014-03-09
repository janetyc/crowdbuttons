from flask import Blueprint, Flask, Response, request, render_template

crowdapp = Blueprint('views', __name__, template_folder='templates')

@crowdapp.route('/')
def index():
    return render_template('index.html')

@crowdapp.route('/page_not_found')
def page_not_found():
    return render_template('404.html')
