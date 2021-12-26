from django.test import TestCase
from .models import Drawing, Category
import pickle
import matplotlib.pyplot as plt


class DBIntegrationTest(TestCase):
    QUICK_DRAW_IMAGE = Drawing.objects.get(pk=1).picture
    MY_IMAGE = Drawing.objects.get(pk=2800080).picture

    def setUp(self):
        c1 = Category.objects.create(name='korona')
        c2 = Category.objects.create(name='macka')
        Drawing.objects.create(category=c1, picture=self.QUICK_DRAW_IMAGE)
        Drawing.objects.create(category=c2, picture=self.MY_IMAGE)

    def test_bytes_decode(self):
        for drawing in Drawing.objects.all():
            np_array = pickle.loads(drawing.picture)
            self.assertEqual(np_array.shape[0], 28)
            self.assertEqual(np_array.shape[1], 28)
            self.assertEqual(len(np_array.shape), 2)
            plt.imshow(np_array, cmap='gray')
            plt.show()
