"""
Management command para sembrar pensum real de Ingeniería en Sistemas
Computacionales (ISC) de UTESA según PDF oficial (Res. 104-22, Enero 2023).
Incluye pre-requisitos y co-requisitos entre materias.
"""

from django.core.management.base import BaseCommand
from pensums.models import Recinto, Carrera, Materia

# Formato: (codigo, nombre, creditos, [pre-requisitos], [co-requisitos])
PENSUM_ISC = {
    "1": [
        ("ESP-181", "Lengua Española I", 4, [], []),
        ("INF-117", "Algoritmos Computacionales", 4, [], []),
        ("ING-105", "Inglés I", 0, [], []),
        ("MAT-115", "Matemáticas Discretas", 4, [], []),
        ("MAT-160", "Precálculo", 4, [], []),
        ("MED-750", "Química Inorgánica I", 3, [], ["MED-755"]),
        ("MED-755", "Laboratorio de Química Inorgánica I", 1, [], ["MED-750"]),
        ("ORI-112", "Orientación Universitaria", 2, [], []),
        ("SOC-182", "Reflexión Filosófica", 3, [], []),
    ],
    "2": [
        ("ESP-189", "Lengua Española II", 4, ["ESP-181"], []),
        ("INF-164", "Programación I", 3, ["INF-117", "MAT-115"], ["INF-165"]),
        ("INF-165", "Laboratorio de Programación I", 1, ["INF-117", "MAT-115"], ["INF-164"]),
        ("INF-204", "Lógica Computacional", 4, [], []),
        ("ING-115", "Inglés II", 0, ["ING-105"], []),
        ("MAT-170", "Cálculo I", 4, ["MAT-160"], []),
        ("MAT-190", "Física I", 4, ["MAT-160"], ["MAT-191"]),
        ("MAT-191", "Laboratorio de Física I", 1, ["MAT-160"], ["MAT-190"]),
    ],
    "3": [
        ("ESP-302", "Redacción Profesional", 3, ["ESP-189"], []),
        ("INF-121", "Análisis de Sistemas", 4, ["INF-164", "INF-165"], []),
        ("INF-167", "Programación II (Orientada a Objeto)", 3, ["INF-164", "INF-165"], ["INF-168"]),
        ("INF-168", "Laboratorio de Programación II", 1, ["INF-164", "INF-165"], ["INF-167"]),
        ("ING-125", "Inglés III", 3, ["ING-115"], []),
        ("MAT-306", "Pensamiento Lógico", 0, ["MAT-160", "SOC-182"], []),
        ("MAT-340", "Cálculo II", 4, ["MAT-170"], []),
        ("MAT-500", "Física II", 4, ["MAT-190", "MAT-191"], ["MAT-501"]),
        ("MAT-501", "Laboratorio de Física II", 1, ["MAT-190", "MAT-191"], ["MAT-500"]),
        ("SOC-114", "Metodología de la Investigación I", 3, [], []),
    ],
    "4": [
        ("IEL-100", "Electricidad Básica", 3, ["MAT-500", "MAT-501"], ["IEL-105"]),
        ("IEL-105", "Taller de Electricidad Básica", 1, ["MAT-500", "MAT-501"], ["IEL-100"]),
        ("INF-171", "Diseño de Sistemas", 4, ["INF-121", "INF-167", "INF-168"], []),
        ("INF-172", "Programación III (Orientada a Objeto)", 3, ["INF-121", "INF-167", "INF-168"], ["INF-173"]),
        ("INF-173", "Laboratorio de Programación III", 1, ["INF-121", "INF-167", "INF-168"], ["INF-172"]),
        ("INF-385", "Base de Datos I", 3, ["INF-121", "INF-167", "INF-168"], ["INF-387"]),
        ("INF-387", "Laboratorio de Base de Datos I", 1, ["INF-121", "INF-167", "INF-168"], ["INF-385"]),
        ("ING-135", "Inglés IV", 4, ["ING-125"], []),
        ("MAT-134", "Fundamentos de Estadística", 2, [], []),
        ("MAT-350", "Cálculo III", 4, ["MAT-340"], []),
        ("SOC-118", "Metodología de la Investigación II", 3, ["SOC-114"], ["MAT-134"]),
        ("SOC-172", "Debates de Historia Dominicana", 3, [], []),
    ],
    "5": [
        ("DIB-520", "Dibujo Técnico", 2, [], []),
        ("IID-420", "Seguridad e Higiene Industrial", 2, [], []),
        ("INF-440", "Arquitectura Computacional", 3, ["INF-204", "IEL-100", "IEL-105"], ["INF-445"]),
        ("INF-445", "Laboratorio de Arquitectura Computacional", 1, ["INF-204", "IEL-100", "IEL-105"], ["INF-440"]),
        ("INF-481", "Base de Datos II", 2, ["INF-171", "INF-385", "INF-387"], ["INF-482"]),
        ("INF-482", "Laboratorio de Base de Datos II", 1, ["INF-171", "INF-385", "INF-387"], ["INF-481"]),
        ("INF-535", "Diseño y Programación de Páginas Web", 3, ["INF-171", "INF-385", "INF-387"], []),
        ("MAT-360", "Cálculo IV", 4, ["MAT-350"], []),
        ("SOC-502", "Ciudadanía y Globalización", 2, [], []),
    ],
    "6": [
        ("INF-184", "Sistemas Operativos", 2, ["INF-440", "INF-445"], ["INF-185"]),
        ("INF-185", "Laboratorio de Sistemas Operativos", 1, ["INF-440", "INF-445"], ["INF-184"]),
        ("INF-217", "Algoritmos y Estructuras de Datos", 2, ["INF-172", "INF-173"], ["INF-218"]),
        ("INF-218", "Laboratorio de Algoritmos y Estructuras de Datos", 1, ["INF-172", "INF-173"], ["INF-217"]),
        ("INF-225", "Proyecto Integrador I", 5, [], []),
        ("INF-331", "Seminario de Informática", 3, [], []),
        ("INF-640", "Minería de Datos", 3, ["INF-481", "INF-482"], []),
        ("ING-168", "Inglés Profesional", 0, ["ING-135"], []),
        ("MAT-135", "Estadística para Ingenieros I", 3, ["MAT-134"], []),
        ("SOC-160", "Ética Profesional", 2, [], []),
    ],
    "7": [
        ("INF-502", "Inteligencia Artificial", 2, ["INF-217", "INF-218"], ["INF-503"]),
        ("INF-503", "Laboratorio de Inteligencia Artificial", 2, ["INF-217", "INF-218"], ["INF-502"]),
        ("INF-700", "Computación Gráfica", 3, ["INF-440", "INF-445", "INF-184", "INF-185"], []),
        ("INF-705", "Métodos Numéricos", 2, ["MAT-360"], ["INF-706"]),
        ("INF-706", "Laboratorio de Métodos Numéricos", 1, ["MAT-360"], ["INF-705"]),
        ("INF-710", "Metodología Ágil", 2, ["INF-167", "INF-168"], []),
        ("MAT-145", "Estadística para Ingenieros II", 3, ["MAT-135"], []),
        ("SIC-766", "Inteligencia Emocional", 2, [], []),
        ("SOC-155", "Medio Ambiente y Sostenibilidad", 3, [], []),
    ],
    "8": [
        ("ECO-525", "Finanzas Personales", 3, ["MAT-360"], []),
        ("IID-725", "Investigación Operativa I", 3, ["INF-225"], []),
        ("INF-241", "Ingeniería de Software I", 3, ["INF-225"], []),
        ("INF-810", "Auditoría de Sistemas Informáticos", 3, ["INF-535", "INF-700"], []),
        ("INF-840", "Programación de Dispositivos Móviles", 3, [], []),
        ("PAS-000", "Pasantía", 1, [], []),
    ],
    "9": [
        ("ADM-910", "Liderazgo y Desempeño", 3, ["IID-725"], []),
        ("IID-830", "Investigación de Operativa II", 2, ["IID-725"], []),
        ("INF-021", "Gestión de Proyecto Informático", 3, ["INF-241"], []),
        ("INF-411", "Redes y Comunicaciones", 3, ["INF-440", "INF-445", "INF-184", "INF-185"], ["INF-412"]),
        ("INF-412", "Laboratorio de Redes y Comunicaciones", 1, ["INF-440", "INF-445", "INF-184", "INF-185"], ["INF-411"]),
        ("INF-450", "Ingeniería de Software II", 3, ["INF-241"], []),
        ("INF-910", "Programación de Videojuegos", 3, ["INF-700"], []),
    ],
    "10": [
        ("ADM-900", "Formación de Emprendedores", 3, [], []),
        ("IID-945", "Ingeniería Económica", 3, ["MAT-360"], []),
        ("INF-344", "Telecomunicación de Datos", 3, ["INF-411", "INF-412"], ["INF-345"]),
        ("INF-345", "Laboratorio de Telecomunicación de Datos", 1, ["INF-411", "INF-412"], ["INF-344"]),
        ("INF-433", "Aseguramiento de Calidad del Software", 3, ["INF-450"], []),
        ("INF-920", "Compiladores", 3, ["INF-502", "INF-503", "INF-184", "INF-185"], []),
    ],
    "11": [
        ("DPG-010", "Anteproyecto de Grado", 6, [], []),
        ("IID-025", "Diseño y Evaluación de Proyectos", 4, ["ADM-900"], []),
        ("INF-025", "Algoritmos Paralelos", 3, ["INF-705", "INF-706"], []),
        ("INF-820", "Seguridad Informática", 3, ["INF-344", "INF-345"], []),
    ],
    "12": [
        ("DPG-020", "Proyecto de Grado", 6, ["DPG-010"], []),
    ],
}

