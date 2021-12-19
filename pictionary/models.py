from random import randint
from django.db import models


class CategoryManager(models.Manager):
    def random(self):
        count = self.all().count()
        random_index = randint(1, count)
        return Category.objects.get(pk=random_index)


class Category(models.Model):
    name = models.CharField(max_length=50)
    objects = CategoryManager()

    def __str__(self):
        return self.name


class Drawing(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
    )
    picture = models.BinaryField()

    def __str__(self):
        return self.category
