from django.db import models
from django.core.exceptions import ValidationError
# Create your models here.


def validate_size(value):
    if value.file.size > 0.4*1024*1024:
        raise ValidationError('This file is bigger than 0.7mb!')


def upload_location(instance, filename):
    return 'first_page/%s/%s' % (instance.title, filename)


def upload_banner(instance, filename):
    return 'banner/%s/%s' % (instance.title, filename)


class FirstPage(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(unique=True, max_length=150)
    image = models.ImageField(upload_to=upload_location, validators=[validate_size, ])
    meta_description = models.CharField(max_length=160)
    meta_keywords = models.CharField(max_length=160)

    def __str__(self):
        return self.title


class Banner(models.Model):
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to=upload_banner, validators=[validate_size, ])
    href = models.URLField(blank=True, null=True)
    new_window = models.BooleanField(default=False)
    big_banner = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def tag_active(self):
        return 'Active' if self.active else 'No Active'