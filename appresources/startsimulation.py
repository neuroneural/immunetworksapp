from flask import Blueprint, render_template,request, current_app, redirect, url_for
from appresources.meshnet.meshnet import enMesh_checkpoint
from appresources.meshnet.loader import Scanloader
from appresources.meshnet.dice import faster_dice
from appresources.meshnet.trainer import training as tr
import threading
from appresources.models import insert_simulation_data, start_simulation, end_simulation, get_tokens, get_path

startsimulation_bp = Blueprint('startsimulation', __name__)


def call_training(run_id, get_token, db_file, id_token, classes, epochs, label, lr, table, url, dbfile, path):
        print(run_id, get_token, db_file, id_token, classes, epochs, label, lr, table, url, dbfile)
    # try:
        training =  tr(
            table = table,
            url = url,
            meshnet=enMesh_checkpoint, 
            start_simulation = start_simulation,
            end_simulation = end_simulation,
            insert_simulation_data = insert_simulation_data,
            get_token = get_token,
            runid = run_id,
            dice=faster_dice, 
            loader=Scanloader,
            modelAE=path+'/appresources/meshnet/modelAE.json',
            dbfile=db_file, 
            classes=classes, 
            epochs = epochs, 
            cubes=1, 
            label = label, 
            keys = id_token,
            l_r = lr)
        training.train_f()
    # except Exception as e:
    #     print(e)




@startsimulation_bp.route('/startsimulation', methods = ['POST'])
def startsimulation():
    id_token = get_tokens(current_app.config['global_variables']['db'], current_app.config['global_variables']['url'])

    if id_token == False:
        print('No token found while opening to simulation, Login again')
        return render_template('login.html', error='No token found while opening to simulation, Login again')
    else:
    # Your home page logic here
        dataset = request.form.get('dataset')
        column = request.form.get('column')
        run_id = request.form.get('run_id')
        classes = request.form.get('classes')
        learning_rate = request.form.get('learning_rate')
        epochs = request.form.get('epochs')
        print(run_id,column, dataset, classes, epochs, learning_rate)
        start_simulation(current_app.config['global_variables']['db'],int(run_id),int(classes))
        args = (int(run_id), get_tokens, current_app.config['global_variables']['db'], id_token, int(classes), int(epochs), str(column), float(learning_rate),str(dataset),current_app.config['global_variables']['url'], current_app.config['global_variables']['db'], get_path(current_app.config['global_variables']['db']))
        try:
            script_thread = threading.Thread(target=call_training, args=args)
            script_thread.start()
        except Exception as e:
            print(e)
        return redirect(url_for('home.home'))