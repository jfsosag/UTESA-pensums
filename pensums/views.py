from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.template.loader import render_to_string
from .models import Recinto, Carrera, Materia, Comentario


class InicioView(ListView):
    model = Recinto
    template_name = "pensums/inicio.html"
    context_object_name = "recintos"

    def get_queryset(self):
        return Recinto.objects.filter(activo=True).prefetch_related("carreras")


class RecintoDetailView(DetailView):
    model = Recinto
    template_name = "pensums/recinto.html"
    context_object_name = "recinto"
    slug_field = "slug"
    slug_url_kwarg = "slug"


class CarreraDetailView(DetailView):
    model = Carrera
    template_name = "pensums/carrera.html"
    context_object_name = "carrera"
    slug_field = "slug"
    slug_url_kwarg = "carrera_slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recinto"] = get_object_or_404(Recinto, slug=self.kwargs["recinto_slug"])
        materias = Materia.objects.filter(
            carrera=self.object, activo=True
        ).order_by("semestre", "codigo")
        semestres = {}
        for m in materias:
            semestres.setdefault(m.semestre, []).append(m)
        context["semestres"] = dict(sorted(semestres.items()))
        context["total_creditos"] = self.object.total_creditos()
        return context


class MateriaDetailView(DetailView):
    model = Materia
    template_name = "pensums/materia.html"
    context_object_name = "materia"
    pk_url_kwarg = "pk"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recinto"] = get_object_or_404(Recinto, slug=self.kwargs["recinto_slug"])
        context["comentarios"] = Comentario.objects.filter(
            materia=self.object, activo=True
        ).order_by("-fecha_creacion")
        return context


def crear_comentario(request, pk, recinto_slug, carrera_slug):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == "POST":
        numero_grupo = request.POST.get("numero_grupo")
        nombre_profesor = request.POST.get("nombre_profesor")
        comentario_texto = request.POST.get("comentario")

        if numero_grupo and nombre_profesor and comentario_texto:
            comentario = Comentario.objects.create(
                materia=materia,
                numero_grupo=int(numero_grupo),
                nombre_profesor=nombre_profesor,
                comentario=comentario_texto,
                activo=False,
            )
            html = render_to_string(
                "pensums/_comentario.html",
                {"comentario": comentario},
                request=request,
            )
            return HttpResponse(html)

    return HttpResponse(status=400)
