from django.db import models


class Drawing(models.Model):
    category = models.CharField(max_length=50)
    picture = models.BinaryField()

    def __str__(self):
        return self.category
