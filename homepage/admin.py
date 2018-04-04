from django.contrib import admin
from .models import Banner, FirstPage
# Register your models here.


@admin.register(FirstPage)
class FirstPageAdmin(admin.ModelAdmin):
    list_display = ['title', 'active']


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'active', ]
