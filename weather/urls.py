from django.urls import path

from . import views

urlpatterns = [
    path(route='', view=views.IndexView.as_view() ,name='index'),
    path(route='add/', view=views.IndexView.as_view() ,name='add'),
    path(route='delete/', view=views.CityDeleteView.as_view() ,name='delete'),
]
