from django.urls import path, include, re_path

urlpatterns =[
    path(r"^/$", "inventory_manager.views.homepage",name='inventory'),

]