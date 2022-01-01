from django.contrib import admin
from .models import DrawingTrain, DrawingTest, Category

admin.site.register(DrawingTrain)
admin.site.register(DrawingTest)
admin.site.register(Category)
