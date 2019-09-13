from django.db import models

class Product(models.Model):
    title = models.CharField(max_length=100)
    brand = models.CharField(max_length=100)
    vendorcode = models.CharField(max_length=100, unique=True)
    price = models.IntegerField(default=0)
    description = models.TextField()

    def __str__(self):
        return self.title

class Pen (models.Model):
    pentypechoise = [
        ('feather', 'перьевая'),
        ('ball', 'шариковая')
    ]

    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name='pendetail')
    color = models.CharField(max_length=50)
    type = models.CharField(max_length=50, choices=pentypechoise)

class Pencil(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name='pencildetail')
    color = models.CharField(max_length=50)
    hardness = models.CharField(max_length=50)

class Paper(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, primary_key=True, related_name='paperdetail')
    format = models.CharField(max_length=50)
    sheets = models.IntegerField(default=0)