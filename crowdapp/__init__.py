import os
from flask import Flask, redirect, url_for
from views import views
#from flask.ext.scss import Scss

app = Flask(__name__)
env = os.getenv('ENV')

if env == "DEVELOPMENT":
    app.config.from_object('config.DevelopmentConfig')
elif env == "PRODUCTION":
    app.config.from_object('config.ProductionConfig')
elif env == "TESTING":
    app.config.from_object('config.TestingConfig')
else:
    app.config.from_object('config')


app.register_blueprint(views)
#Scss(app, static_dir='static', asset_dir='assets')

@app.route("/")
def index():
    return redirect(url_for('views.index'))

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('views.page_not_found'))
