import os
import json
import requests
from appresources.models import save_auth_tokens, get_tokens, save_simulation_status, get_table_info
from flask import Blueprint, render_template,  request, current_app, redirect, url_for

login_bp = Blueprint('login', __name__)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    Id_token = get_tokens(current_app.config['global_variables']['db'],current_app.config['global_variables']['url'])
    if Id_token==False:
        if request.method == 'POST':

            data = {
                "username": request.form.get('username'),
                "password": request.form.get('password'),
                "request": "LOGIN"
            }
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            response = requests.post(current_app.config['global_variables']['url']+'/login', data=json_data, headers=headers).json()
            if response['statusCode']==200:
                save_auth_tokens(current_app.config['global_variables']['db'],response['body']['AuthenticationResult']['IdToken'], response['body']['AuthenticationResult']['RefreshToken'],)
                return render_template('home.html')
            else:
                error = 'Invalid username or password or the User is not yet verified. Please try again!.'
    else:
        headers = {'Content-Type': 'application/json','Authorization':Id_token}
        response = requests.post(current_app.config['global_variables']['url']+'/runs', data=json.dumps({}), headers=headers).json()
        data = []
        for i in response['body']:
            save_simulation_status(current_app.config['global_variables']['db'],int(i))
            data.append({'ID':i,
            "Name":response['body'][i]['name'],
            "Description":response['body'][i]['description'],
            "Classes" : response['body'][i]['classes'],
            "Users": response['body'][i]['users']
            })
        # Your home page logic here
        datasets_data =  get_table_info(current_app.config['global_variables']['db'])
        pretrfiles_data = [
                    { "ID": 1, "Name": "Model 1", "Description": "Description for Model 1" },
                    { "ID": 2, "Name": "Model 2", "Description": "Description for Model 2" }
                ]
        return render_template('home.html', simulation_data=data, Datasets = datasets_data, pretrfiles = pretrfiles_data)
        
    return render_template('login.html',  error=error)
