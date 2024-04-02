# app/models.py
import os
import json
import zlib
import sqlite3
import torch
import requests
from datetime import datetime, timedelta
import nibabel as nib
import numpy as np
import pandas as pd

##########model.pth####################

def upload_model_to_database(model, run_id, loss=None, db_name='immunetworks.db'):
    torch.save(model.state_dict(), 'model_state.pth')
    with open('model_state.pth', 'rb') as f:
        model_state_binary = f.read()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT Runid FROM models WHERE Runid=?", (run_id,))
    existing_row = cursor.fetchone()

    if existing_row:
        if loss is None:
            cursor.execute("UPDATE models SET Model_data=? WHERE Runid=?", (model_state_binary, run_id))
        else:
            cursor.execute("UPDATE models SET Model_data=?, Loss=? WHERE Runid=?", (model_state_binary, loss, run_id))
    else:
        if loss is None:
            cursor.execute("INSERT INTO models (Runid, Model_data) VALUES (?, ?)", (run_id, model_state_binary))
        else:
            cursor.execute("INSERT INTO models (Runid, Model_data, Loss) VALUES (?, ?, ?)", (run_id, model_state_binary, loss))

    conn.commit()
    conn.close()
    os.remove('model_state.pth')


def upload_modelpth_to_database(run_id, modelpth, db_name='immunetworks.db'):
    with open(modelpth, 'rb') as f:
        model_state_binary = f.read()
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO models (Runid, Model_data) VALUES (?, ?)", (run_id, model_state_binary))
    conn.commit()
    conn.close()

