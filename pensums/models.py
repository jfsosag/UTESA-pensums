from django.db import models
from django.utils import timezone
from django.utils.text import slugify


SEMESTRE_CHOICES = [(str(i), f"{i}° Cuatrimestre") for i in range(1, 13)]


class Recinto(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    descripcion = models.TextField(blank=True)
    portada = models.ImageField(upload_to="recintos/portadas/", blank=True, null=True, verbose_name="Portada")
    carreras = models.ManyToManyField(
        "Carrera", blank=True, related_name="recintos",
        verbose_name="Carreras que se ofrecen"
    )
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Recinto"
        verbose_name_plural = "Recintos"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def cantidad_carreras(self):
        return self.carreras.count()


class Carrera(models.Model):
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    codigo = models.CharField(max_length=20, blank=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Carrera"
        verbose_name_plural = "Carreras"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def cantidad_materias(self):
        return self.materias.count()

    def total_creditos(self):
        return self.materias.aggregate(total=models.Sum("creditos"))["total"] or 0


class Materia(models.Model):
    carrera = models.ForeignKey(
        Carrera, on_delete=models.CASCADE, related_name="materias"
    )
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=200)
    creditos = models.PositiveSmallIntegerField(default=0)
    semestre = models.CharField(max_length=2, choices=SEMESTRE_CHOICES)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    prerrequisitos = models.ManyToManyField(
        "self", blank=True, symmetrical=False,
        related_name="materias_prerrequisito_de",
        verbose_name="Pre-requisitos"
    )
    corequisitos = models.ManyToManyField(
        "self", blank=True, symmetrical=False,
        related_name="materias_corequisito_de",
        verbose_name="Co-requisitos"
    )

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ["semestre", "codigo"]
        unique_together = ["carrera", "codigo"]

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

    def lista_prerrequisitos(self):
        return ", ".join(m.codigo for m in self.prerrequisitos.all())

    def lista_corequisitos(self):
        return ", ".join(m.codigo for m in self.corequisitos.all())


class Comentario(models.Model):
    materia = models.ForeignKey(
        Materia, on_delete=models.CASCADE, related_name="comentarios"
    )
    numero_grupo = models.PositiveSmallIntegerField(verbose_name="Número de grupo")
    nombre_profesor = models.CharField(
        max_length=200, verbose_name="Nombre del profesor"
    )
    comentario = models.TextField(verbose_name="Comentario")
    fecha_creacion = models.DateTimeField(default=timezone.now)
    activo = models.BooleanField(default=True, verbose_name="Activo (moderado)")

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Comentario en {self.materia.codigo} por {self.nombre_profesor}"
