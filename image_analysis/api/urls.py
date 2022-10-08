from django.urls import path
from . import views

urlpatterns = [
    path("query/<path:image_url>", views.endpoint_view),
    path("add", views.upload),
    path("upload", views.post_data),
    path("createdata", views.create_data_set),
    path("createmodel/<path:model_name>", views.create_model),
]
