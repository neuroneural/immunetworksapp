import sqlite3
import torch
import zlib
import numpy as np

class Scanloader(torch.utils.data.Dataset):
    def __init__(self, db_file, table_name, label_type='GWlabels', num_cubes=1):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.label_type = label_type
        self.table_name = table_name
        self.query = f"SELECT images, {self.label_type} FROM {self.table_name}"
        self.cursor.execute(self.query)
        self.data = self.cursor.fetchall()
        self.len = len(self.data)
        self.num_cubes = num_cubes
        self.indexes = []
    
    def __len__(self):
        return self.len
    
    def divide_into_sub_cubes(self, tensor):
        sub_cubes = []
        sub_cube_size = tensor.shape[0] // self.num_cubes  # Assuming the tensor is a cube

        for i in range(self.num_cubes):
            for j in range(self.num_cubes):
                for k in range(self.num_cubes):
                    sub_cube = tensor[
                        i * sub_cube_size: (i + 1) * sub_cube_size,
                        j * sub_cube_size: (j + 1) * sub_cube_size,
                        k * sub_cube_size: (k + 1) * sub_cube_size
                    ].clone()
                    sub_cubes.append(sub_cube)

        sub_cubes = torch.stack(sub_cubes, 0)
        return sub_cubes
    
    def __getitem__(self, idx):
        sample = self.data[idx]
        image = zlib.decompress(sample[0])
        image_tensor = torch.from_numpy(np.copy(np.frombuffer(image, dtype=np.float32)).reshape((256, 256, 256)))
        label = zlib.decompress(sample[1])
        label_tensor = torch.from_numpy(np.copy(np.frombuffer(label, dtype=np.float32)).reshape((256, 256, 256)))
        if idx in self.indexes:  # Check if dataset is inference dataset
            print('test')
            return image_tensor.to(self.device), label_tensor.to(self.device)  # Return full image and label tensors
        
        # Divide into subcubes for training and validation datasets
        image_subcubes = self.divide_into_sub_cubes(image_tensor.to(self.device))
        label_subcubes = self.divide_into_sub_cubes(label_tensor.to(self.device))
        
        return image_subcubes, label_subcubes
    
    def split_dataset(self):
        train_size = int(0.7 * self.len)
        valid_size = int(0.2 * self.len)
        train_data, valid_data, infer_data = torch.utils.data.random_split(self, [train_size, valid_size, self.len - train_size - valid_size])
        self.indexes = infer_data.indices
        return train_data, valid_data, infer_data
    
    def get_loaders(self, batch_size=1, shuffle=False):
        train_data, valid_data, infer_data = self.split_dataset()
        train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, shuffle=True)
        valid_loader = torch.utils.data.DataLoader(valid_data, batch_size=batch_size, shuffle=False)
        infer_loader = torch.utils.data.DataLoader(infer_data, batch_size=1, shuffle=False)
        
        return train_loader, valid_loader, infer_loader
