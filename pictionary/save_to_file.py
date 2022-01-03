import pickle
import numpy as np
from .models import DrawingTrain, DrawingTest


def save_to_file(model, file):
    dataset = model.objects.all().values_list('category', 'picture').order_by('id')
    dataset = np.array(dataset)
    dataset = dataset.astype('object')

    for img in dataset:
        img[1] = pickle.loads(img[1])

    np.save(file, dataset)
    print("{} modified".format(file))


save_to_file(DrawingTrain, 'train.npy')
save_to_file(DrawingTest, 'test.npy')
