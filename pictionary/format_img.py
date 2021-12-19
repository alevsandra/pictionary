from PIL import Image
import io
import base64
import pickle
from .models import Drawing
import numpy as np


class MyImage:
    IMG_SIZE = (28, 28)
    MY_CATEGORIES = ['warkocz', 'flet', 'Ziemia', 'góry', 'spódnica',
                     'sukienka', 'ogon', 'macka', 'kod kreskowy', 'koza']

    def reformat_image(self):
        to_update = []
        for category in self.MY_CATEGORIES:
            print(category, end=": ")
            image_list = Drawing.objects.filter(category=category)

            for img in image_list:
                np_bytes = base64.b64decode(img.picture)
                i = io.BytesIO(np_bytes)

                im = Image.open(i)

                image_array = np.array(im)

                col_sum = np.where(np.sum(image_array, axis=0) > 0)
                row_sum = np.where(np.sum(image_array, axis=1) > 0)
                y1, y2 = row_sum[0][0], row_sum[0][-1]
                x1, x2 = col_sum[0][0], col_sum[0][-1]

                if x2 - x1 > y2 - y1:
                    middle = y1 + (y2 - y1) / 2
                    y1 -= ((x2 - x1) - (y2 - y1)) / 2
                    y2 = middle + (x2 - x1) / 2
                else:
                    middle = x1 + (x2 - x1) / 2
                    x1 -= ((y2 - y1) - (x2 - x1)) / 2
                    x2 = middle + (y2 - y1) / 2

                im = im.crop((x1, y1, x2, y2))

                im.thumbnail(self.IMG_SIZE, Image.ANTIALIAS)

                image_array = np.array(im)
                np_bytes = pickle.dumps(image_array)
                np_base64 = base64.b64encode(np_bytes)

                img.picture = np_base64
                to_update.append(img)
            Drawing.objects.bulk_update(to_update, ['picture'])  # 3411666
            print("Updated")
            to_update.clear()


MI = MyImage()
MI.reformat_image()
