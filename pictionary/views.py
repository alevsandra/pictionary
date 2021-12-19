from django.views.generic import TemplateView
from .models import Category


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
