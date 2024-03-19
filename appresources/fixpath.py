import os
from flask import Blueprint, render_template, request, current_app
from appresources.models import put_path

fixpath_bp = Blueprint('fixpath', __name__)

@fixpath_bp.route('/fixpath', methods = ['POST'])
def fixpath():
    # Your home page logic here
    input_text = request.form['input_text']
    if os.path.exists(input_text+'/appresources/meshnet/modelAE.json') ==  False:
        print('Path invalid',input_text+'/appresources/meshnet/modelAE.json')
        return render_template('fixpath.html')
    put_path(current_app.config['global_variables']['db'],input_text)
    return render_template('index.html')