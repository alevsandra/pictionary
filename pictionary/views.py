import base64
import io
import numpy as np
from PIL import Image
from django.views.generic import TemplateView
from .models import Category, TempCategory
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.http import HttpResponse
from django.urls import reverse
import pickle
import torch
import simplejson
from datetime import datetime

points_number = 0

class HomePageView(TemplateView):
    template_name = 'home.html'


class CategoryPageView(TemplateView):
    template_name = 'category.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = context['new_category'] = TempCategory.objects.get(
                pk=min(TempCategory.objects.filter().values_list('pk', flat=True)))
        return context


class PaintAppView(TemplateView):
    template_name = 'paint.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['model'] = TempCategory.objects.all()
        context['category'] = TempCategory.objects.get(
                pk=min(TempCategory.objects.filter().values_list('pk', flat=True)))
        return context


class ResultPageView(TemplateView):
    template_name = 'result.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['points'] = points_number
        return context


@csrf_protect
def delete_temp(request):
    if request.method == 'POST':
        TempCategory.objects.get(pk=min(TempCategory.objects.filter().values_list('pk', flat=True))).delete()
        if TempCategory.objects.exists():
            json_dump = simplejson.dumps({'url': reverse('category')})
        else:
            json_dump = simplejson.dumps({'url': reverse('result')})
        return HttpResponse(json_dump, content_type='application/json')


@csrf_exempt
def guess(request):
    if request.method == 'POST':
        start_time = datetime.now()
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        image = (request.POST['picture']).split('data:image/png;base64,')[1]
        img = reformat_image(image)
        model = pickle.load(open("cnn_model.sav", "rb"))
        output = model(torch.tensor(img).view(-1, 1, 28, 28).to(device))[0]
        prediction = output.argmax()
        category = Category.objects.get(pk=prediction+1)
        global points_number
        if category.name == TempCategory.objects.get(
                pk=min(TempCategory.objects.filter().values_list('pk', flat=True))).name:
            points_number += 1
        json_dump = simplejson.dumps({'category': category.name})
        print("Duration: {}".format(datetime.now() - start_time))
        return HttpResponse(json_dump, content_type='application/json')


@csrf_exempt
def random_temp(request):
    if request.method == 'POST':
        # adding randomly to model TempCategory 5 categories
        while len(TempCategory.objects.all()) < 5:
            s = Category.objects.random()
            if not TempCategory.objects.filter(name=s).exists():
                TempCategory.objects.create(name=s)

        # picking up the first category with the smallest id
        category_f = TempCategory.objects.get(
            pk=min(TempCategory.objects.filter().values_list('pk', flat=True)))
        # forwarding first category id to request response
        global points_number
        points_number = 0
        json_dump = simplejson.dumps({'pid': category_f.pk})
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

    im.thumbnail((26, 26), Image.ANTIALIAS)

    image_array = np.array(im)
    gray_array = image_array.mean(axis=2).astype(np.float32)
    gray_array = np.pad(gray_array, 1, mode='constant')
    return gray_array / np.max(gray_array)
