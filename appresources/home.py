import json
import requests
from flask import Blueprint, render_template, current_app
from appresources.models import get_tokens, save_simulation_status, get_table_info, get_model_stat_data

home_bp = Blueprint('home', __name__)

@home_bp.route('/home')
def home():
    id_token = get_tokens(current_app.config['global_variables']['db'],current_app.config['global_variables']['url'])
    if id_token==False:
        print('No token found while opening to home page, Login again!')
        return render_template('login.html',  error='No token found while opening to home page, Login again!')
    
    
    headers = {'Content-Type': 'application/json','Authorization':id_token}
    response = requests.post(current_app.config['global_variables']['url']+'/runs', data=json.dumps({}), headers=headers).json()
    data = []
    pth = []
    for i in response['body']:
        save_simulation_status(current_app.config['global_variables']['db'],int(i))
        data.append({'ID':i,
        "Name":response['body'][i]['name'],
        "Description":response['body'][i]['description'],
        "Classes" : response['body'][i]['classes'],
        "Users": response['body'][i]['users']
        })
        a,b= get_model_stat_data(int(i))
        upload =1
        download =1
        Loss  = 'Not available'
        if a is not None:
            upload = 0
            if b is None:
                Loss = 'Pretreined Model loss N/A'
            else:
                Loss = str(b)
        else:
            download = 0 

        pth.append({'ID':i,
        "Name":response['body'][i]['name'],
        "Description":response['body'][i]['description'],
        'Upload': upload,
        'Download': download,
        'Loss': Loss
        })

    # Your home page logic here
    datasets_data =  get_table_info(current_app.config['global_variables']['db'])
    pretrfiles_data = pth
    # [
    #              { "ID": 1, "Name": "Model 1", "Description": "Description for Model 1" },
    #              { "ID": 2, "Name": "Model 2", "Description": "Description for Model 2" }
    #         ]
    return render_template('home.html', simulation_data=data, Datasets = datasets_data, pretrfiles = pretrfiles_data)