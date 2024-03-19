from flask import Blueprint, render_template,request, current_app, redirect, url_for
import requests
import json
from appresources.models import get_tokens

createsim_bp = Blueprint('createsim', __name__)

@createsim_bp.route('/createsim', methods=['POST','GET'])
def createsim():
    id_token = get_tokens(current_app.config['global_variables']['db'], current_app.config['global_variables']['url'])

    if id_token == False:
        print('No token found while opening to simulation, Login again')
        return render_template('login.html', error='No token found while opening to simulation, Login again')
    
    if request.method == 'GET':
        selected_users = request.form.getlist('users')
        headers = {'Content-Type': 'application/json','Authorization':id_token}
        response = requests.get(current_app.config['global_variables']['url']+'/user_runs', headers=headers).json()
        return render_template('createsim.html', users = response['body'])

    elif request.method == 'POST':
        data = {
                'Name': request.form.get('name'),
                'Description': request.form.get('description'),
                'Users': request.form.getlist('users'),
                'check_Threshold': int(request.form.get('checkThreshold')),
                'Classes': int(request.form.get('classes'))
        }
        headers = {'Content-Type': 'application/json','Authorization':id_token}
        response = requests.post(current_app.config['global_variables']['url']+'/runs_update', data=json.dumps(data),headers=headers).json()
        return redirect(url_for('home.home'))