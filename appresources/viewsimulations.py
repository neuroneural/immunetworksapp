from flask import Blueprint, render_template, request, current_app
from appresources.models import get_tokens, fetch_simulation_data, end_simulation

viewsimulation_bp = Blueprint('viewsimulation', __name__)
@viewsimulation_bp.route('/viewsimulation')
def view_simulator():
    id_token = get_tokens(current_app.config['global_variables']['db'], current_app.config['global_variables']['url'])

    if id_token == False:
        print('No token found while opening to simulation, Login again')
        return render_template('login.html', error='No token found while opening to simulation, Login again')
    else:
        runid = request.args.get('run_id')
        fetched_data = fetch_simulation_data(current_app.config['global_variables']['db'],runid)
        
        data = {
            'Train':{
                'Epoch':[],
                'Loss':[],
                'Dice0':[],
                'Dice1':[],
                'Dice2':[]
                },
            'Valid':{'Epoch':[],'Loss':[],'Dice0':[],'Dice1':[],'Dice2':[]}}
        c =1
        for i in fetched_data['train'][1]:
            data['Train']['Epoch'].append(c)
            data['Train']['Loss'].append(i[2])
            data['Train']['Dice0'].append(i[3])
            data['Train']['Dice1'].append(i[4])
            data['Train']['Dice2'].append(i[5])
            c+=1
        c =1
    
        for i in fetched_data['valid'][1]:
            data['Valid']['Epoch'].append(c)
            data['Valid']['Loss'].append(i[1])
            data['Valid']['Dice0'].append(i[2])
            data['Valid']['Dice1'].append(i[3])
            data['Valid']['Dice2'].append(i[4])
            c+=1

        # end_simulation(current_app.config['global_variables']['db'],str(runid))
        return render_template('viewsimulation.html', fetched_data=data, runid = runid)
