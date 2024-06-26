import logging
import torch
import time
import ast
import json
import requests
import numpy as np
from datetime import datetime

# Configure logging
logging.basicConfig(filename='training.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def upload_gradients(url, runid, keys, gradients):
    try:
        data = {
            "runid": str(runid),
            "gradients": gradients
        }
        json_data = json.dumps(data)
        headers = {'Content-Type': 'application/json','Authorization':keys}
        requests.post(url+'/results', data=json_data, headers=headers)
    except Exception as e:
        logging.error(f"Failed to upload gradients: {e}")

def get_gradients(url, runid, keys):
    try:
        data = {
            "runid": str(runid),
        }
        json_data = json.dumps(data)
        headers = {'Content-Type': 'application/json','Authorization':keys}
        return requests.post(url+'/agggrad', data=json_data, headers=headers).json()
    except Exception as e:
        logging.error(f"Failed to get gradients: {e}")

def activate_user(url, runid, keys):
    try:
        data = {
            "activate": 1,
            "runid": int(runid)
        }
        json_data = json.dumps(data)
        headers = {'Content-Type': 'application/json','Authorization':keys}
        requests.post(url+'/activate', data=json_data, headers=headers)
    except Exception as e:
        logging.error(f"Failed to activate user: {e}")

def deactivate_user(url, runid, keys):
    try:
        data = {
            "activate": 0,
            "runid": int(runid)
        }
        json_data = json.dumps(data)
        headers = {'Content-Type': 'application/json','Authorization':keys}
        requests.post(url+'/activate', data=json_data, headers=headers)
    except Exception as e:
        logging.error(f"Failed to deactivate user: {e}")

def convert_weights_to_serializable_dict(weights):
    serializable_weights = {}
    for key, value in weights.items():
        if isinstance(value, torch.Tensor):
            serializable_weights[key] = value.tolist()
        else:
            serializable_weights[key] = value
    return json.dumps(serializable_weights)

def upload_weights(url,weights,keys,runid):
    try:
        data = {
            "weights": convert_weights_to_serializable_dict(weights),
            "runid": int(runid)
        }
        json_data = json.dumps(data)
        headers = {'Content-Type': 'application/json','Authorization':keys}
        return requests.post(url+'/weights', data=json_data, headers=headers).json()
    except Exception as e:
        logging.error(f"Failed to upload weights: {e}")

def get_weights(url,keys,runid):
    try:
        data = {
            "runid": int(runid)
        }
        json_data = json.dumps(data)
        headers = {'Content-Type': 'application/json','Authorization':keys}
        return requests.post(url+'/weightsavg', data=json_data, headers=headers).json()
    except Exception as e:
        logging.error(f"Failed to get weights: {e}")

class training():
    def __init__(self, upload_model, get_stat, insert_simulation_data, start_simulation, end_simulation, table, keys, url, get_token, meshnet, runid, dice, loader, modelAE, dbfile, l_r=0.003125, classes=3, epochs=10, cubes=1, label='GWlabels'):
        try:
            self.upload_model = upload_model
            self.get_stat = get_stat
            self.keys = keys
            self.url = url
            self.dice = dice
            logging.info("no error")
            self.runid = runid
            self.start_simulation = start_simulation
            self.end_simulation = end_simulation
            self.insert_simulation_data = insert_simulation_data
            self.cubes = cubes
            self.classes = classes
            self.get_tokens = get_token
            self.shape = 256 // self.cubes
            self.epochs = epochs
            self.criterion = torch.nn.CrossEntropyLoss()
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logging.info(f"Device: {self.device}")
            self.lr = l_r
            self.db = dbfile
            self.train, self.valid, self.test = loader(self.db, table, label_type=label, num_cubes=self.cubes).get_loaders()
            self.model = meshnet(1, self.classes, 1, modelAE).to(self.device, dtype=torch.float32)
            logging.info(self.model)
            self.optimizer = torch.optim.RMSprop(self.model.parameters(), lr=self.lr)
            self.scheduler = torch.optim.lr_scheduler.OneCycleLR(
                self.optimizer, 
                max_lr=self.lr, 
                div_factor=100,
                pct_start=0.2,
                steps_per_epoch=len(self.train),
                epochs=self.epochs)
            logging.info('Initilizing training successful')
            if self.get_stat(int(self.runid))[0]:
                model_state_binary = self.get_stat(int(self.runid))[0]
                with open(str(self.runid)+'_model_state_loaded.pth', 'wb') as f:
                    f.write(model_state_binary)
                self.model.load_state_dict(torch.load(str(self.runid)+'_model_state_loaded.pth'))
            try:
                logging.info('Uploading weights')
                upload_weights(url = self.url,weights=self.model.state_dict(),keys=self.keys,runid=self.runid)
                try:
                    weights = get_weights(url=self.url,runid=self.runid, keys=self.keys)
                    logging.info('Getting weights for model')
                    while weights['statusCode']!=200:
                        time.sleep(6)
                        weights = get_weights(url=self.url,runid=self.runid, keys=self.keys)
                    if weights['result']!=0:
                        result_dict = json.loads(weights['result'])
                        new_state_dict = {}
                        for key, value in result_dict.items():
                                new_state_dict[key] = torch.tensor(value)
                        self.model.load_state_dict(new_state_dict)
                        logging.info('Got weights and updated model')
                except Exception as e:
                    logging.error(f"Failed to get weights: {e}")
            except Exception as e:
                logging.error(f"Failed to upload weights: {e}")
        except Exception as e:
            logging.error(f"Initialization failed: {e}")
            deactivate_user(self.url, self.runid ,self.keys)

    def train_f(self):
        try:
            logging.info('Started training')
            activate_user(self.url, self.runid ,self.keys)
            epoch = 0
            while epoch != self.epochs:
                logging.info("Epoch : "+str(epoch))
                self.model.train()
                for image, label in self.train:
                    try:

                        self.keys = self.get_tokens(self.db, self.url)
                        self.optimizer.zero_grad()
                        logging.info("Reshaping Images and Labels accordingly")
                        output = self.model(image.reshape(-1, 1, self.shape, self.shape, self.shape))
                        loss = self.criterion(output, label.reshape(-1, self.shape, self.shape, self.shape).long())
                        logging.info("Caliculating Cross entropy loss")
                        train_metrics = {'Train_loss':float(loss.item())}
                        logging.info("'Train_loss'"+str(float(loss.item())))
                        if self.cubes == 1:
                            dice_loss = self.dice(torch.argmax(torch.squeeze(output), 0), label.reshape(self.shape, self.shape, self.shape), labels=[i for i in range(self.classes)])
                        else:
                            dice_loss = self.dice(torch.argmax(torch.squeeze(output), 1), label.reshape(-1, self.shape, self.shape, self.shape), labels=[i for i in range(self.classes)])
                        loss.backward()
                        logging.info("claiculating Dice Loss")
                        for cls in range(self.classes):
                            train_metrics.update({f'Train_dice_{cls}':float(dice_loss[cls])})
                        logging.info(train_metrics)
                        train_metrics.update({'LR':self.scheduler.get_last_lr()[0]})
                        self.insert_simulation_data(self.db,self.runid,train_metrics,'train')
                        logging.info("Logging above metrics to database")
                        local_gradients = [param.grad.clone() for param in self.model.parameters()]
                        numpy_arrays = [tensor.cpu().numpy() for tensor in local_gradients]
                        nested_lists = [array.tolist() for array in numpy_arrays]
                        logging.info("Seding gradients tfor centralized aggregation")
                        upload_gradients(self.url, self.runid, self.keys, str(nested_lists))
                        logging.info("Sent centralized aggregation")
                        result =  get_gradients(self.url, self.runid, self.keys)
                        logging.info("Collecting aggregated Gradients")
                        while result is None:
                            logging.info('None result')
                            time.sleep(6)
                            result =  get_gradients(self.url, self.runid, self.keys)
                            logging.info("Collecting aggregated Gradients - Waiting 0")
                        while result['result'] =='None':
                            time.sleep(5)
                            result =  get_gradients(self.url, self.runid, self.keys)
                            logging.info("Collecting aggregated Gradients - Waiting 1")
                        logging.info("collected aggregated Gradients")
                        agg_grad = [np.array(array) for array in ast.literal_eval(result['result'])]
                        logging.debug(agg_grad)
                        with torch.no_grad():
                            for param, avg_grad in zip(self.model.parameters(), agg_grad):
                                if param.requires_grad:
                                    avg_grad = torch.tensor(avg_grad, dtype=param.grad.dtype, device=param.grad.device)
                                    param.grad = avg_grad.clone().detach().to(param.grad.device)
                        logging.debug(self.scheduler.get_last_lr()[0])
                        logging.info("Updating with collected aggregated gradients")
                        self.optimizer.step()
                        self.scheduler.step()
                        logging.info("Optmizer/Scheduler - step")

                    except Exception as e:
                        logging.error(f"Error during training: {e}")
                        logging.info(" Exception Updating with collected aggregated gradients")
                        self.optimizer.step()
                        self.scheduler.step()
                        logging.info("Exception Optmizer/Scheduler - step")

                self.model.eval()
                with torch.no_grad():
                    for image, label in self.valid:
                        try:
                            output = self.model(image.reshape(-1,1,self.shape,self.shape,self.shape))
                            loss = self.criterion(output, label.reshape(-1, self.shape, self.shape, self.shape).long())
                            valid_metrics = {'Valid_loss':float(loss.item())}
                            if self.cubes == 1:
                                dice_loss = self.dice(torch.argmax(torch.squeeze(output), 0), label.reshape(self.shape, self.shape, self.shape), labels=[i for i in range(self.classes)])
                            else:
                                dice_loss = self.dice(torch.argmax(torch.squeeze(output), 1), label.reshape(-1, self.shape, self.shape, self.shape), labels=[i for i in range(self.classes)])
                            for cls in range(self.classes):
                                valid_metrics.update({f'Valid_dice_{cls}':float(dice_loss[cls])})
                            self.insert_simulation_data(self.db,self.runid,valid_metrics,'valid')
                            logging.info(valid_metrics)
                        except Exception as e:
                            logging.error(f"Error during validation: {e}")
                
                logging.info('Uploading stat dict to db')
                # upload_model_to_database(model, run_id, loss=None, db_name='immunetworks.db'):
                self.upload_model(model = self.model,run_id=self.runid, loss= loss.item())
                try:
                    logging.info(f'Uploading weights after Ecoch: {epoch}')
                    upload_weights(url = self.url,weights=self.model.state_dict(),keys=self.keys,runid=self.runid)
                except Exception as e:
                    logging.error(f"Failed to upload weights after epoch {epoch}: {e}")
                epoch += 1
            deactivate_user(self.url, self.runid ,self.keys)
            self.end_simulation(self.db,str(self.runid))
        except Exception as e:
            logging.error(f"Error in training function: {e}")
            deactivate_user(self.url, self.runid ,self.keys)
            self.end_simulation(self.db,str(self.runid))

# Example usage
# Create a logging object
# logger = logging.getLogger(__name__)

# Use it for logging
# logger.info("This is an information message")
