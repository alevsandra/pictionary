import base64
import pickle
import numpy as np
import psycopg2
import tensorflow_datasets.public_api as tfds
# from urllib.request import urlretrieve
from translate import Translator
from pictionary.models import Drawing
from psycopg2 import Error
from environs import Env

env = Env()
env.read_env()


class QuickDrawDB:
    BASE_URL = "https://storage.googleapis.com/quickdraw_dataset/full/numpy_bitmap"
    LABELS_PATH = tfds.core.tfds_path("image_classification/quickdraw_labels.txt")
    IMG_SHAPE = (28, 28, 1)
    FOLDER_PATH = ".quickdraw/"

    def get_labels(self):
        with open(self.LABELS_PATH, "r") as file:
            labels = file.read().splitlines()
            urls = {
                label: "{}/{}.npy".format(self.BASE_URL, label.replace(" ", "%20"))
                for label in labels
            }

        for k, v in urls.items():
            print(k + " " + v)
            # urlretrieve(v, self.FOLDER_PATH + k.replace(" ", "_") + ".npy")
            file = np.load(self.FOLDER_PATH + k.replace(" ", "_") + ".npy",
                           encoding='latin1', allow_pickle=True)
            translator = Translator(to_lang="pl")
            for i, np_image in enumerate(file):
                np_bytes = pickle.dumps(np_image.reshape(self.IMG_SHAPE))
                np_base64 = base64.b64encode(np_bytes)
                d = Drawing(category=translator.translate(k), picture=np_base64)
                d.save()
                print(translator.translate(k))
                break  # only first image
            break  # only first file


class HerokuDB:
    USER = env.str("USER")
    PASSWORD = env.str("PASSWORD")
    HOST = env.str("HOST")
    PORT = 5432
    DATABASE = env.str("DATABASE")

    def connect(self):
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
        drawing_table = "SELECT b.id, b.picture, a.name FROM pictionary_db_category a " \
                        "INNER JOIN pictionary_db_drawing b on a.id = b.category_id"
        cursor.execute(drawing_table)
        drawing_data = cursor.fetchall()

        for drawing in drawing_data:
            print(drawing[2])
            img_data = drawing[1].split('data:image/png;base64,')[1]

            d = Drawing(category=drawing[2], picture=bytes(img_data, 'utf-8'))
            d.save()
            break

        cursor.close()
        connection.close()


HD = HerokuDB()
c1, c2 = HD.connect()
# HD.populate(c1, c2)
