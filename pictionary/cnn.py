import numpy as np
import pickle
from torch.utils.data import random_split
from .models import Drawing
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from tqdm import tqdm
from datetime import datetime


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()

        self.conv1 = torch.nn.Conv2d(1, 64, (15, 15), stride=3)
        self.conv2 = torch.nn.Conv2d(64, 128, (5, 5), stride=1)
        self.conv3 = torch.nn.Conv2d(128, 256, (3, 3), stride=1, padding=1)
        self.conv4 = torch.nn.Conv2d(256, 256, (3, 3), stride=1, padding=1)
        self.conv5 = torch.nn.Conv2d(256, 256, (3, 3), stride=1, padding=1)
        self.conv6 = torch.nn.Conv2d(256, 512, (7, 7), stride=1, padding=0)
        self.conv7 = torch.nn.Conv2d(512, 512, (1, 1), stride=1, padding=0)

        self.linear1 = torch.nn.Linear(512, 256)
        self.linear2 = torch.nn.Linear(256, 50)

    def forward(self, x, feature=False):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, (3, 3), stride=2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, (3, 3), stride=2)
        x = F.relu(self.conv3(x))
        x = F.relu(self.conv4(x))
        x = F.relu(self.conv5(x))
        x = F.max_pool2d(x, (3, 3), stride=2)
        if self.training:
            x = F.dropout2d(F.relu(self.conv6(x)))
            x = F.dropout2d(F.relu(self.conv7(x)))
        else:
            x = F.relu(self.conv6(x))
            x = F.relu(self.conv7(x))
        x = x.view(-1, 512)

        if feature:
            return F.relu(self.linear1(x))
        else:
            return self.linear2(F.relu(self.linear1(x)))


class MyModel:
    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.SPLIT_PROPORTION = 2 / 3
        self.train_X = []
        self.train_y = []
        self.test_X = []
        self.test_y = []
        self.BATCH_SIZE = 100
        self.EPOCHS = 50
        self.cnn = CNN().to(self.device)

    @staticmethod
    def img_to_arr(drawing):
        return pickle.loads(drawing.picture)

    def create_X_y(self, dataset):
        X = []
        y = []

        for drawing in dataset:
            X.append(self.img_to_arr(drawing))
            y.append(drawing.category.id)

        X = np.array(X)
        X = X/255

        print("X shape: {}\ny shape: {}".format(X.shape, len(y)))
        return torch.Tensor(X), torch.Tensor(y)

    def create_train_test(self):
        dataset_length = Drawing.objects.count()
        train_samples_len = int(dataset_length * self.SPLIT_PROPORTION)
        test_samples_len = dataset_length - train_samples_len

        train_dataset, test_dataset = random_split(Drawing.objects.all(), [train_samples_len, test_samples_len])
        print("Train len: {}\nTest len: {}".format(train_samples_len, test_samples_len))

        self.train_X, self.train_y = self.create_X_y(train_dataset)
        self.test_X, self.test_y = self.create_X_y(test_dataset)

    def train(self):
        optimizer = optim.Adam(self.cnn.parameters(), lr=0.01)
        loss_function = nn.MSELoss()

        for epoch in range(self.EPOCHS):
            for i in tqdm(range(0, len(self.train_X), self.BATCH_SIZE)):
                batch_X = self.train_X[i:i+self.BATCH_SIZE]
                batch_y = self.train_y[i:i+self.BATCH_SIZE]

                batch_X, batch_y = batch_X.to(self.device), batch_y.to(self.device)

                self.cnn.zero_grad()
                outputs = self.cnn(batch_X)
                loss = loss_function(outputs, batch_y)
                loss.backword()
                optimizer.step()
            print("Epoch: {} Loss: {}".format(epoch, loss))

    def test(self):
        correct = 0
        total = 0
        with torch.no_grad():
            for i in tqdm(range(len(self.test_X))):
                real_class = torch.argmax(self.test_y[i]).to(self.device)
                net_out = self.cnn(self.test_X[i].to(self.device))[0]
                predicted_class = torch.argmax(net_out)
                if predicted_class == real_class:
                    correct += 1
                total += 1
        print("Accuracy: {}".format(round(correct/total, 3)))


start_time = datetime.now()
NN = MyModel()
NN.create_train_test()
print("Duration: {}".format(datetime.now() - start_time))
NN.train()
NN.test()
print("Duration: {}".format(datetime.now() - start_time))
