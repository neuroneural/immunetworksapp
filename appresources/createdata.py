from flask import Blueprint, render_template,request, current_app, redirect,url_for
from appresources.models import get_tokens, create_dataset, create_blob_table, upload_dataframe_to_db
import pandas as pd
import nibabel as nib
import numpy as np
import os

createdata_bp = Blueprint('createdata', __name__)

def pad_tensor(img):
  target_shape = (256, 256, 256)
  if img.shape != target_shape:
    pad_x = (target_shape[0] - img.shape[0]) // 2
    pad_y = (target_shape[1] - img.shape[1]) // 2
    pad_z = (target_shape[2] - img.shape[2]) // 2
    return np.pad(img, ((pad_x, pad_x), (pad_y, pad_y), (pad_z, pad_z)), mode='constant')
  else:
    return img

@createdata_bp.route('/createdata', methods = ['GET','POST'])
def createdata():
    id_token = get_tokens(current_app.config['global_variables']['db'], current_app.config['global_variables']['url'])
    message = None
    valid = 0
    namecheck = 0
    filepath = None
    tablename = None

    if id_token == False:
        print('No token found while opening to simulation, Login again')
        return render_template('login.html', error='No token found while opening to simulation, Login again')

    if request.method == 'POST':
        filepath = request.form.get('filepath')
        absolute_path = os.path.dirname(filepath)
        if request.form['validation'] == '0':
            if os.path.exists(filepath) and filepath.lower().endswith('.csv'):
                try:
                    data = pd.read_csv(filepath)
                    for string in data.columns.tolist():
                        if ' ' in string:
                            message = "Spaces are present in headings"
                            return render_template("createdata.html", message=message, validation=valid)
                    invalids = []
                    for string in data.columns.tolist():
                        for fil in data[string]:
                            try:
                                nib.load(absolute_path+fil)
                            except Exception as e:
                                invalids.append(filepath+fil)
                    if len(invalids) > 0:
                        valid = 0 
                        message = "following files are not in correct format," + '/n'.join(invalids)
                except Exception as e:
                    message = str(e)
                valid = '1'

        elif request.form['validation'] == '1' and request.form['namecheck'] == '0':
            tablename = request.form['tablename']
            namecheck = '1'
            valid = '1'
            filepath = request.form.get('filepath') 
            data = pd.read_csv(filepath)
            if create_dataset(current_app.config['global_variables']['db'],tablename,tablename):
                data = pd.read_csv(filepath)
                create_blob_table(current_app.config['global_variables']['db'],tablename, data.columns.tolist())
                upload_dataframe_to_db(filepath, current_app.config['global_variables']['db'], tablename)
                return  redirect(url_for('home.home'))

            else:
                message = 'table already exists create an new one'
                valid = 1
                namecheck = 0
                
    return render_template(
        "createdata.html", 
        message=message, 
        tablename=tablename,
        filepath=filepath,
        validation=valid, 
        namecheck=namecheck)