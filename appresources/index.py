from flask import Blueprint, render_template, current_app
from appresources.models import get_path
index_bp = Blueprint('index', __name__)

@index_bp.route('/')
def home():
    # Your home page logic here
    path = get_path(current_app.config['global_variables']['db'])
    print(path)
    if path ==  0:
        return render_template('fixpath.html')

    return render_template('index.html')