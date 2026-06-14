"""
Procesa todos los PDFs de la carpeta pensum pdf/ y extrae las materias
a archivos CSV y/o las importa directamente a la base de datos.

Uso:
    python manage.py importar_pdfs                    # solo generar CSVs
    python manage.py importar_pdfs --importar          # generar CSVs e importar
    python manage.py importar_pdfs --pdf "Derecho"     # solo un PDF específico
"""

import csv
import os
import re
import subprocess
import sys
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from pensums.models import Carrera

PDF_DIR = Path("/home/jsosa/utesa-pensums/pensum pdf")
CSV_DIR = Path("/home/jsosa/utesa-pensums/pensum csv")

SEMESTRE_MAP = {
    "PRIMER": "1", "SEGUNDO": "2", "TERCER": "3", "CUARTO": "4",
    "QUINTO": "5", "SEXTO": "6", "SÉPTIMO": "7", "SEPTIMO": "7",
    "OCTAVO": "8", "NOVENO": "9", "DÉCIMO": "10", "DECIMO": "10",
    "UNDÉCIMO": "11", "UNDECIMO": "11", "DUODÉCIMO": "12", "DUODECIMO": "12",
}

SKIP_WORDS = {"CLAVE", "NOMBRE", "ASIGNATURA", "HT", "HP", "TH", "CRED",
              "PRERREQUISITOS", "TOTAL", "SUB", "ELECTIVA", "ELECTIVAS",
              "PASANTÍA", "PASANTIA"}

UNIQUE_PDFS = {}

# Mapeo explícito de nombre de PDF → slug de carrera
PDF_A_SLUG = {
    "Administración de Empresas Turísticas y Hoteleras": "administracion-de-empresas-turisticas-y-hoteleras",
    "Educación": "educacion",
    "Fármaco-Bioquímica": "farmaco-bioquimica",
    "Medicina": "medicina",
    "Nutrición Humana y Dietética": "nutricion-humana-y-dietetica",
    "Arquitectura": "arquitectura",
    "Bioanalisis": "bioanalisis",
    "Derecho": "derecho",
    "Ingenieria Civil": "ingenieria-civil",
    "Ingenieria Electronica": "ingenieria-electronica",
    "Ingenieria Industrial": "ingenieria-industrial",
    "Ingenieria Mecanica": "ingenieria-mecanica",
    "Ingenieria en Sistemas Computacionales": "ingenieria-en-sistemas-computacionales",
    "Lenguas Extranjeras": "lenguas-extranjeras",
    "Mercadeo": "mercadeo",
    "Odontologia": "odontologia",
    "Psicologia": "psicologia",
    "Veterinaria y Zootecnia": "veterinaria-y-zootecnia",
    "Optometría": "optometria",
    "Optometria": "optometria",
    "Administración de Empresas": "administracion-de-empresas",
    "Administracion de Empresas": "administracion-de-empresas",
    "Enfermería": "enfermeria",
    "Ing. Electrica": "ingenieria-electrica",
    "Ingeniería Eléctrica": "ingenieria-electrica",
}


def find_unique_pdfs():
    """Retorna PDFs únicos, prefiriendo el archivo sin (1)."""
    files = sorted(PDF_DIR.glob("*.pdf"))
    seen = {}
    for f in files:
        base = re.sub(r'\s*\(1\)$', '', f.stem)
        if base not in seen:
            seen[base] = f
            continue
        # Si el actual no tiene (1) y el guardado sí, reemplazar
        if "(1)" not in f.stem and "(1)" in seen[base].stem:
            seen[base] = f
    return list(seen.values())


def pdf_to_text(pdf_path):
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise CommandError(f"Error al procesar {pdf_path.name}: {result.stderr}")
    return result.stdout


def guess_carrera_slug(pdf_name):
    """Busca el slug en el mapeo, o intenta adivinarlo."""
    for key, slug in PDF_A_SLUG.items():
        if key.lower() in pdf_name.lower():
            return slug
    name = pdf_name.replace("Pensum", "").replace("Pénsum", "").replace("Carrera de", "")
    name = name.replace("Pensum -", "").replace("Pénsum -", "").replace("Pensúm -", "")
    name = name.replace("(1)", "").replace("UTESA", "").replace("2023", "")
    name = name.replace("2024", "").replace("2021", "").replace("2019", "")
    name = name.replace("2013", "").strip()
    name = re.sub(r'[\s_]+', ' ', name).strip()
    name = re.sub(r'[,-]', '', name)
    return slugify(name)


