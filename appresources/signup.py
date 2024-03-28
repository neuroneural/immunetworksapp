import os
import json
import requests
from flask import Blueprint, render_template,  request, url_for, redirect, current_app

signup_bp = Blueprint('signup', __name__)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    signup_message = 'Welcome to signup page'
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
                signup_message = 'Verifaction mail sent to email to verify the email address '+data['email']+' Please click verify to resend vrification link again'
                return render_template('signup.html', validation=1 , email = request.form['email'], message = signup_message)
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
                signup_message = 'Verifaction mail sent to email to verify the email address '+ data['email']+' Please click verify to resend vrification link again'
                return render_template('signup.html', validation=1 , email = request.form['email'], message = signup_message)
            else:
                signup_message = 'Email Verification completed please enter username and password'
                #  \n Password Policy \n Contains at least 1 number \n Contains at least 1 special character \n Contains at least 1 uppercase letter \nContains at least 1 lowercase letter'
                return render_template('signup.html', validation=2 ,email = request.form['email'], message = signup_message)
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
                return render_template('login.html', error = 'Signup link sent to email '+request.form.get('email')+'plase confirm the link to signin ')
            else:
                signup_message = signup_message = 'Please re-enter a  different username or a strong password'
                return render_template('signup.html', validation=2 ,email = request.form['email'], message = signup_message)
    
    # Render the signup form
    return render_template('signup.html', validation=0, message = signup_message)