ELECTIVAS = [
    ("CON-118", "Contabilidad I", 3, [], []),
    ("IEL-200", "Circuitos Eléctricos I", 3, ["IEL-100", "IEL-105"], ["IEL-205"]),
    ("IEL-205", "Taller de Circuitos Eléctricos I", 1, ["IEL-100", "IEL-105"], ["IEL-200"]),
    ("INF-022", "Sistema y Tecnología de Información", 3, ["INF-385", "INF-387"], []),
    ("INF-023", "Domótica y Entorno Inteligente", 3, ["INF-344", "INF-345"], []),
    ("INF-024", "Administración de Negocios Electrónicos", 3, ["INF-225"], []),
    ("INF-026", "Robótica", 3, ["INF-344", "INF-345"], []),
    ("INF-027", "Blockchain, Criptomonedas y Metaverso", 3, ["INF-411", "INF-412"], []),
]


class Command(BaseCommand):
    help = "Crea pensum real de Ingeniería en Sistemas Computacionales (ISC) UTESA"

    def _crear_materias(self, carrera, data):
        materias_creadas = {}
        for semestre, subjects in data.items():
            for codigo, nombre, creditos, _, _ in subjects:
                materia, _ = Materia.objects.get_or_create(
                    carrera=carrera,
                    codigo=codigo,
                    defaults={
                        "nombre": nombre,
                        "creditos": creditos,
                        "semestre": semestre,
                    },
                )
                materias_creadas[codigo] = materia
        return materias_creadas

    def _asignar_pre_corequisitos(self, carrera, data, materias_dict):
        for semestre, subjects in data.items():
            for codigo, _, _, prereqs, coreqs in subjects:
                materia = materias_dict[codigo]
                for p_cod in prereqs:
                    if p_cod in materias_dict:
                        materia.prerrequisitos.add(materias_dict[p_cod])
                for c_cod in coreqs:
                    if c_cod in materias_dict:
                        materia.corequisitos.add(materias_dict[c_cod])

    def handle(self, *args, **options):
        carrera, created = Carrera.objects.get_or_create(
            slug="ingenieria-en-sistemas-computacionales",
            defaults={
                "nombre": "Ingeniería en Sistemas Computacionales",
                "codigo": "ISC-01",
                "descripcion": "Pensum actualizado 2023 - Res. 104-22",
            },
        )
        for recinto in Recinto.objects.all():
            recinto.carreras.add(carrera)
        self.stdout.write(f"  Carrera vinculada a {Recinto.objects.filter(carreras=carrera).count()} recintos")
        if created:
            self.stdout.write(self.style.SUCCESS(f"✓ Carrera creada: {carrera.nombre}"))
        else:
            self.stdout.write(f"  Carrera existente: {carrera.nombre} - limpiando materias anteriores...")
            carrera.materias.all().delete()

        pensum_completo = {**PENSUM_ISC}
        pensum_completo["E"] = ELECTIVAS

        materias = self._crear_materias(carrera, pensum_completo)
        self._asignar_pre_corequisitos(carrera, PENSUM_ISC, materias)
        self._asignar_pre_corequisitos(carrera, {"E": ELECTIVAS}, materias)

        total_materias = carrera.materias.count()
        total_creditos = carrera.total_creditos()
        total_semestres = len(PENSUM_ISC)

        self.stdout.write(self.style.SUCCESS(
            f"✓ Pensum ISC cargado: {total_materias} materias en {total_semestres} cuatrimestres"
        ))
        self.stdout.write(f"  Total créditos: {total_creditos}")
        self.stdout.write(f"  Total electivas: {len(ELECTIVAS)}")
        self.stdout.write(f"  Relaciones pre-requisito: {Materia.prerrequisitos.through.objects.count()}")
        self.stdout.write(f"  Relaciones co-requisito: {Materia.corequisitos.through.objects.count()}")

        self.stdout.write("\n" + "=" * 60)
        self.stdout.write("Materias con pre-requisitos:")
        self.stdout.write("=" * 60)
        for m in Materia.objects.filter(carrera=carrera, semestre__gte="2").exclude(prerrequisitos=None).order_by("semestre", "codigo"):
            pre = ", ".join(p.codigo for p in m.prerrequisitos.all())
            co = ", ".join(c.codigo for c in m.corequisitos.all())
            parts = [f"Pre: {pre}"]
            if co:
                parts.append(f"Co-Req: {co}")
            self.stdout.write(f"  [{m.semestre}°] {m.codigo} {m.nombre} ({'; '.join(parts)})")
