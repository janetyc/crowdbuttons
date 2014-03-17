import os
from flask import Flask, redirect, url_for
from flask.ext.mongokit import MongoKit
#from flask.ext.scss import Scss

#def create_app():
app = Flask(__name__)
env = os.getenv('ENV')

if env == "DEVELOPMENT":
    app.config.from_object('config.DevelopmentConfig')
    
elif env == "PRODUCTION":
    app.config.from_object('config.ProductionConfig')
    
elif env == "TESTING":
    app.config.from_object('config.TestingConfig')
    
elif env == "DEBUG":
    app.config.from_object('config.DebugConfig')

else:
    app.config.from_object('config.Config')

db = MongoKit(app)

from crowdapp.views import views #should put after app
app.register_blueprint(views)
#Scss(app, static_dir='static', asset_dir='assets')

@app.route("/")
def index():
    return redirect(url_for('views.index'))

@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('views.page_not_found'))

@app.errorhandler(400)
def bad_request(error):
    return redirect(url_for('views.bad_request'))

#    return app, db

#call create_up function
#app, db = create_app()
