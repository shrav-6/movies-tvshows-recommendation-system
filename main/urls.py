from django.urls import path 
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
#import views from the current directory
from . import views

urlpatterns = [
    path("",views.home, name="home"),
    path("movies/",views.movies,name='movies'),
]
urlpatterns += staticfiles_urlpatterns()