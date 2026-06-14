from django.urls import path
from . import views

app_name = "pensums"

urlpatterns = [
    path("", views.InicioView.as_view(), name="inicio"),
    path("recinto/<slug:slug>/", views.RecintoDetailView.as_view(), name="recinto"),
    path("recinto/<slug:recinto_slug>/carrera/<slug:carrera_slug>/", views.CarreraDetailView.as_view(), name="carrera"),
    path("recinto/<slug:recinto_slug>/carrera/<slug:carrera_slug>/materia/<int:pk>/", views.MateriaDetailView.as_view(), name="materia"),
    path("recinto/<slug:recinto_slug>/carrera/<slug:carrera_slug>/materia/<int:pk>/comentar/", views.crear_comentario, name="crear_comentario"),
]
