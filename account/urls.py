from django.urls import path
from  django.conf.urls import url
from .views import *


app_name = 'accounts'

urlpatterns =[
    url(r'^$', view=create_user, name='create_user'),
    url(r'^auth_view/$',view=auth_view, name='auth_view'),
    url(r'^logged_in/$',view=logged_in, name='logged_in'),
    url(r'^logout/$',view=logout, name='log_out'),

    # dashboard urls
    path('user-list/', UserListView.as_view(), name='dash_list'),
    path('user-update/<int:pk>/', UserUpdateView.as_view(), name='dash_update'),
    path('user-delete/<int:pk>/', view=delete_user, name='dash_delete'),
    path('user-create/', UserCreateView.as_view(), name='dash_create'),


]
