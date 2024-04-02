import os
from flask import Blueprint, render_template, current_app, redirect, url_for, request, send_file
from appresources.models import get_tokens, get_model_stat_data, upload_modelpth_to_database, get_path
pthmodule_bp = Blueprint('pthmodule', __name__)

@pthmodule_bp.route('/pthmodule/upload/',methods=['GET'])
def pthmodule_up():
    id_token = get_tokens(current_app.config['global_variables']['db'],current_app.config['global_variables']['url'])
    if id_token==False:
        print('No token found while opening to home page, Login again!')
        return render_template('login.html',  error='No token found while opening to home page, Login again!')
    # upload_modelpth_to_database(run_id, modelpth)
    message =None
    id = request.args.get('id')
    description = request.args.get('description')
    file_path = request.args.get('file_path')
    if file_path:
        if os.path.exists(file_path):   
            message = 'Exist'+file_path 
            try: 
                upload_modelpth_to_database(run_id=int(id),modelpth =  file_path)
                return redirect(url_for('home.home'))
            except Exception as e:
                print(e)
                message = 'Unable to upload .pth file '+ file_path+'due to '+str(e)
        else:
            message = 'Do not exist '+file_path 
    print('Upload',id,file_path)
    return render_template('pthmodule.html', id=id,description=description, message =message)

@pthmodule_bp.route('/pthmodule/download/<int:id>')
def pthmodule_down(id):
    id_token = get_tokens(current_app.config['global_variables']['db'],current_app.config['global_variables']['url'])
    if id_token==False:
        print('No token found while opening to home page, Login again!')
        return render_template('login.html',  error='No token found while opening to home page, Login again!')
    # upload_modelpth_to_database(run_id, modelpth)
    try:
        path = os.getcwd()
        pth,_ = get_model_stat_data(run_id=id)
        with open(path+'/'+str(id)+'model_state_loaded.pth', 'wb') as f:
            f.write(pth)
        response =  send_file(path+'/'+str(id)+'model_state_loaded.pth', as_attachment=True)
        os.remove(path+'/'+str(id)+'model_state_loaded.pth')
        return response
    except Exception as e:
        print(e)
    print('Download',id)
    return redirect(url_for('home.home'))
