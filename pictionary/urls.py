from django.urls import path
from .views import (HomePageView,
                    CategoryPageView,
                    PaintAppView,
                    guess,
                    random_temp,
                    delete_temp,
                    ResultPageView)

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('kategoria/', CategoryPageView.as_view(), name='category'),
    path('rysuj/', PaintAppView.as_view(), name='paint'),
    path('random/', random_temp, name='random_temp'),
    path('usun/', delete_temp, name='delete_category'),
    path('zgaduj/', guess, name='guess'),
    path('koniec/', ResultPageView.as_view(), name='result'),
]
