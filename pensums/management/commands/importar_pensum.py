"""
Management command para importar pensum desde CSV.

Uso:
    python manage.py importar_pensum --carrera <carrera_id> --archivo <ruta.csv>

Formato CSV esperado:
    codigo,nombre,creditos,semestre
    MAT101,Matemática I,4,1
    ...
"""

import csv
from django.core.management.base import BaseCommand, CommandError
from pensums.models import Carrera, Materia


class Command(BaseCommand):
    help = "Importa materias desde un archivo CSV a una carrera específica"

    def add_arguments(self, parser):
        parser.add_argument(
            "--carrera",
            type=int,
            required=True,
            help="ID de la carrera a la que importar las materias",
        )
        parser.add_argument(
            "--archivo",
            type=str,
            required=True,
            help="Ruta al archivo CSV con columnas: codigo,nombre,creditos,semestre",
        )

    def handle(self, *args, **options):
        carrera_id = options["carrera"]
        archivo = options["archivo"]

        try:
            carrera = Carrera.objects.get(id=carrera_id)
        except Carrera.DoesNotExist:
            raise CommandError(f"No existe una carrera con ID {carrera_id}")

        columnas_requeridas = {"codigo", "nombre", "creditos", "semestre"}

        creadas = 0
        actualizadas = 0
        errores = []

        with open(archivo, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                raise CommandError("El archivo CSV está vacío o no tiene cabeceras")

            columnas_csv = set(reader.fieldnames)
            if not columnas_requeridas.issubset(columnas_csv):
                faltan = columnas_requeridas - columnas_csv
                raise CommandError(
                    f"Faltan columnas requeridas en el CSV: {', '.join(sorted(faltan))}"
                )

            for fila_num, row in enumerate(reader, start=2):
                try:
                    codigo = row["codigo"].strip()
                    nombre = row["nombre"].strip()
                    creditos = int(row["creditos"])
                    semestre = str(int(row["semestre"]))

                    if semestre not in [str(i) for i in range(1, 13)]:
                        errores.append(
                            f"Fila {fila_num}: semestre inválido '{row['semestre']}' (debe ser 1-12)"
                        )
                        continue

                    materia, created = Materia.objects.update_or_create(
                        carrera=carrera,
                        codigo=codigo,
                        defaults={
                            "nombre": nombre,
                            "creditos": creditos,
                            "semestre": semestre,
                        },
                    )
                    if created:
                        creadas += 1
                    else:
                        actualizadas += 1

                except (ValueError, KeyError) as e:
                    errores.append(f"Fila {fila_num}: error - {e}")

        self.stdout.write(self.style.SUCCESS(f"Importación completada para: {carrera}"))
        self.stdout.write(f"  Materias creadas: {creadas}")
        self.stdout.write(f"  Materias actualizadas: {actualizadas}")
        if errores:
            self.stdout.write(self.style.WARNING(f"  Errores ({len(errores)}):"))
            for err in errores:
                self.stdout.write(self.style.WARNING(f"    - {err}"))
