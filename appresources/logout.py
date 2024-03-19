import json
import requests
from flask import Blueprint, render_template, current_app
from appresources.models import remove_tokens

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout')
def logout():
    remove_tokens(current_app.config['global_variables']['db'])
    return render_template('index.html')