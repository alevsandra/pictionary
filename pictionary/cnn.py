import numpy as np
import pickle
from torch.utils.data import random_split
from .models import Drawing


class MyModel:
    def __init__(self):
        self.SPLIT_PROPORTION = 2 / 3
        self.train_X = []
        self.train_y = []
        self.test_X = []
        self.test_y = []

    @staticmethod
    def img_to_arr(drawing):
        return pickle.loads(drawing.picture)

    def create_X_y(self, dataset):
        X = []
        y = []

        for drawing in dataset:
            X.append(self.img_to_arr(drawing))
            y.append(drawing.category)

        X = np.array(X)

        print("X shape: {}\ny shape: {}".format(np.array(X).shape, len(y)))
        return X, y

    def create_train_test(self):
        dataset_length = Drawing.objects.count()
        train_samples_len = int(dataset_length * self.SPLIT_PROPORTION)
        test_samples_len = dataset_length - train_samples_len

        train_dataset, test_dataset = random_split(Drawing.objects.all(), [train_samples_len, test_samples_len])
        print("Train len: {}\nTest len: {}".format(train_samples_len, test_samples_len))

        self.train_X, self.train_y = self.create_X_y(train_dataset)
        self.test_X, self.test_y = self.create_X_y(test_dataset)


NN = MyModel()
NN.create_train_test()