def guess_carrera_nombre(pdf_name):
    """Intenta adivinar el nombre real de la carrera."""
    pdf_name = re.sub(r'Pensum|Pénsum|Pensúm|Carrera de|\d{4}|\(1\)|UTESA', '', pdf_name)
    pdf_name = re.sub(r'[\s_]+', ' ', pdf_name).strip()
    pdf_name = re.sub(r'[,-]$', '', pdf_name).strip()
    map_override = {
        "Bioanalisis": "Bioanálisis",
        "Ingenieria Civil": "Ingeniería Civil",
        "Ingenieria Electronica": "Ingeniería Electrónica",
        "Ingenieria Industrial": "Ingeniería Industrial",
        "Ingenieria Mecanica": "Ingeniería Mecánica",
        "Ingenieria en Sistemas Computacionales": "Ingeniería en Sistemas Computacionales",
        "Fármaco-Bioquímica": "Fármaco-Bioquímica",
        "Lenguas Extranjeras": "Lenguas Extranjeras",
        "Administración de Empresas": "Administración de Empresas",
        "Administración de Empresas Turísticas y Hoteleras": "Administración de Empresas Turísticas y Hoteleras",
        "Mercadeo": "Mercadeo",
        "Derecho": "Derecho",
        "Psicologia": "Psicología",
        "Odontologia": "Odontología",
        "Veterinaria y Zootecnia": "Veterinaria y Zootecnia",
        "Optometría": "Optometría",
        "Nutrición Humana y Dietética": "Nutrición Humana y Dietética",
        "Educación": "Educación",
        "Enfermería": "Enfermería",
        "Medicina": "Medicina",
        "Arquitectura": "Arquitectura",
        "Ing. Electrica": "Ingeniería Eléctrica",
    }
    for key, val in map_override.items():
        if key.lower() in pdf_name.lower():
            return val
    return pdf_name.strip()


