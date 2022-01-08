import base64
import io
import numpy as np
from PIL import Image

from django.views.generic import TemplateView
from .models import Category
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
import pickle
import torch
import simplejson
from datetime import datetime


class HomePageView(TemplateView):
    template_name = 'home.html'


class CategoryPageView(TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.random()
        return context


class PaintAppView(TemplateView):
    template_name = 'paint.html'


@csrf_exempt
def guess(request):
    if request.method == 'POST':
        start_time = datetime.now()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image = (request.POST['picture']).split('data:image/png;base64,')[1]
        img = reformat_image(image)
        model = pickle.load(open("cnn_model.sav", "rb"))
        print(model)
        output = model(torch.tensor(img).view(-1, 1, 28, 28).to(device))[0]
        prediction = torch.argmax(output)
        category = Category.objects.get(pk=prediction+1)
        json_dump = simplejson.dumps({'category': category.name})
        print("Duration: {}".format(datetime.now() - start_time))
        return HttpResponse(json_dump, content_type='application/json')


def reformat_image(img):
    np_bytes = base64.b64decode(img)
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

    im.thumbnail((28, 28), Image.ANTIALIAS)

    image_array = np.array(im)
    gray_array = image_array.mean(axis=2).astype(np.float32)
    return gray_array / 255
