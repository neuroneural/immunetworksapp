import os
from flask import Flask
from appresources.login import login_bp
from appresources.signup import signup_bp
from appresources.home import home_bp
from appresources.index import index_bp
from appresources.models import create_tables
from appresources.simulations import simulations_bp
from appresources.logout import logout_bp
from appresources.createsim import createsim_bp
from appresources.createdata import createdata_bp
from appresources.startsimulation import startsimulation_bp
from appresources.viewsimulations import viewsimulation_bp
from appresources.fixpath import fixpath_bp


comp = create_tables('immunetworks.db')
print(os.getcwd())

def create_app():
    app = Flask(__name__, template_folder="../resources/templates", static_folder="../resources/static")
    app.config['global_variables'] = {
    'url': 'https://c813ur0lif.execute-api.us-east-1.amazonaws.com/dev',
    'db': 'immunetworks.db'
    }
    app.register_blueprint(login_bp, url_prefix='/auth')
    app.register_blueprint(signup_bp, url_prefix='/auth')
    app.register_blueprint(home_bp)
    app.register_blueprint(index_bp)
    app.register_blueprint(logout_bp)
    app.register_blueprint(createsim_bp, url_prefix='/home')
    app.register_blueprint(simulations_bp, url_prefix='/home')
    app.register_blueprint(createdata_bp, url_prefix='/home')
    app.register_blueprint(startsimulation_bp, url_prefix='/home/simulations')
    app.register_blueprint(fixpath_bp)
    app.register_blueprint(viewsimulation_bp, url_prefix='/home/simulations')
    return app