def get_model_stat_data(run_id, db_name='immunetworks.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT Model_data,Loss FROM models WHERE Runid=?", (run_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return row[0], row[1]
    else:
        return None, None

#######simulations##########
def start_simulation( db, runid, classes):
        con = sqlite3.connect(db)
        cur = con.cursor()
        columns_str = ', '.join([f'Train_dice_{cls} REAL' for cls in range(classes)])
        query = f'CREATE TABLE IF NOT EXISTS simulator_train_{runid} (Runid Integer,LR REAL, Train_loss REAL, {columns_str})'
        cur.execute(query)
        columns_str = ', '.join([f'Valid_dice_{cls} REAL' for cls in range(classes)])
        query = f'CREATE TABLE IF NOT EXISTS simulator_valid_{runid} (Runid Integer, Valid_loss REAL, {columns_str})'
        cur.execute(query)
        cur.execute("UPDATE simulator_status SET Status = 1 WHERE Run_id = ?", (runid,))
        con.commit()

def insert_simulation_data( db, runid, data_dict, type_in):
        con = sqlite3.connect(db)
        cur = con.cursor()
        columns = list(data_dict.keys())
        values = tuple(data_dict.values())
        placeholders = ', '.join(['?' for _ in range(len(values))])
        query = f'INSERT INTO simulator_{type_in}_{runid} (Runid, {", ".join(columns)}) VALUES (?, {placeholders})'
        cur.execute(query, (runid,) + values)
        con.commit()

def end_simulation(db, runid):
        con = sqlite3.connect(db)
        cur = con.cursor()
        cur.execute("UPDATE simulator_status SET Status = 0 WHERE Run_id = ?", (runid,))
        con.commit()

def fetch_simulation_data(db,runid):
        con = sqlite3.connect("immunetworks.db")
        cur = con.cursor()
        fetched_data = {}
        cur.execute(f"PRAGMA table_info(simulator_train_{runid})")
        columns_info = cur.fetchall()
        column_names = [info[1] for info in columns_info if info[1] != 'Runid']
        cur.execute(f"SELECT * FROM simulator_train_{runid} WHERE Runid = ? ORDER BY rowid ASC", (runid,))
        train_data = cur.fetchall()
        fetched_data['train'] = (column_names, train_data)
        cur.execute(f"PRAGMA table_info(simulator_valid_{runid})")
        columns_info = cur.fetchall()
        column_names = [info[1] for info in columns_info if info[1] != 'Runid']
        cur.execute(f"SELECT * FROM simulator_valid_{runid} WHERE Runid = ? ORDER BY rowid ASC", (runid,))
        valid_data = cur.fetchall()
        fetched_data['valid'] = (column_names, valid_data)
        con.close()
        return fetched_data



############## data sets creation
def pad_tensor(img):
  target_shape = (256, 256, 256)
  if img.shape != target_shape:
    pad_x = (target_shape[0] - img.shape[0]) // 2
    pad_y = (target_shape[1] - img.shape[1]) // 2
    pad_z = (target_shape[2] - img.shape[2]) // 2
    return np.pad(img, ((pad_x, pad_x), (pad_y, pad_y), (pad_z, pad_z)), mode='constant')
  else:
    return img

def normalize(data):
    normalized_data = (data - np.min(data)) / (np.max(data) - np.min(data))
    return normalized_data


def upload_dataframe_to_db(filepath, db_file, table_name):
    dataframe = pd.read_csv(filepath)
    conn = sqlite3.connect(db_file)
    cur = conn.cursor()
    
    for index, row in dataframe.iterrows():
        image_columns = [col for col in dataframe.columns.tolist()]
        image_paths = [row[col] for col in image_columns]
        normalized_images = []
        c = 0
        for image_path in image_paths:
            image_data = nib.load(os.path.dirname(filepath)+image_path).get_fdata(dtype=np.float32)
            if image_columns[c] in ['labels','images']:
                normalized_image = pad_tensor(normalize(image_data))
            else:
                normalized_image = pad_tensor(image_data)
            normalized_images.append(normalized_image)
            c+=1
        insert_values = [sqlite3.Binary(zlib.compress(image.tobytes())) for image in normalized_images]

        cur.execute(
            f"INSERT INTO {table_name} ({', '.join(image_columns)}) VALUES ({', '.join(['?'] * len(image_columns))})",
            insert_values
        )
    conn.commit()
    conn.close()



def create_tables(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Table for id_token, refresh_token, last_refreshed, etc.
    c.execute('''CREATE TABLE IF NOT EXISTS auth_tokens (
                    id INTEGER PRIMARY KEY,
                    id_token TEXT,
                    refresh_token TEXT,
                    last_refreshed TIMESTAMP
                  )''')

    # Another table for simulator status
    c.execute('''CREATE TABLE IF NOT EXISTS simulator_status (
                    Run_id INTEGER PRIMARY KEY,
                    Status INTEGER CHECK(Status IN (0, 1))
                  )''')

        # Another table for simulator status
    c.execute('''CREATE TABLE IF NOT EXISTS datasets (
                    Name TEXT,
                    Description TEXT
                  )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS pathfix (
                    path TEXT
                  )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS models (
                        Runid INTEGER PRIMARY KEY,
                        Model_data BLOB DEFAULT NULL,
                        Loss REAL DEFAULT NULL
                    )''')

    c.execute("DELETE FROM auth_tokens")
    c.execute("DELETE FROM simulator_status")


    c.execute("PRAGMA database_list")
    print("Settin up database")
    print(c.fetchall())
    conn.commit()
    conn.close()


def get_path(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM pathfix")
    filepaths = c.fetchall()
    print(filepaths)
    if len(filepaths) > 0:
         return filepaths[0][0]
    return 0

def put_path(db, path):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''INSERT INTO pathfix (path ) VALUES (? )''', (path,))
    conn.commit()
    conn.close()


    


#dataset creation
def create_dataset(db,tablename, description):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM datasets WHERE Name=?", (tablename,))
    if c.fetchone() is None:
        print(tablename,description)
        c.execute('''INSERT INTO datasets (Name, Description) VALUES (?, ?)''', (tablename,description,))
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False

def create_blob_table(db,table_name, columns):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join([f'{column} BLOB' for column in columns])})"
    cursor.execute(create_table_sql)
    conn.commit()
    conn.close()

def get_table_info(db):
    table_info_list = []
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # Fetch table names from the 'datasets' table
        c.execute("SELECT rowid, Name, Description FROM datasets")
        tables = c.fetchall()

        for table in tables:
            row_id, name, description = table
            table_info = {
                "ID": row_id,
                "Name": name,
                "Description": description,
                "Total_Datasets": None,
                "Image_Types": None
            }

            # Get the number of rows (datasets)
            c.execute(f"SELECT COUNT(*) FROM {name}")
            num_rows = c.fetchone()[0]
            table_info["Total_Datasets"] = num_rows

            # Get the number of columns (image types)
            c.execute(f"PRAGMA table_info({name})")
            columns = c.fetchall()
            num_columns = len(columns)
            table_info["Image_Types"] = num_columns

            table_info_list.append(table_info)

    except sqlite3.Error as e:
        print("Error reading database:", e)

    finally:
        if conn:
            conn.close()

    return table_info_list


def get_dataset_columns(db):
    dataset_columns = {}
    try:
        conn = sqlite3.connect(db)
        c = conn.cursor()

        # Fetch table names from the 'datasets' table
        c.execute("SELECT Name FROM datasets")
        tables = c.fetchall()

        for table in tables:
            name = table[0]

            # Get the columns (image types) associated with the dataset
            c.execute(f"PRAGMA table_info({name})")
            columns = c.fetchall()
            column_names = [column[1] for column in columns]

            dataset_columns[name] = column_names

    except sqlite3.Error as e:
        print("Error reading database:", e)

    finally:
        if conn:
            conn.close()

    return dataset_columns


#logout functionalit

def remove_tokens(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("DELETE FROM auth_tokens")
    conn.commit()
    conn.close()

#functions for updating authentication tokens

def get_tokens(db,url):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM auth_tokens")
    fa = c.fetchone()
    if fa is not None:
        last_refreshed_str=fa[3]
        last_refreshed = datetime.strptime(last_refreshed_str, '%Y-%m-%d %H:%M:%S.%f')
        current_time = datetime.now()
        time_diff = current_time - last_refreshed
        minutes_diff = time_diff.total_seconds() / 60
        if 55 < minutes_diff < 60:
            refresh_token = fa[2]
            data =  {
                "request": "REFRESH",
                "REFRESH_TOKEN": refresh_token
            }
            json_data = json.dumps(data)
            headers = {'Content-Type': 'application/json'}
            ref = requests.post(url+'/login', data=json_data, headers=headers).json()
            c.execute('''UPDATE auth_tokens 
                 SET id_token = ?, refresh_token = ?, last_refreshed = ?''', 
                 (ref['body']['AuthenticationResult']['IdToken'], refresh_token, datetime.now()))
            conn.commit()
            conn.close()
            return ref['body']['AuthenticationResult']['IdToken']

        elif minutes_diff>=60:
            return False
        else:
            return fa[1]
    else:
        return False


def update_auth_tokens( db, id_token, refresh_token, last_refreshed):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    # Update the only row in the auth_tokens table
    c.execute('''UPDATE auth_tokens 
                 SET id = ?,id_token = ?, refresh_token = ?, last_refreshed = ?''', 
                 (1,id_token, refresh_token, last_refreshed))

    conn.commit()
    conn.close()

def save_auth_tokens(db, id_token, refresh_token):
    last_refreshed = datetime.now()
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''INSERT INTO auth_tokens (id, id_token, refresh_token, last_refreshed) 
                 VALUES (?, ?, ?, ?)''', (1, id_token, refresh_token, last_refreshed))
    conn.commit()
    conn.close()


#functions to for simulation status

def save_simulation_status(db,run_id):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT * FROM simulator_status WHERE Run_id=?", (run_id,))
    row = c.fetchone()
    if row is None:
        c.execute('''INSERT INTO simulator_status (Run_id, Status) 
                     VALUES (?, ?)''', (run_id, 0))
    conn.commit()
    conn.close()

def get_simulation_status(db, run_id):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute("SELECT Status FROM simulator_status WHERE Run_id=?", (run_id,))
    row = c.fetchone()
    conn.close()
    return row[0]


def update_simulator_status(db, run_id, status):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    c.execute('''INSERT INTO simulator_status (Run_id, Status) 
                 VALUES (?, ?)''', (run_id, status))
    conn.commit()
    conn.close()

