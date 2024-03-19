import os
import json
import requests
from flask import Blueprint, render_template,  request, url_for, redirect, current_app

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
    
        # If validation is 0, show only email field
        if request.form['validation'] == '0':
            email = request.form['email']
            data = {
                "email": request.form.get('email'),
            }
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            
            # Make a POST request to the login API endpoint
            response = requests.post(current_app.config['global_variables']['url']+'/identityadd', data=json_data, headers=headers).json()
            if response['statusCode']==404:
                return render_template('signup.html', validation=1 , email = request.form['email'])
        if request.form['validation'] == '1':
            email = request.form['email']
            data = {
                "email": email,
            }
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            
            # Make a POST request to the login API endpoint
            response = requests.post(current_app.config['global_variables']['url']+'/identityadd', data=json_data, headers=headers).json()
            if response['statusCode']==404:
                return render_template('signup.html', validation=1 , email = request.form['email'])
            else:
                return render_template('signup.html', validation=2 ,email = request.form['email'])
        else:
            data = {
                "email": request.form.get('email'),
                "username": request.form['username'],
                "password": request.form['password']
            }
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            response = requests.post(current_app.config['global_variables']['url']+'/identityadd', data=json_data, headers=headers).json()
            if response['statusCode'] == 200:
                return render_template('login.html')
            else:
                return render_template('signup.html', validation=2 ,email = request.form['email'])
    
    # Render the signup form
    return render_template('signup.html', validation=0)