def parse_standard(text):
    """Parsea formato estándar 2023 con -layout."""
    materias = []
    semestre_actual = None

    for line in text.split("\n"):
        line = line.strip()

        # Detectar encabezado de semestre
        sem_match = re.match(r"(PRIMER|SEGUNDO|TERCER|CUARTO|QUINTO|SEXTO|SÉPTIMO|SEPTIMO|OCTAVO|NOVENO|DÉCIMO|DECIMO|UNDÉCIMO|UNDECIMO|DUODÉCIMO|DUODECIMO)\s+CUATRIMESTRE", line, re.IGNORECASE)
        if sem_match:
            semestre_actual = SEMESTRE_MAP.get(sem_match.group(1).upper())
            continue

        if not semestre_actual or not line:
            continue

        # Saltar líneas que no sean materias
        if any(word in line for word in SKIP_WORDS):
            continue
        if re.match(r'^\d+$', line):
            continue
        if line.startswith("SUB TOTAL") or line.startswith("TOTAL"):
            continue

        # Buscar código de materia: PAT-123 o PAT -123
        m = re.match(r'([A-ZÑÁÉÍÓÚ]{2,4}\s*-?\s*\d{3,4})\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
        if m:
            codigo = m.group(1).replace(" ", "").replace("-", "-")
            nombre = m.group(2).strip()
            creditos = int(m.group(6))
            pre_reqs_raw = line[m.end():].strip()
            pre_reqs = re.findall(r'[A-ZÑÁÉÍÓÚ]{2,4}\s*-?\s*\d{3,4}', pre_reqs_raw)
            pre_reqs = [p.replace(" ", "") for p in pre_reqs]
            materias.append({
                "codigo": codigo,
                "nombre": nombre,
                "creditos": creditos,
                "semestre": semestre_actual,
                "prerrequisitos": pre_reqs,
            })
    return materias


def parse_optometria(text):
    """Parsea formato Optometría 2019 con Clave/Asignaturas/CR/Prerrequisitos."""
    materias = []
    semestre_actual = None

    for line in text.split("\n"):
        line = line.strip()
        sem_match = re.match(r"(PRIMER|SEGUNDO|TERCER|CUARTO|QUINTO|SEXTO|SÉPTIMO|SEPTIMO|OCTAVO|NOVENO|DÉCIMO|DECIMO)\s+CUATRIMESTRE", line, re.IGNORECASE)
        if sem_match:
            semestre_actual = SEMESTRE_MAP.get(sem_match.group(1).upper())
            continue
        if not semestre_actual or not line:
            continue
        if any(word in line for word in SKIP_WORDS):
            continue
        if line.startswith("SUB TOTAL") or line.startswith("TOTAL"):
            continue

        m = re.match(r'([A-ZÑÁÉÍÓÚ]{2,4}-\d{3,4})\s+(.+?)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)', line)
        if m:
            codigo = m.group(1)
            nombre = m.group(2).strip()
            creditos = int(m.group(6))
            pre_reqs_raw = line[m.end():].strip()
            pre_reqs = re.findall(r'[A-ZÑÁÉÍÓÚ]{2,4}\s*-?\s*\d{3,4}', pre_reqs_raw)
            pre_reqs = [p.replace(" ", "") for p in pre_reqs]
            materias.append({
                "codigo": codigo,
                "nombre": nombre,
                "creditos": creditos,
                "semestre": semestre_actual,
                "prerrequisitos": pre_reqs,
            })
    return materias


def parse_viejo(text):
    """Parsea formato viejo (2013) sin créditos visibles - usa defaults."""
    materias = []
    semestre_actual = None

    for line in text.split("\n"):
        line = line.strip()
        sem_match = re.match(r"(PRIMER|SEGUNDO|TERCER|CUARTO|QUINTO|SEXTO|SÉPTIMO|SEPTIMO|OCTAVO|NOVENO|DÉCIMO|DECIMO)\s+CUATRIMESTRE", line, re.IGNORECASE)
        if sem_match:
            semestre_actual = SEMESTRE_MAP.get(sem_match.group(1).upper())
            continue
        if not semestre_actual or not line:
            continue
        if any(word in line for word in SKIP_WORDS):
            continue

        m = re.match(r'([A-ZÑÁÉÍÓÚ]{2,4}-\d{3,4})\s+(.+)', line)
        if m:
            materias.append({
                "codigo": m.group(1),
                "nombre": m.group(2).strip(),
                "creditos": 0,
                "semestre": semestre_actual,
                "prerrequisitos": [],
            })
    return materias


def detect_format(text):
    lines = text.strip().split("\n")
    # Check if it has layout table columns
    has_layout = any("HT" in line and "HP" in line and "TH" in line and "CRED" in line for line in lines[:50])
    has_viejo = any(re.match(r'[A-ZÑÁÉÍÓÚ]{2,4}-\d{3,4}\s+.+', line) for line in lines[:50]) and not has_layout
    # Check optometría (CR instead of CRED, Prerrequisitos)
    has_opt = any("Prerrequisitos" in line or "Correquisito" in line for line in lines[:20])

    if has_opt:
        return "optometria"
    if has_layout:
        return "standard"
    if has_viejo:
        return "viejo"
    return "unknown"


def generar_csv(materias, pdf_stem):
    CSV_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = CSV_DIR / f"{pdf_stem}.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["codigo", "nombre", "creditos", "semestre", "prerrequisitos"])
        for m in materias:
            writer.writerow([m["codigo"], m["nombre"], m["creditos"], m["semestre"], ";".join(m["prerrequisitos"])])
    return csv_path


def importar_a_db(materias, carrera_slug, pdf_stem):
    try:
        carrera = Carrera.objects.get(slug=carrera_slug)
    except Carrera.DoesNotExist:
        print(f"    ⚠ No existe carrera con slug '{carrera_slug}' — se omite importación")
        return 0

    creadas = 0
    for m in materias:
        _, created = carrera.materias.update_or_create(
            codigo=m["codigo"],
            defaults={
                "nombre": m["nombre"],
                "creditos": m["creditos"],
                "semestre": m["semestre"],
            },
        )
        if created:
            creadas += 1
    return creadas


class Command(BaseCommand):
    help = "Procesa PDFs de pensums y extrae materias a CSV/DB"

    def add_arguments(self, parser):
        parser.add_argument("--importar", action="store_true", help="Importar a la base de datos")
        parser.add_argument("--pdf", type=str, help="Procesar solo un PDF (busca por substring en el nombre)")

    def handle(self, *args, **options):
        pdfs = find_unique_pdfs()
        if options["pdf"]:
            pdfs = [p for p in pdfs if options["pdf"].lower() in p.stem.lower()]

        if not pdfs:
            self.stdout.write(self.style.WARNING("No se encontraron PDFs"))
            return

        self.stdout.write(f"Procesando {len(pdfs)} PDFs...\n")

        total_creadas = 0
        for pdf_path in pdfs:
            pdf_stem = pdf_path.stem
            self.stdout.write(f"[{pdf_stem}]")

            try:
                text = pdf_to_text(pdf_path)
            except (subprocess.TimeoutExpired, CommandError) as e:
                self.stdout.write(self.style.WARNING(f"    ⚠ {e}"))
                continue
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    ⚠ Error extrayendo texto: {e}"))
                continue

            if len(text.strip()) < 20:
                self.stdout.write(self.style.WARNING("    ⚠ PDF sin texto (escaneado/imagen)"))
                continue

            fmt = detect_format(text)
            self.stdout.write(f"    Formato: {fmt}")

            if fmt == "standard":
                materias = parse_standard(text)
            elif fmt == "optometria":
                materias = parse_optometria(text)
            elif fmt == "viejo":
                materias = parse_viejo(text)
            else:
                self.stdout.write(self.style.WARNING("    ⚠ Formato no reconocido"))
                continue

            if not materias:
                self.stdout.write(self.style.WARNING("    ⚠ No se extrajeron materias"))
                continue

            csv_path = generar_csv(materias, pdf_stem)
            self.stdout.write(f"    ✓ {len(materias)} materias → {csv_path.name}")

            if options["importar"]:
                carrera_slug = guess_carrera_slug(pdf_stem)
                creadas = importar_a_db(materias, carrera_slug, pdf_stem)
                self.stdout.write(f"    ✓ {creadas} nuevas en DB (slug: {carrera_slug})")
                total_creadas += creadas

        if options["importar"]:
            self.stdout.write(self.style.SUCCESS(f"\n✓ Total materias importadas: {total_creadas}"))
        self.stdout.write(self.style.SUCCESS("\n✓ Procesamiento completado"))
