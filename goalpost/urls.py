from . import views
from django.urls import path

app_name = 'project_bracket'

urlpatterns = [
    path("", views.index, name="index")
]