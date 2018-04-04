from  django.conf.urls import url
from .views import *
urlpatterns =(
    url(r'^$', view=create_user, name='create_user'),
    url(r'^log_in/$', view=log_in, name='log_in'),
    url(r'^auth_view/$',view=auth_view, name='auth_view'),
    url(r'^logged_in/$',view=logged_in, name='logged_in'),
    url(r'^logout/$',view=logout, name='log_out'),

)
