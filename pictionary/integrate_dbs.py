import pickle
import numpy as np
import psycopg2
from urllib.request import urlretrieve
from pictionary.models import DrawingTrain, DrawingTest, Category
from psycopg2 import Error
from environs import Env
import random

env = Env()
env.read_env()


class QuickDrawDB:
    """
    The class for all operations needed to add QuickDraw dataset to database.

    Constants:
        BASE_URL (str): The base url address to QuickDraw database.
        LABELS_PATH (str): The local path to tensorflow file with QuickDraw categories.
        IMG_SHAPE (tuple): The QuickDraw image shape.
        FOLDER_PATH (str): The local path to folder with all .npy files.
        TRANSLATIONS_FILE (str): The local path to file with labels and theirs translations from English to Polish.
    """
    BASE_URL = "https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap"
    LABELS_PATH = "picked.txt"
    IMG_SHAPE = (28, 28, 1)
    FOLDER_PATH = ".quickdraw/"
    TRANSLATIONS_FILE = "quick_draw_translated.txt"
    LIMIT = 70000
    SPLIT_PROPORTION = 2/3

    def get_translations(self):
        """
        The function to create dictionary with labels and theirs translations from English to Polish.
        """
        with open(self.TRANSLATIONS_FILE, "r") as f:
            labels = f.read().splitlines()
            translations = {
                label.split('\t')[0]: label.split('\t')[1]
                for label in labels
            }
        return translations

    def get_labels_urls(self, translations):
        """
        The function to create dictionary with urls to every .npy file.
        """
        with open(self.LABELS_PATH, "r") as file:
            labels = file.read().splitlines()
            urls = {
                label: "{}/{}.npy".format(self.BASE_URL, label.replace(" ", "%20"))
                for label in labels
                if label in translations.keys()
            }
        return urls

    def populate(self):
        """
        The function to add QuickDraw dataset to database.
        """
        translations = self.get_translations()
        urls = self.get_labels_urls(translations)
        train_add = []
        test_add = []
        for k, v in urls.items():
            print(k + " " + v)
            urlretrieve(v, self.FOLDER_PATH + k.replace(" ", "_") + ".npy")
            file = np.load(self.FOLDER_PATH + k.replace(" ", "_") + ".npy",
                           encoding='latin1', allow_pickle=True)
            category = Category.objects.create(name=translations[k])
            for i, np_image in enumerate(file):
                np_bytes = pickle.dumps(np_image.reshape(self.IMG_SHAPE))
                if i <= (self.LIMIT*self.SPLIT_PROPORTION):
                    train_add.append(DrawingTrain(category=category, picture=np_bytes))
                elif (self.LIMIT*self.SPLIT_PROPORTION) < i <= self.LIMIT:
                    test_add.append(DrawingTest(category=category, picture=np_bytes))
                else:
                    break
            del file
        random.shuffle(train_add)
        DrawingTrain.objects.bulk_create(train_add)
        train_add.clear()
        random.shuffle(test_add)
        DrawingTest.objects.bulk_create(test_add)
        test_add.clear()


class HerokuDB:
    """
    The class for all operations needed to add Heroku dataset to database.
    """
    USER = env.str("USER")
    PASSWORD = env.str("PASSWORD")
    HOST = env.str("HOST")
    PORT = 5432
    DATABASE = env.str("DATABASE")
    SPLIT_PROPORTION = 2 / 3

    def connect(self):
        """
        The function to connect to PostgreSQL Heroku database.
        """
        try:
            connection = psycopg2.connect(user=self.USER,
                                          password=self.PASSWORD,
                                          host=self.HOST,
                                          port=self.PORT,
                                          database=self.DATABASE)
            return connection.cursor(), connection
        except (Exception, Error) as error:
            print("Error while connecting to PostgreSQL", error)

    def populate(self, cursor, connection):
        """
        The function to add Heroku dataset to database.
        """
        drawing_table = "SELECT b.id, b.picture, a.name FROM pictionary_db_category a " \
                        "INNER JOIN pictionary_db_drawing b on a.id = b.category_id"
        cursor.execute(drawing_table)
        drawing_data = cursor.fetchall()

        train_add = []
        test_add = []
        db_len = len(drawing_data)
        for i, drawing in enumerate(drawing_data):
            print(drawing[2])
            if not Category.objects.filter(name=drawing[2]).exists():
                category = Category.objects.create(name=drawing[2])
            else:
                category = Category.objects.get(name=drawing[2])
            img_data = drawing[1].split('data:image/png;base64,')[1]
            if i <= (db_len*self.SPLIT_PROPORTION):
                train_add.append(DrawingTrain(category=category, picture=bytes(img_data, 'utf-8')))
            else:
                test_add.append(DrawingTest(category=category, picture=bytes(img_data, 'utf-8')))

        random.shuffle(train_add)
        DrawingTrain.objects.bulk_create(train_add)
        train_add.clear()

        random.shuffle(test_add)
        DrawingTest.objects.bulk_create(test_add)
        test_add.clear()

        cursor.close()
        connection.close()


QD = QuickDrawDB()
QD.populate()

HD = HerokuDB()
c1, c2 = HD.connect()
HD.populate(c1, c2)
