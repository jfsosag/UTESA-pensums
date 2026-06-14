from django.core.management.base import BaseCommand
from django.utils.text import slugify
from pensums.models import Recinto, Carrera

CARRERAS_POR_RECINTO = {
    "Recinto Santiago": [
        "Administración de Empresas",
        "Administración de Empresas Turísticas y Hoteleras",
        "Contaduría Pública",
        "Mercadeo",
        "Arquitectura",
        "Ingeniería Civil",
        "Ingeniería Eléctrica",
        "Ingeniería Electrónica",
        "Ingeniería Industrial",
        "Ingeniería Mecánica",
        "Comunicación Social",
        "Derecho",
        "Educación",
        "Lenguas Extranjeras",
        "Psicología",
        "Bioanálisis",
        "Enfermería",
        "Fármaco-Bioquímica",
        "Medicina",
        "Odontología",
        "Veterinaria y Zootecnia",
        "Optometría",
        "Nutrición Humana y Dietética",
    ],
    "Recinto Santo Domingo": [
        "Administración de Empresas",
        "Administración de Empresas Turísticas y Hoteleras",
        "Contaduría Pública",
        "Mercadeo",
        "Comunicación Social",
        "Derecho",
        "Educación",
        "Lenguas Extranjeras",
        "Psicología",
        "Enfermería",
        "Medicina",
        "Optometría",
        "Nutrición Humana y Dietética",
    ],
    "Recinto Puerto Plata": [
        "Administración de Empresas",
        "Administración de Empresas Turísticas y Hoteleras",
        "Contaduría Pública",
        "Mercadeo",
        "Ingeniería Electrónica",
        "Ingeniería Industrial",
        "Comunicación Social",
        "Derecho",
        "Educación",
        "Psicología",
    ],
}


class Command(BaseCommand):
    help = "Crea las carreras base y las asigna a sus recintos"

    def handle(self, *args, **options):
        for recinto_nombre, carreras_list in CARRERAS_POR_RECINTO.items():
            try:
                recinto = Recinto.objects.get(nombre=recinto_nombre)
            except Recinto.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ✗ Recinto no encontrado: {recinto_nombre}"))
                continue

            creadas = 0
            for nombre in carreras_list:
                slug = slugify(nombre)
                carrera, created = Carrera.objects.get_or_create(
                    slug=slug,
                    defaults={"nombre": nombre},
                )
                if created:
                    creadas += 1
                recinto.carreras.add(carrera)

            total = recinto.carreras.count()
            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {recinto_nombre}: {creadas} nuevas, {total} total"
            ))

        total_carreras = Carrera.objects.count()
        self.stdout.write(self.style.SUCCESS(f"\n✓ Total carreras base: {total_carreras}"))
