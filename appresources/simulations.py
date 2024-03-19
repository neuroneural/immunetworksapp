from flask import Blueprint, render_template, request, current_app
from appresources.models import get_tokens, get_simulation_status, get_dataset_columns
import requests
simulations_bp = Blueprint('simulations', __name__)

@simulations_bp.route('/simulations', methods=['POST'])
def simulations():
    id_token = get_tokens(current_app.config['global_variables']['db'], current_app.config['global_variables']['url'])

    if id_token == False:
        print('No token found while opening to simulation, Login again')
        return render_template('login.html', error='No token found while opening to simulation, Login again')
    else:
        if request.method == 'POST':
            # Get data from the form
            simulation_id = request.form['simulation_id']
            simulation_name = request.form['simulation_name']
            simulation_description = request.form['simulation_description']
            simulation_classes = request.form['simulation_classes']
            simulation_users = request.form['simulation_users'].split(',')
            a = get_simulation_status(current_app.config['global_variables']['db'],int(simulation_id))
            st = 0
            print(a)
            if a:
                st = 1
            return render_template('simulations.html',
                                runid=simulation_id,
                                status= st, 
                                dataset_columns = get_dataset_columns(current_app.config['global_variables']['db']),
                                data={
                                    "body": {
                                        simulation_id: {
                                            "description": simulation_description,
                                            "name": simulation_name,
                                            "users": simulation_users,
                                            "classes": simulation_classes
                                        }
                                    }
                                })
        
        
