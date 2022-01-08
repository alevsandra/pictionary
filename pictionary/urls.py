from django.urls import path
from .views import HomePageView, CategoryPageView, PaintAppView, guess

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('kategoria/', CategoryPageView.as_view(), name='category'),
    path('rysuj/', PaintAppView.as_view(), name='paint'),
    path('zgaduj/', guess, name='guess'),
]
